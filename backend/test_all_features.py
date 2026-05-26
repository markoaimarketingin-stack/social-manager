# -*- coding: utf-8 -*-
"""
Social Manager - Full Backend Test Script (Windows-safe)
Run:  python test_all_features.py
"""

import httpx
import json
import sys
import asyncio
import os
from datetime import datetime

# Force utf-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://localhost:8088"
results = {"passed": 0, "failed": 0, "warnings": 0}
TOKEN = None
USER_ID = None


def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}\n")

def check(label, response, expected_status=200):
    status = response.status_code
    ok = status == expected_status
    icon = "[PASS]" if ok else "[FAIL]"
    print(f"  {icon} [{status}] {label}")
    if ok:
        results["passed"] += 1
    else:
        results["failed"] += 1
        try:
            print(f"       Response: {response.text[:300]}")
        except Exception:
            pass
    return ok

def warn(label, msg):
    print(f"  [WARN] {label}: {msg}")
    results["warnings"] += 1


# 1. HEALTH
def test_health():
    section("1. Health & System Status")
    r = httpx.get(f"{BASE}/health", headers={"Accept": "application/json"})
    check("GET /health", r)
    r = httpx.get(f"{BASE}/api/system/status")
    check("GET /api/system/status", r)
    r = httpx.get(f"{BASE}/api/v1/health")
    check("GET /api/v1/health", r)
    r = httpx.get(f"{BASE}/api/v1/system/status")
    check("GET /api/v1/system/status", r)
    r = httpx.get(f"{BASE}/")
    check("GET / (root)", r)
    r = httpx.get(f"{BASE}/docs")
    check("GET /docs (Swagger UI)", r)


# 2. AUTH
def test_auth():
    global TOKEN, USER_ID
    section("2. User Authentication")
    email = f"test_{int(datetime.now().timestamp())}@example.com"
    r = httpx.post(f"{BASE}/api/users/register", json={
        "email": email, "password": "Test1234!", "name": "Test User"
    })
    if check("POST /api/users/register", r):
        data = r.json()
        TOKEN = data["access_token"]
        USER_ID = data["user"]["id"]
        print(f"       Token: {TOKEN[:30]}...")
        print(f"       User ID: {USER_ID}")

    if TOKEN:
        r = httpx.get(f"{BASE}/api/users/me", headers={"Authorization": f"Bearer {TOKEN}"})
        check("GET /api/users/me (authenticated)", r)


