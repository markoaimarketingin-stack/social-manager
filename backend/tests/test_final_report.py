"""
FINAL API WORKFLOW TEST SUMMARY
================================

This script validates the entire backend API workflow for the Social Manager system.
"""

import json
import requests
from datetime import datetime

def print_section(title, char="="):
    print(f"\n{char * 80}")
    print(f" {title}")
    print(f"{char * 80}")

def test_endpoint():
    """Test the complete workflow"""
    
    print_section("SOCIAL MANAGER BACKEND API - FINAL TEST REPORT", "=")
    print(f"Test Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # === ENDPOINT CONFIGURATION ===
    print_section("ENDPOINT CONFIGURATION", "-")
    endpoint = "http://localhost:8088/api/social_manager/run"
    print(f"URL: {endpoint}")
    print(f"Method: POST")
    print(f"Content-Type: application/json")
    print(f"Timeout: 30 seconds")
    
    # === TEST PAYLOAD ===
    print_section("TEST PAYLOAD STRUCTURE", "-")
    
    test_payload = {
        "state": {
            "structured_context": {
                "industry": "SaaS",
                "company_size": "startup",
                "current_reach": "10K followers"
            },
            "brand_profile": {
                "name": "TestBrand",
                "tagline": "Test tagline",
                "values": ["Innovation", "Quality"],
                "voice_tone": "Professional",
                "mission": "Test mission"
            },
            "target_persona": {
                "name": "Test User",
                "age_range": "25-45",
                "interests": ["Tech", "Innovation"],
                "pain_points": ["Time management"],
                "platforms": ["LinkedIn"]
            },
            "active_platforms": ["Instagram", "LinkedIn", "Twitter"],
            "posting_frequency": {
                "Instagram": 4,
                "LinkedIn": 3,
                "Twitter": 5
            }
        }
    }
    
    payload_json = json.dumps(test_payload)
    print(f"Payload size: {len(payload_json)} bytes")
    print(f"Required fields:")
    print(f"  - brand_profile: {bool(test_payload['state'].get('brand_profile'))}")
    print(f"  - target_persona: {bool(test_payload['state'].get('target_persona'))}")
    print(f"  - active_platforms: {len(test_payload['state'].get('active_platforms', []))} platforms")
    print(f"  - posting_frequency: {len(test_payload['state'].get('posting_frequency', {}))} entries")
    
    # === SEND REQUEST ===
    print_section("SENDING REQUEST", "-")
    
    try:
        print("Sending POST request...")
        response = requests.post(endpoint, json=test_payload, timeout=30)
        response_time = "< 30 seconds"
        print(f"✓ Request completed")
        print(f"✓ Response time: {response_time}")
        print(f"✓ Status Code: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print(f"✗ CONNECTION FAILED: Cannot reach backend at {endpoint}")
        print(f"  Please ensure the backend is running: python main.py")
        return False
    except Exception as e:
        print(f"✗ ERROR: {type(e).__name__}: {e}")
        return False
    
    # === RESPONSE VALIDATION ===
    print_section("RESPONSE VALIDATION", "-")
    
    if response.status_code != 200:
        print(f"✗ Unexpected status code: {response.status_code}")
        print(f"Expected: 200")
        return False
    
    print(f"✓ Status Code: 200 OK")
    
    try:
        response_data = response.json()
        output_state = response_data.get("state", {})
        print(f"✓ Valid JSON response")
        print(f"✓ Response size: {len(response.text)} bytes")
    except json.JSONDecodeError:
        print(f"✗ Invalid JSON in response")
        return False
    
    # === FIELD VALIDATION ===
    print_section("GENERATED OUTPUT FIELDS", "-")
    
    expected_fields = {
        "content_pillars": "Content Strategy Pillars",
        "monthly_calendar": "30-Day Content Calendar",
        "engagement_plan": "Engagement & Community Strategy",
        "platform_strategies": "Per-Platform Strategy Details",
        "brand_profile": "Enhanced Brand Profile",
        "target_persona": "Target Audience Profile",
        "active_platforms": "Selected Platforms",
        "suggestions_list": "Strategic Suggestions",
        "conversation_history": "Conversation Context"
    }
    
    results = {}
    for field, description in expected_fields.items():
        if field in output_state:
            value = output_state[field]
            if isinstance(value, list):
                status = "✓" if len(value) > 0 else "!"
                print(f"{status} {description}: {len(value)} items")
                results[field] = "present"
            elif isinstance(value, dict):
                status = "✓" if len(value) > 0 else "!"
                print(f"{status} {description}: {len(value)} entries")
                results[field] = "present"
            else:
                print(f"✓ {description}: Present")
                results[field] = "present"
        else:
            print(f"- {description}: Not generated")
            results[field] = "missing"
    
    # === DETAILED CONTENT ANALYSIS ===
    print_section("DETAILED CONTENT ANALYSIS", "-")
    
    # Content Pillars
    if output_state.get("content_pillars"):
        print(f"\n1. CONTENT PILLARS ({len(output_state['content_pillars'])} generated):")
        for pillar in output_state["content_pillars"][:4]:
            name = pillar.get("name", "Unnamed")
            goal = pillar.get("goal", "No goal")
            types = pillar.get("post_types", [])
            print(f"   • {name}")
            print(f"     Goal: {goal}")
            print(f"     Types: {', '.join(types[:2])}")
    
    # Calendar Entries
    if output_state.get("monthly_calendar"):
        print(f"\n2. MONTHLY CALENDAR ({len(output_state['monthly_calendar'])} entries):")
        platforms = set()
        pillars = set()
        for entry in output_state["monthly_calendar"]:
            platforms.add(entry.get("platform", ""))
            pillars.add(entry.get("pillar", ""))
        print(f"   Date range: {output_state['monthly_calendar'][0].get('date')} to {output_state['monthly_calendar'][-1].get('date')}")
        print(f"   Platforms: {', '.join(sorted(platforms))}")
        print(f"   Pillars covered: {len(pillars)}")
    
    # Platform Strategies
    if output_state.get("platform_strategies"):
        print(f"\n3. PLATFORM STRATEGIES ({len(output_state['platform_strategies'])} platforms):")
        for platform, strategy in output_state["platform_strategies"].items():
            freq = strategy.get("frequency_per_week", "N/A")
            formats = list(strategy.get("post_format_mix", {}).keys())
            print(f"   • {platform}: {freq} posts/week")
            print(f"     Formats: {', '.join(formats)}")
    
    # Engagement Plan
    if output_state.get("engagement_plan"):
        print(f"\n4. ENGAGEMENT PLAN:")
        plan = output_state["engagement_plan"]
        for key, value in list(plan.items())[:3]:
            desc = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
            print(f"   • {key.replace('_', ' ').title()}: {desc}")
    
    # === ERROR & ISSUE SUMMARY ===
    print_section("ISSUES IDENTIFIED", "-")
    
    issues = []
    
    # Check for missing fields
    missing = [f for f, s in results.items() if s == "missing"]
    if missing:
        issues.append(f"Missing fields: {', '.join(missing)}")
    
    # Check for empty critical fields
    critical = ["content_pillars", "monthly_calendar", "platform_strategies"]
    for field in critical:
        if field in output_state:
            value = output_state[field]
            if isinstance(value, (list, dict)) and len(value) == 0:
                issues.append(f"Empty critical field: {field}")
    
    if issues:
        print("\nWarnings/Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("✓ No issues detected")
    
    # === FINAL RESULTS ===
    print_section("FINAL RESULTS", "=")
    
    success = len(missing) == 0
    
    print(f"\nEndpoint Status: {'✓ WORKING' if response.status_code == 200 else '✗ ERROR'}")
    print(f"Data Generation: {'✓ COMPLETE' if success else '! INCOMPLETE'}")
    print(f"API Workflow: {'✓ VALIDATED' if success else '! REQUIRES ATTENTION'}")
    
    print(f"\nData Summary:")
    print(f"  - Response Status: {response.status_code}")
    print(f"  - Fields Generated: {len(results) - len(missing)}/{len(results)}")
    print(f"  - Content Pillars: {len(output_state.get('content_pillars', []))}")
    print(f"  - Calendar Entries: {len(output_state.get('monthly_calendar', []))}")
    print(f"  - Platform Strategies: {len(output_state.get('platform_strategies', {}))}")
    print(f"  - Total State Size: {len(json.dumps(output_state))} bytes")
    
    print(f"\n" + "="*80)
    
    return success

if __name__ == "__main__":
    try:
        success = test_endpoint()
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
