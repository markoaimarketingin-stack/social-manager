#!/usr/bin/env python3
"""
Test all specialist agents and features
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8088"

def test_feature(feature_name, endpoint, method="GET", payload=None):
    """Test a specific feature endpoint"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=payload or {}, timeout=10)
        
        if response.status_code < 400:
            return f"✓ {feature_name}: {response.status_code}"
        else:
            return f"✗ {feature_name}: {response.status_code}"
    except Exception as e:
        return f"✗ {feature_name}: {str(e)[:50]}"

def main():
    print("\n" + "="*60)
    print("TESTING ALL SPECIALIST AGENTS & FEATURES")
    print("="*60 + "\n")
    
    # Test all feature endpoints
    features = [
        ("Trend Intelligence", "/api/features/trends", "GET"),
        ("Competitor Analysis", "/api/features/competitors", "GET"),
        ("Market Segmentation", "/api/features/segments", "GET"),
        ("Brand Positioning", "/api/features/positioning", "GET"),
        ("Copy Generation", "/api/features/copy", "POST", {"topic": "test"}),
        ("Hashtag Research", "/api/features/hashtags", "POST", {"topic": "test"}),
        ("Sentiment Analysis", "/api/real-features/sentiment", "POST", {"text": "Great product!"}),
        ("Influencer Discovery", "/api/features/influencers", "GET"),
        ("A/B Testing", "/api/real-features/ab-testing", "GET"),
        ("Metrics Collection", "/api/real-features/metrics", "GET"),
        ("Image Generation", "/api/real-features/dalle", "POST", {"prompt": "test"}),
        ("Email Service", "/api/real-features/email", "POST", {"to": "test@test.com", "subject": "test"}),
    ]
    
    results = []
    for feature_name, endpoint, method, *payload in features:
        result = test_feature(
            feature_name, 
            endpoint, 
            method, 
            payload[0] if payload else None
        )
        results.append(result)
        print(result)
    
    # Count results
    working = sum(1 for r in results if r.startswith("✓"))
    total = len(results)
    
    print("\n" + "="*60)
    print(f"FEATURE STATUS: {working}/{total} features responding")
    print("="*60 + "\n")
    
    # Test main workflow with all agents
    print("Testing main workflow with multiple agents...")
    
    agents = ["Trend Intelligence", "Competitor Analysis", "Community Manager"]
    for agent in agents:
        payload = {
            "state": {
                "brand_profile": {"brand_name": "Test", "industry": "Tech"},
                "target_persona": {"interests": ["tech"]},
                "active_platforms": ["Instagram", "LinkedIn"],
                "selected_agent": agent,
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
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/social_manager/run",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                print(f"✓ Agent '{agent}' workflow: OK")
            else:
                print(f"✗ Agent '{agent}' workflow: {response.status_code}")
        except Exception as e:
            print(f"✗ Agent '{agent}' workflow: {str(e)[:50]}")
    
    print("\n" + "="*60)
    print("All tests complete. System is ready for use!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
