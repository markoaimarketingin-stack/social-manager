import requests
import sqlite3
import sys
import time
from datetime import datetime

API_URL = "http://127.0.0.1:8088"
DB_PATH = "social_manager.db"

def run_tests():
    print("\n" + "="*80)
    print("STARTING COMPLIANCE & CHAT AGENT INTEGRATION TESTS")
    print("="*80)

    # 1. Register or Login Test User
    email = "compliance_tester@example.com"
    password = "password123"
    name = "Compliance Tester"
    
    print("\n[1] Authenticating Test User...")
    token = None
    user_id = None
    
    # Try registering
    resp = requests.post(f"{API_URL}/api/users/register", json={
        "email": email,
        "password": password,
        "name": name
    })
    
    if resp.status_code == 200:
        data = resp.json()
        token = data["access_token"]
        user_id = data["user"]["id"]
        print(f"    ✓ Registered new test user (ID: {user_id})")
    elif resp.status_code == 400 and "already registered" in resp.text:
        # User exists, login
        resp = requests.post(f"{API_URL}/api/users/login", json={
            "email": email,
            "password": password
        })
        if resp.status_code == 200:
            data = resp.json()
            token = data["access_token"]
            user_id = data["user"]["id"]
            print(f"    ✓ Logged in existing test user (ID: {user_id})")
        else:
            print(f"    ✗ Login failed: {resp.status_code} - {resp.text}")
            return False
    else:
        print(f"    ✗ Registration failed: {resp.status_code} - {resp.text}")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Insert mock platform connections directly to SQLite
    print("\n[2] Seeding platform connections in DB...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if connections table exists and insert connections
        cursor.execute("SELECT id FROM sm_users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            print("    ✗ User not found in DB even after login!")
            return False
            
        platforms = ["linkedin", "instagram", "facebook"]
        for plat in platforms:
            cursor.execute(
                "SELECT id FROM social_connections WHERE user_id = ? AND platform = ?", 
                (user_id, plat)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO social_connections (user_id, platform, access_token, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (user_id, plat, "mock_token_" + plat, datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
                )
                print(f"    ✓ Created mock social connection for: {plat}")
            else:
                print(f"    ✓ Connection already exists for: {plat}")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"    ✗ SQLite connection seeding failed: {e}")
        return False

    all_passed = True

    # 3. Test API /api/publishing/schedule
    print("\n[3] Testing /api/publishing/schedule compliance pipeline...")

    # Case A: Fails policy (Banned word "guarantee")
    print("  [Case A] Posting content with banned word 'guarantee'...")
    resp = requests.post(
        f"{API_URL}/api/publishing/schedule",
        json={
            "platforms": ["linkedin"],
            "content": "We offer a 100% guarantee on all sales!",
            "scheduled_at": None
        },
        headers=headers
    )
    if resp.status_code == 400 and "Compliance Check Failed" in resp.json().get("detail", ""):
        print("    ✓ Success: Blocked successfully. Error: ", resp.json()["detail"])
    else:
        print(f"    ✗ Failed: Expected HTTP 400 compliance block, got status {resp.status_code}: {resp.text}")
        all_passed = False

    # Case B: Warning/Pending (Short content under 20 chars)
    print("  [Case B] Posting short content (warning check)...")
    resp = requests.post(
        f"{API_URL}/api/publishing/schedule",
        json={
            "platforms": ["linkedin"],
            "content": "Short text",
            "scheduled_at": None
        },
        headers=headers
    )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "warning_pending_approval":
            print(f"    ✓ Success: Flagged warnings and routed to approvals. Message: {data.get('message')}")
        else:
            print(f"    ✗ Failed: Expected status warning_pending_approval, got: {data}")
            all_passed = False
    else:
        print(f"    ✗ Failed: Expected HTTP 200, got status {resp.status_code}: {resp.text}")
        all_passed = False

    # Case C: All checks passed (Auto-approved)
    print("  [Case C] Posting clean content...")
    resp = requests.post(
        f"{API_URL}/api/publishing/schedule",
        json={
            "platforms": ["linkedin"],
            "content": "This is a clean post about social media automation platforms that has no banned words or short warnings.",
            "scheduled_at": None
        },
        headers=headers
    )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "success":
            print("    ✓ Success: Post auto-approved and queued.")
        else:
            print(f"    ✗ Failed: Expected status 'success', got: {data}")
            all_passed = False
    else:
        print(f"    ✗ Failed: Expected HTTP 200, got status {resp.status_code}: {resp.text}")
        all_passed = False


    # 4. Test API /api/chat/interact (agent mode)
    print("\n[4] Testing /api/chat/interact agent mode routing...")

    # Case A: Fails policy (Banned word "risk-free")
    print("  [Case A] Asking agent to post banned word...")
    resp = requests.post(
        f"{API_URL}/api/chat/interact",
        json={
            "message": "Promise a risk-free investment return.",
            "mode": "agent",
            "platforms": ["instagram"]
        },
        headers=headers
    )
    if resp.status_code == 200:
        data = resp.json()
        if "Blocked by compliance check" in data.get("response", ""):
            print(f"    ✓ Success: Agent blocked due to policy violations. Response: {data['response']}")
        else:
            print(f"    ✗ Failed: Response did not indicate block. Got: {data}")
            all_passed = False
    else:
        print(f"    ✗ Failed: Expected HTTP 200, got status {resp.status_code}: {resp.text}")
        all_passed = False

    # Case B: Warning/Pending pricing risk keyword
    print("  [Case B] Asking agent to write about product launches and pricing (requires review)...")
    resp = requests.post(
        f"{API_URL}/api/chat/interact",
        json={
            "message": "Launch our new social media manager product at the cost of 50 dollars.",
            "mode": "agent",
            "platforms": ["instagram"]
        },
        headers=headers
    )
    if resp.status_code == 200:
        data = resp.json()
        if "Sent to approval queue" in data.get("response", ""):
            print(f"    ✓ Success: Draft enqueued for review. Response: {data['response']}")
        else:
            print(f"    ✗ Failed: Response did not indicate queued status. Got: {data}")
            all_passed = False
    else:
        print(f"    ✗ Failed: Expected HTTP 200, got status {resp.status_code}: {resp.text}")
        all_passed = False

    # Case C: All checks passed (Auto-approved educational content)
    print("  [Case C] Asking agent to draft clean educational post...")
    resp = requests.post(
        f"{API_URL}/api/chat/interact",
        json={
            "message": "Explain how color psychology influences social media click rates.",
            "mode": "agent",
            "platforms": ["instagram"]
        },
        headers=headers
    )
    if resp.status_code == 200:
        data = resp.json()
        if "Passed policy and queued for publishing" in data.get("response", ""):
            print(f"    ✓ Success: Auto-approved and queued. Response: {data['response']}")
        else:
            print(f"    ✗ Failed: Response did not indicate successful queueing. Got: {data}")
            all_passed = False
    else:
        print(f"    ✗ Failed: Expected HTTP 200, got status {resp.status_code}: {resp.text}")
        all_passed = False


    # 5. Check DB side-effects (audit logs and post tables)
    print("\n[5] Verifying DB audit trail and states...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verify strategy logs
        cursor.execute("SELECT event, details FROM social_strategy_logs ORDER BY id DESC LIMIT 5")
        logs = cursor.fetchall()
        print("    Recent strategy logs:")
        for log in logs:
            print(f"      - [{log[0]}] {log[1][:100]}...")
            
        has_compliance_logs = any("compliance" in log[0] or "agent" in log[0] for log in logs)
        if has_compliance_logs:
            print("    ✓ Success: Found compliance/agent entries in social_strategy_logs")
        else:
            print("    ✗ Failed: No compliance/agent entries found in social_strategy_logs")
            all_passed = False
            
        conn.close()
    except Exception as e:
        print(f"    ✗ Failed to read DB tables: {e}")
        all_passed = False

    print("\n" + "="*80)
    if all_passed:
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("="*80 + "\n")
        return True
    else:
        print("SOME TESTS FAILED. CHECK DETAILS ABOVE.")
        print("="*80 + "\n")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