# 3. V1 API
def test_v1_api():
    section("3. V1 API - Workspace Flow")
    r = httpx.post(f"{BASE}/api/v1/workspaces", json={
        "name": "Test Brand Workspace",
        "owner": {"full_name": "Test User", "email": "test@example.com"}
    })
    ws_id = None
    if check("POST /api/v1/workspaces (create)", r, 201):
        ws_id = r.json()["id"]
        print(f"       Workspace ID: {ws_id}")
    if not ws_id:
        ws_id = "test-ws-1"

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}")
    check("GET /api/v1/workspaces/{id}", r)

    # Brand Profile
    section("3a. Brand Profile")
    r = httpx.put(f"{BASE}/api/v1/workspaces/{ws_id}/brand-profile", json={
        "brand_name": "Acme Corp", "industry": "SaaS",
        "description": "AI-powered social media tools",
        "website_url": "https://acme.com",
        "voice_summary": "Professional, witty, data-driven",
        "mission": "Democratize social media intelligence"
    })
    check("PUT brand-profile (create)", r)
    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/brand-profile")
    check("GET brand-profile", r)

    # Audience Segments
    section("3b. Audience Segments")
    r = httpx.post(f"{BASE}/api/v1/workspaces/{ws_id}/audience-segments", json={
        "name": "Startup Founders", "description": "Early-stage founders",
        "age_range": "25-40", "interests": ["AI", "SaaS", "Growth"],
        "primary_platform": "LinkedIn", "messaging_angle": "Productivity hacking"
    })
    seg_id = None
    if check("POST audience-segments (create)", r, 201):
        seg_id = r.json()["id"]
    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/audience-segments")
    check("GET audience-segments (list)", r)
    if seg_id:
        r = httpx.put(f"{BASE}/api/v1/workspaces/{ws_id}/audience-segments/{seg_id}", json={
            "name": "Startup Founders (updated)", "description": "Series A founders",
            "age_range": "28-45", "interests": ["AI", "SaaS"],
            "primary_platform": "LinkedIn", "messaging_angle": "Team building"
        })
        check("PUT audience-segments/{id} (update)", r)

    # Strategy
    section("3c. Strategy Generation")
    r = httpx.post(f"{BASE}/api/v1/workspaces/{ws_id}/strategy-runs", json={
        "goal": "Build thought leadership in AI SaaS"
    })
    strategy_id = None
    if check("POST strategy-runs (generate)", r, 201):
        run = r.json()
        strategy_id = run["output_payload"].get("brand_strategy_id")
        print(f"       Strategy ID: {strategy_id}")

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/strategies")
    if check("GET strategies (list)", r):
        print(f"       Count: {len(r.json())}")

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/strategies/latest")
    if check("GET strategies/latest", r):
        s = r.json()
        print(f"       Title: {s.get('title','N/A')}")
        print(f"       Platform plans: {len(s.get('platform_plans',[]))}")
        print(f"       Content pillars: {len(s.get('content_pillars',[]))}")

    if strategy_id:
        r = httpx.patch(f"{BASE}/api/v1/strategies/{strategy_id}/review", json={
            "status": "approved", "review_notes": "Approved for planning."
        })
        check("PATCH strategies/{id}/review (approve)", r)

    # Content Plan
    section("3d. Content Plan")
    r = httpx.post(f"{BASE}/api/v1/workspaces/{ws_id}/content-plan-runs", json={
        "planning_horizon_label": "Next 2 weeks"
    })
    if check("POST content-plan-runs (generate)", r, 201):
        pr = r.json()
        print(f"       Plan ID: {pr['output_payload'].get('content_plan_id')}")
        print(f"       Posts: {pr['output_payload'].get('planned_post_count')}")

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/content-plans")
    check("GET content-plans (list)", r)

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/content-plans/latest")
    pp_id = None
    if check("GET content-plans/latest", r):
        plan = r.json()
        posts = plan.get("planned_posts", [])
        print(f"       Posts in plan: {len(posts)}")
        if posts:
            pp_id = posts[0]["id"]
            for p in posts[:3]:
                print(f"         > [{p['platform']}] {p['title']} ({p['status']})")

    if pp_id:
        r = httpx.put(f"{BASE}/api/v1/planned-posts/{pp_id}", json={
            "status": "approved", "title": "Updated post", "hook": "Did you know...",
            "angle": "Data-backed", "call_to_action": "Follow for more",
            "platform": "LinkedIn", "format": "Carousel",
            "scheduled_for": "2026-06-01", "notes": "Test approved"
        })
        check("PUT planned-posts/{id} (update)", r)

    # Drafts
    section("3e. Draft Generation")
    r = httpx.post(f"{BASE}/api/v1/workspaces/{ws_id}/draft-runs", json={})
    if check("POST draft-runs (generate)", r, 201):
        dr = r.json()
        print(f"       Generated: {dr['output_payload'].get('generated_count')} drafts")

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/drafts")
    draft_id = None
    if check("GET drafts (list)", r):
        drafts = r.json()
        print(f"       Total: {len(drafts)}")
        if drafts:
            draft_id = drafts[0]["id"]

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/drafts/review-queue")
    if check("GET drafts/review-queue", r):
        print(f"       In review: {len(r.json())}")

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/drafts/publishing-queue")
    if check("GET drafts/publishing-queue", r):
        print(f"       Publish-ready: {len(r.json())}")

    # Draft review flow
    section("3f. Draft Review -> Publish")
    if draft_id:
        r = httpx.put(f"{BASE}/api/v1/drafts/{draft_id}", json={
            "title": "Polished Draft", "caption": "Your AI strategy starts here.",
            "creative_brief": "Dark gradients with neon accent",
            "call_to_action": "Save this for later",
            "hashtags": ["#AI", "#SaaS"], "review_status": "approved",
            "reviewer_notes": "Looks great!"
        })
        check("PUT drafts/{id} (approve)", r)

        r = httpx.post(f"{BASE}/api/v1/drafts/{draft_id}/publish-ready", json={
            "scheduled_publish_at": "2026-06-01T10:00:00Z"
        })
        check("POST drafts/{id}/publish-ready", r)

        r = httpx.post(f"{BASE}/api/v1/drafts/{draft_id}/publish", json={})
        if check("POST drafts/{id}/publish", r):
            pub = r.json()
            receipt = pub.get("mock_publishing_receipt", {})
            print(f"       Receipt: {receipt.get('receipt_id', 'N/A')}")

    # Workflow runs & Activity
    section("3g. Workflow Runs & Activity")
    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/workflow-runs")
    if check("GET workflow-runs", r):
        runs = r.json()
        print(f"       Runs: {len(runs)}")
        for run in runs[:3]:
            print(f"         > [{run['workflow_type']}] {run['status']}")

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/activity")
    if check("GET activity", r):
        events = r.json()
        print(f"       Events: {len(events)}")
        for e in events[:5]:
            print(f"         > [{e['event_type']}] {e['summary'][:60]}")

    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/activity/summary")
    if check("GET activity/summary", r):
        s = r.json()
        print(f"       Total: {s['total_events']}, Approvals: {s['approvals']}")

    # Knowledge Base
    section("3h. Knowledge Base & Training")
    r = httpx.post(f"{BASE}/api/v1/workspaces/{ws_id}/knowledge-base/documents", json={
        "file_name": "brand_guidelines.pdf", "category": "brand_voice",
        "mime_type": "application/pdf", "size_bytes": 524288
    })
    doc_id = None
    if check("POST knowledge-base/documents", r, 201):
        doc_id = r.json()["id"]
    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/knowledge-base/documents")
    check("GET knowledge-base/documents", r)

    if doc_id:
        r = httpx.post(f"{BASE}/api/v1/workspaces/{ws_id}/training-jobs", json={
            "document_ids": [doc_id], "category": "brand_voice"
        })
        check("POST training-jobs", r, 201)
    r = httpx.get(f"{BASE}/api/v1/workspaces/{ws_id}/training-jobs")
    check("GET training-jobs", r)

    # Assistant
    section("3i. Assistant Commands")
    r = httpx.post(f"{BASE}/api/v1/workspaces/{ws_id}/assistant/commands", json={
        "prompt": "Best time to post on LinkedIn?",
        "route_context": "strategy", "mode": "ask"
    })
    check("POST assistant/commands", r)

    # Cleanup
    if seg_id:
        r = httpx.delete(f"{BASE}/api/v1/workspaces/{ws_id}/audience-segments/{seg_id}")
        check("DELETE audience-segments/{id}", r, 204)


