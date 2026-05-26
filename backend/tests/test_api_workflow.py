"""
Test script for Social Manager Backend API workflow.
Tests the /api/social_manager/run endpoint with a minimal valid SocialManagerState.
"""

import json
import requests
import sys
from datetime import datetime

def create_minimal_state():
    """Create a minimal but valid SocialManagerState for testing."""
    state = {
        "structured_context": {
            "industry": "Technology/SaaS",
            "company_size": "startup",
            "current_reach": "5000 followers"
        },
        "brand_profile": {
            "name": "TechStartup",
            "tagline": "Making tech accessible",
            "values": ["Innovation", "Community", "Transparency"],
            "voice_tone": "Friendly and professional",
            "mission": "Empower users with simple tech solutions",
            "unique_selling_point": "Simple, powerful, affordable"
        },
        "target_persona": {
            "name": "Tech-savvy Entrepreneur",
            "age_range": "25-45",
            "interests": ["Technology", "Productivity", "Business"],
            "pain_points": ["Time management", "Tool overload"],
            "platforms": ["LinkedIn", "Twitter", "Instagram"],
            "content_preferences": ["Tips", "How-tos", "Case studies"]
        },
        "active_platforms": ["instagram", "linkedin", "twitter"],
        "posting_frequency": {
            "instagram": 4,
            "linkedin": 3,
            "twitter": 5
        },
        "engagement_metrics": {
            "engagement_rate": 2.5,
            "follower_growth": 150,
            "post_consistency_score": 0.85
        },
        "conversation_history": []
    }
    return state

def test_api_endpoint():
    """Test the /api/social_manager/run endpoint."""
    
    # Configuration
    API_URL = "http://localhost:8088"
    ENDPOINT = "/api/social_manager/run"
    FULL_URL = f"{API_URL}{ENDPOINT}"
    
    print("\n" + "="*70)
    print("SOCIAL MANAGER API WORKFLOW TEST")
    print("="*70)
    
    # Step 1: Create minimal state
    print("\n[STEP 1] Creating minimal SocialManagerState...")
    state = create_minimal_state()
    print("  OK State created with:")
    print(f"    - Brand: {state['brand_profile'].get('name')}")
    print(f"    - Platforms: {', '.join(state['active_platforms'])}")
    print(f"    - Target Persona: {state['target_persona'].get('name')}")
    
    # Step 2: Prepare request
    print("\n[STEP 2] Preparing POST request...")
    request_payload = {
        "state": state
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    print(f"  URL: {FULL_URL}")
    print(f"  Payload size: {len(json.dumps(request_payload))} bytes")
    
    # Step 3: Send request
    print("\n[STEP 3] Sending request to backend...")
    try:
        response = requests.post(
            FULL_URL,
            json=request_payload,
            headers=headers,
            timeout=30
        )
    except requests.exceptions.ConnectionError as e:
        print(f"  FAIL CONNECTION ERROR: Cannot reach {API_URL}")
        print(f"    Error: {e}")
        print(f"\n    Make sure the backend is running on {API_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"  FAIL TIMEOUT: Request took too long (>30s)")
        return False
    except Exception as e:
        print(f"  FAIL ERROR: {type(e).__name__}: {e}")
        return False
    
    # Step 4: Analyze response
    print(f"\n[STEP 4] Analyzing response...")
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"  FAIL Unexpected status code (expected 200)")
        print(f"\n  Response body:")
        try:
            error_data = response.json()
            print(f"    {json.dumps(error_data, indent=2)}")
        except:
            print(f"    {response.text[:500]}")
        return False
    
    print(f"  OK Status 200 OK")
    
    # Step 5: Parse response
    print(f"\n[STEP 5] Parsing response data...")
    try:
        response_data = response.json()
        output_state = response_data.get("state", {})
    except json.JSONDecodeError as e:
        print(f"  FAIL Invalid JSON response: {e}")
        print(f"    Response: {response.text[:500]}")
        return False
    
    # Step 6: Validate required output fields
    print(f"\n[STEP 6] Validating output fields...")
    
    required_fields = {
        "content_pillars": "Content Pillars",
        "monthly_calendar": "Monthly Calendar",
        "engagement_plan": "Engagement Plan",
        "platform_strategies": "Platform Strategies",
        "brand_profile": "Brand Profile",
        "active_platforms": "Active Platforms"
    }
    
    validation_results = {}
    missing_fields = []
    
    for field_name, field_label in required_fields.items():
        if field_name in output_state:
            field_value = output_state[field_name]
            if isinstance(field_value, list):
                count = len(field_value)
                status = "OK" if count > 0 else "WARN"
                print(f"  {status} {field_label}: {count} items")
                validation_results[field_name] = (True, count)
            elif isinstance(field_value, dict):
                count = len(field_value)
                status = "OK" if count > 0 else "WARN"
                print(f"  {status} {field_label}: {count} keys")
                validation_results[field_name] = (True, count)
            else:
                print(f"  OK {field_label}: Present")
                validation_results[field_name] = (True, "present")
        else:
            print(f"  FAIL {field_label}: MISSING")
            validation_results[field_name] = (False, None)
            missing_fields.append(field_name)
    
    # Step 7: Print detailed output
    print(f"\n[STEP 7] Detailed output summary...")
    
    if output_state.get("content_pillars"):
        print(f"\n  Content Pillars ({len(output_state['content_pillars'])} items):")
        for pillar in output_state["content_pillars"][:3]:
            if isinstance(pillar, dict):
                print(f"    - {pillar.get('name', 'Unnamed')}: {pillar.get('goal', 'No goal')}")
    
    if output_state.get("monthly_calendar"):
        print(f"\n  Monthly Calendar ({len(output_state['monthly_calendar'])} entries):")
        for entry in output_state["monthly_calendar"][:3]:
            if isinstance(entry, dict):
                date = entry.get('date', 'N/A')
                pillar = entry.get('pillar', 'N/A')
                platform = entry.get('platform', 'N/A')
                print(f"    - {date}: {pillar} ({platform})")
    
    if output_state.get("platform_strategies"):
        print(f"\n  Platform Strategies ({len(output_state['platform_strategies'])} platforms):")
        for platform, strategy in list(output_state["platform_strategies"].items())[:3]:
            if isinstance(strategy, dict):
                freq = strategy.get('frequency_per_week', 'N/A')
                print(f"    - {platform}: {freq} posts/week")
    
    # Step 8: Summary
    print(f"\n[STEP 8] Test Summary")
    print("="*70)
    
    success_count = sum(1 for passed, _ in validation_results.values() if passed)
    total_count = len(validation_results)
    
    print(f"\nValidation Results: {success_count}/{total_count} fields present")
    
    if missing_fields:
        print(f"\nMissing Fields ({len(missing_fields)}):")
        for field in missing_fields:
            print(f"  - {field}")
    
    success = len(missing_fields) == 0
    
    # Step 9: Final verdict
    print(f"\n[RESULT]")
    if success:
        print(f"  OK ENDPOINT WORKING CORRECTLY")
        print(f"  OK All expected fields present")
        print(f"  OK API workflow validated successfully")
    else:
        print(f"  WARN ENDPOINT PARTIALLY WORKING")
        print(f"  WARN {len(missing_fields)} field(s) missing from response")
        print(f"  WARN Check if build_social_strategy() is generating all required fields")
    
    print(f"\nResponse size: {len(response.text)} bytes")
    print("="*70 + "\n")
    
    return success

if __name__ == "__main__":
    try:
        success = test_api_endpoint()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
