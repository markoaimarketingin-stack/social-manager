"""
Detailed API test with extended field inspection
"""

import json
import requests

API_URL = "http://localhost:8088/api/social_manager/run"

state = {
    "structured_context": {
        "industry": "Technology/SaaS",
        "company_size": "startup"
    },
    "brand_profile": {
        "name": "TechStartup",
        "tagline": "Making tech accessible",
        "values": ["Innovation"],
        "voice_tone": "Friendly",
        "mission": "Empower users"
    },
    "target_persona": {
        "name": "Entrepreneur",
        "age_range": "25-45",
        "interests": ["Tech"],
        "pain_points": ["Time management"],
        "platforms": ["LinkedIn"]
    },
    "active_platforms": ["instagram", "linkedin"],
    "posting_frequency": {
        "instagram": 4,
        "linkedin": 3
    }
}

print("\n[TEST] Sending request to API...")
response = requests.post(API_URL, json={"state": state}, timeout=30)
data = response.json()
output_state = data["state"]

print("\n[RESPONSE ANALYSIS]")
print("="*70)

# Check each field in detail
print("\n1. BRAND PROFILE:")
if output_state.get("brand_profile"):
    for key, value in output_state["brand_profile"].items():
        if isinstance(value, (list, dict)):
            print(f"   {key}: {len(value)} items")
        else:
            print(f"   {key}: {str(value)[:50]}")

print("\n2. CONTENT PILLARS:")
if output_state.get("content_pillars"):
    print(f"   Total: {len(output_state['content_pillars'])} pillars")
    for pillar in output_state["content_pillars"]:
        print(f"   - {pillar.get('name')}")

print("\n3. MONTHLY CALENDAR:")
if output_state.get("monthly_calendar"):
    print(f"   Total: {len(output_state['monthly_calendar'])} entries")
    platforms_in_calendar = set()
    pillars_in_calendar = set()
    for entry in output_state["monthly_calendar"]:
        platforms_in_calendar.add(entry.get("platform"))
        pillars_in_calendar.add(entry.get("pillar"))
    print(f"   Platforms: {', '.join(sorted(platforms_in_calendar))}")
    print(f"   Pillars: {', '.join(sorted(pillars_in_calendar))}")

print("\n4. ENGAGEMENT PLAN:")
if output_state.get("engagement_plan"):
    plan = output_state["engagement_plan"]
    print(f"   Keys present: {list(plan.keys())}")

print("\n5. PLATFORM STRATEGIES:")
if output_state.get("platform_strategies"):
    print(f"   Total: {len(output_state['platform_strategies'])} strategies")
    for platform, strat in output_state["platform_strategies"].items():
        print(f"   - {platform}: {list(strat.keys())}")
else:
    print(f"   WARNING: Empty or not generated")

print("\n6. OTHER FIELDS:")
fields_to_check = ["conversation_history", "suggestions_list", "posts", "assets"]
for field in fields_to_check:
    if field in output_state:
        value = output_state[field]
        if isinstance(value, list):
            print(f"   {field}: {len(value)} items")
        elif isinstance(value, dict):
            print(f"   {field}: {len(value)} keys")
        else:
            print(f"   {field}: Present")

print("\n[SUMMARY]")
print(f"Response Status: {response.status_code}")
print(f"Response Size: {len(response.text)} bytes")
print(f"State Fields: {len(output_state)} total")
print("\n" + "="*70)