# 4. OLD ENDPOINTS
def test_old_endpoints():
    section("4. Legacy Backend Endpoints")
    if TOKEN:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        r = httpx.get(f"{BASE}/api/strategy/current", headers=headers)
        check("GET /api/strategy/current", r)
        r = httpx.get(f"{BASE}/api/publishing/queue", headers=headers)
        check("GET /api/publishing/queue", r)

    r = httpx.get(f"{BASE}/api/knowledge_base/documents")
    check("GET /api/knowledge_base/documents", r)
    r = httpx.get(f"{BASE}/api/knowledge_base/search?query=brand")
    check("GET /api/knowledge_base/search?query=brand", r)
    r = httpx.get(f"{BASE}/api/knowledge_base/context/llm")
    check("GET /api/knowledge_base/context/llm", r)
    r = httpx.get(f"{BASE}/api/inbox")
    check("GET /api/inbox", r)
    r = httpx.post(f"{BASE}/api/policy/check", json={"content": "Buy our product now!"})
    check("POST /api/policy/check", r)
    r = httpx.get(f"{BASE}/api/metrics/post/test-123")
    check("GET /api/metrics/post/{id}", r)
    r = httpx.get(f"{BASE}/api/metrics/platform/instagram?hours=24")
    check("GET /api/metrics/platform/{platform}", r)


