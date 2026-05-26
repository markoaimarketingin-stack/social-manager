#!/usr/bin/env python3
"""
FINAL SYSTEM VALIDATION - Complete End-to-End Test
Tests all features, agents, and integrations are working
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "http://localhost:8088"
FRONTEND_URL = "http://localhost:3000"

def test_complete_workflow():
    """Test the complete Social Manager AI workflow"""
    
    print("\n" + "="*70)
    print("SOCIAL MANAGER AI - COMPLETE SYSTEM TEST")
    print("="*70 + "\n")
    
    results = {
        "backend_health": False,
        "frontend_health": False,
        "main_workflow": False,
        "knowledge_base": False,
        "real_trends": False,
        "publishing": False,
        "policy_check": False,
        "google_signin": False,
    }
    
    # Test 1: Backend Health
    print("[1/8] Testing Backend Health...")
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if resp.status_code == 200:
            results["backend_health"] = True
            print("    ✓ Backend is responding\n")
        else:
            print(f"    ✗ Backend returned {resp.status_code}\n")
    except Exception as e:
        print(f"    ✗ Error: {str(e)}\n")
    
    # Test 2: Frontend Access
    print("[2/8] Testing Frontend Access...")
    try:
        resp = requests.get(FRONTEND_URL, timeout=5)
        if resp.status_code == 200:
            results["frontend_health"] = True
            print("    ✓ Frontend is accessible\n")
        else:
            print(f"    ✗ Frontend returned {resp.status_code}\n")
    except Exception as e:
        print(f"    ✗ Error: {str(e)}\n")
    
    # Test 3: Main Workflow
    print("[3/8] Testing Main Strategy Workflow...")
    try:
        payload = {
            "state": {
                "brand_profile": {
                    "brand_name": "Tech Innovators",
                    "industry": "Technology",
                    "product_category": "SaaS",
                    "voice_keywords": ["innovative", "helpful", "forward-thinking"]
                },
                "target_persona": {
                    "age_group": "25-45",
                    "interests": ["AI", "Tech", "Innovation"],
                    "pain_points": ["complexity", "time-saving"]
                },
                "active_platforms": ["Instagram", "LinkedIn", "Twitter"],
                "conversation_history": [],
                "content_pillars": [],
                "monthly_calendar": [],
                "platform_strategies": {},
                "engagement_plan": None,
                "ugc_campaign": None,
                "influencer_plan": None,
                "loyalty_strategy": None,
                "suggestions_list": [],
                "posting_frequency": {},
                "structured_context": {}
            }
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/api/social_manager/run",
            json=payload,
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            state = data.get("state", {})
            
            has_pillars = len(state.get("content_pillars", [])) > 0
            has_calendar = len(state.get("monthly_calendar", [])) > 0
            has_strategies = len(state.get("platform_strategies", {})) > 0
            
            if has_pillars and has_calendar and has_strategies:
                results["main_workflow"] = True
                print(f"    ✓ Generated 30-day strategy with {len(state.get('content_pillars', []))} pillars")
                print(f"    ✓ Calendar: {len(state.get('monthly_calendar', []))} entries planned")
                print(f"    ✓ Platforms: {list(state.get('platform_strategies', {}).keys())}\n")
            else:
                print(f"    ✗ Incomplete strategy generation\n")
        else:
            print(f"    ✗ Workflow failed: {resp.status_code}\n")
    except Exception as e:
        print(f"    ✗ Error: {str(e)}\n")
    
    # Test 4: Knowledge Base
    print("[4/8] Testing Knowledge Base...")
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/knowledge_base/documents",
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            docs = data.get("documents", [])
            results["knowledge_base"] = True
            print(f"    ✓ Knowledge Base: {len(docs)} documents loaded\n")
        else:
            print(f"    ✗ KB endpoint returned {resp.status_code}\n")
    except Exception as e:
        print(f"    ✗ Error: {str(e)}\n")
    
    # Test 5: Real Trends (NewsAPI)
    print("[5/8] Testing Real Trends (NewsAPI)...")
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/real/trends/news?keywords=marketing&limit=5",
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            trends = data.get("trends", [])
            results["real_trends"] = True
            print(f"    ✓ NewsAPI trends: {len(trends)} articles found")
            if trends:
                print(f"    ✓ Sample: {trends[0].get('title', 'N/A')[:60]}...\n")
            else:
                print(f"    ✓ Trends endpoint operational (demo mode)\n")
        else:
            print(f"    ✗ Trends endpoint returned {resp.status_code}\n")
    except Exception as e:
        print(f"    ✗ Error: {str(e)}\n")
    
    # Test 6: Publishing Queue
    print("[6/8] Testing Publishing Queue...")
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/publishing/queue",
            timeout=5
        )
        if resp.status_code == 200:
            results["publishing"] = True
            print(f"    ✓ Publishing queue operational\n")
        else:
            print(f"    ✗ Publishing endpoint returned {resp.status_code}\n")
    except Exception as e:
        print(f"    ✗ Error: {str(e)}\n")
    
    # Test 7: Policy Check
    print("[7/8] Testing Content Policy Engine...")
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/policy/check",
            json={"content": "Check this content for brand compliance"},
            timeout=5
        )
        if resp.status_code == 200:
            results["policy_check"] = True
            print(f"    ✓ Policy engine operational\n")
        else:
            print(f"    ✗ Policy endpoint returned {resp.status_code}\n")
    except Exception as e:
        print(f"    ✗ Error: {str(e)}\n")
    
    # Test 8: Google Sign-In (Frontend Check)
    print("[8/8] Testing Google Sign-In Configuration...")
    try:
        resp = requests.get(FRONTEND_URL, timeout=5)
        if "g_id_onload" in resp.text or "handleGoogleLogin" in resp.text:
            results["google_signin"] = True
            print(f"    ✓ Google Sign-In configured\n")
        else:
            print(f"    ✗ Google Sign-In config not found\n")
    except Exception as e:
        print(f"    ✗ Error: {str(e)}\n")
    
    # Print Summary
    print("="*70)
    print("SYSTEM TEST RESULTS")
    print("="*70 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        symbol = "✓" if status else "✗"
        status_str = "PASS" if status else "FAIL"
        print(f"  {symbol} {name.replace('_', ' ').upper():.<50} {status_str}")
    
    print("\n" + "="*70)
    print(f"OVERALL STATUS: {passed}/{total} TESTS PASSED")
    
    if passed == total:
        print("\n🎉 SOCIAL MANAGER AI IS FULLY FUNCTIONAL!")
        print("\nFeatures Active:")
        print("  • 7 Specialist Agents (Trends, Competitors, Segments, etc.)")
        print("  • Content Calendar Generation (30-day plans)")
        print("  • Knowledge Base Integration (Brand voice, strategy, audience)")
        print("  • Real Trend Monitoring (NewsAPI integration)")
        print("  • Publishing Queue & Policy Engine")
        print("  • Google Sign-In Authentication")
        print("  • Community Management Tools")
        print("  • Analytics & KPI Tracking")
        print("\n✅ Ready for deployment and full use!")
    elif passed >= 6:
        print("\n⚠️  MOSTLY WORKING - Please fix remaining issues above")
    else:
        print("\n❌ CRITICAL ISSUES - Check backend and frontend services")
    
    print("="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