# 5. PLATFORM ADAPTERS
async def test_platform_adapters():
    section("5. Platform Adapter Tests (Direct)")
    sys.path.insert(0, os.path.dirname(__file__))
    from social_manager.platforms.linkedin import LinkedInAdapter
    from social_manager.platforms.facebook import FacebookAdapter
    from social_manager.platforms.instagram import InstagramAdapter
    from social_manager.config import settings

    print("  Configured credentials:")
    creds = {
        "LinkedIn client_id": settings.linkedin_client_id,
        "LinkedIn access_token": settings.linkedin_access_token,
        "Facebook app_id": settings.facebook_app_id,
        "Facebook access_token": settings.facebook_access_token,
        "Facebook page_id": settings.facebook_page_id,
        "Instagram token": settings.instagram_access_token,
        "Instagram account": settings.instagram_business_account_id,
    }
    for k, v in creds.items():
        print(f"    {k}: {'SET' if v else 'NOT SET'}")
    print()

    # LinkedIn
    li = LinkedInAdapter(
        api_key=settings.linkedin_client_id or "",
        access_token=settings.linkedin_access_token or "",
        sandbox=not settings.linkedin_access_token,
    )
    print(f"  LinkedIn mode: {'SANDBOX' if li.sandbox else 'LIVE'}")
    prepared = await li.prepare_post("Testing Social Manager backend! #AI #SaaS", [])
    print(f"  [PASS] LinkedIn prepare_post OK")
    results["passed"] += 1
    try:
        result = await li.publish(prepared)
        print(f"  [PASS] LinkedIn publish ({'sandbox' if li.sandbox else 'LIVE'}): {result}")
        results["passed"] += 1
    except Exception as e:
        print(f"  [FAIL] LinkedIn publish: {e}")
        results["failed"] += 1

    # Facebook
    fb = FacebookAdapter(
        api_key=settings.facebook_access_token or "",
        page_id=settings.facebook_page_id or "",
        sandbox=not settings.facebook_access_token,
    )
    print(f"\n  Facebook mode: {'SANDBOX' if fb.sandbox else 'LIVE'}")
    prepared = await fb.prepare_post("Testing on Facebook!", [])
    print(f"  [PASS] Facebook prepare_post OK")
    results["passed"] += 1
    try:
        result = await fb.publish(prepared)
        print(f"  [PASS] Facebook publish ({'sandbox' if fb.sandbox else 'LIVE'}): {result}")
        results["passed"] += 1
    except Exception as e:
        print(f"  [FAIL] Facebook publish: {e}")
        results["failed"] += 1

    # Instagram
    ig = InstagramAdapter(
        api_key=settings.instagram_access_token or "",
        ig_user_id=settings.instagram_business_account_id or "",
        sandbox=not settings.instagram_access_token,
    )
    print(f"\n  Instagram mode: {'SANDBOX' if ig.sandbox else 'LIVE'}")
    prepared = await ig.prepare_post("Visual storytelling with AI #ContentCreation", [])
    print(f"  [PASS] Instagram prepare_post OK")
    results["passed"] += 1
    try:
        result = await ig.publish(prepared)
        print(f"  [PASS] Instagram publish ({'sandbox' if ig.sandbox else 'LIVE'}): {result}")
        results["passed"] += 1
    except Exception as e:
        if "requires at least one media asset" in str(e):
            print(f"  [WARN] Instagram publish: Needs image/video - {e}")
            results["warnings"] += 1
        else:
            print(f"  [FAIL] Instagram publish: {e}")
            results["failed"] += 1


# 6. PUBLISHING VIA AUTH
def test_real_publishing():
    section("6. Publishing Endpoint (via auth)")
    if not TOKEN:
        warn("Publishing", "No auth token - skipping")
        return
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = httpx.post(f"{BASE}/api/publishing/schedule", headers=headers, json={
        "platforms": ["linkedin"],
        "content": "Testing Social Manager publishing pipeline!",
    })
    if r.status_code == 400:
        print(f"  [WARN] Publishing (linkedin): No active connection for user")
        print(f"       -> Connect via OAuth first (see instructions below)")
        results["warnings"] += 1
    elif r.status_code == 200:
        print(f"  [PASS] Publishing scheduled: {r.json()}")
        results["passed"] += 1
    else:
        check("POST /api/publishing/schedule", r)


def main():
    print(f"\n{'='*60}")
    print(f"  Social Manager - Full Backend Feature Test Suite")
    print(f"  Target: {BASE}")
    print(f"{'='*60}\n")

    try:
        r = httpx.get(f"{BASE}/health", headers={"Accept": "application/json"}, timeout=5)
        print(f"  Backend is ONLINE")
    except Exception:
        print(f"  [FAIL] Backend is OFFLINE at {BASE}")
        print(f"       Start it with: cd backend && python main.py")
        sys.exit(1)

    test_health()
    test_auth()
    test_v1_api()
    test_old_endpoints()
    asyncio.run(test_platform_adapters())
    test_real_publishing()

    total = results["passed"] + results["failed"]
    print(f"\n{'='*60}")
    print(f"  TEST SUMMARY")
    print(f"{'='*60}")
    print(f"  Passed:   {results['passed']}")
    print(f"  Failed:   {results['failed']}")
    print(f"  Warnings: {results['warnings']}")
    print(f"  Total:    {total}")
    print(f"{'='*60}\n")

    if results["failed"] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
