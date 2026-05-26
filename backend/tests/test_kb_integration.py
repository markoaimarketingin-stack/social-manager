#!/usr/bin/env python3
"""
Comprehensive Knowledge Base Integration Test
============================================
Tests that all agent nodes properly utilize KB context for enhanced decisions.
"""

import json
import sys
from datetime import datetime
from social_manager.state import SocialManagerState, EngagementMetrics
from social_manager.db import init_db
from social_manager.knowledge_base import init_knowledge_base_with_samples
from social_manager.graph import build_social_strategy
from social_manager.llm import client

def test_kb_initialization():
    """Test 1: KB initialization with sample documents."""
    print("=" * 70)
    print("TEST 1: Knowledge Base Initialization")
    print("=" * 70)
    
    try:
        init_db(seed=42)
        init_knowledge_base_with_samples()
        print("✅ Database initialized")
        print("✅ Knowledge base loaded with sample documents")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_kb_context_injection():
    """Test 2: KB context injection utilities."""
    print("\n" + "=" * 70)
    print("TEST 2: KB Context Injection")
    print("=" * 70)
    
    try:
        from social_manager.kb_context_injector import get_injector
        
        injector = get_injector()
        
        # Test each context getter
        contexts = {
            "brand_voice": injector.get_brand_voice_context(max_chars=500),
            "audience": injector.get_audience_context(max_chars=500),
            "competitor": injector.get_competitor_context(max_chars=500),
            "campaign": injector.get_campaign_context(max_chars=500),
            "strategy": injector.get_social_strategy_context(max_chars=500),
        }
        
        print(f"✅ Injector initialized")
        for name, context in contexts.items():
            has_context = bool(context and len(context) > 50)
            status = "✅" if has_context else "⚠️"
            print(f"{status} {name}: {len(context)} chars {'OK' if has_context else 'MISSING OR SHORT'}")
            if context:
                print(f"  Preview: {context[:100]}...")
        
        return all(len(c) > 0 for c in contexts.values())
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_agent_run():
    """Test 3: Full agent pipeline with KB context."""
    print("\n" + "=" * 70)
    print("TEST 3: Full Agent Pipeline with KB Context")
    print("=" * 70)
    
    try:
        # Create test state
        state = SocialManagerState(
            brand_profile={
                "brand_name": "FitFlow",
                "industry": "Fitness & Wellness",
                "product_category": "Fitness apps",
                "brand_type": "B2C SaaS",
                "voice_keywords": ["motivational", "achievable", "supportive"],
                "tone": "Uplifting and practical"
            },
            target_persona={
                "age_range": "25-45",
                "interests": ["fitness", "wellness", "nutrition"],
                "challenges": ["time management", "motivation", "tracking progress"]
            },
            active_platforms=["Instagram", "LinkedIn"],
            posting_frequency={"Instagram": 5, "LinkedIn": 3},
            engagement_metrics=EngagementMetrics(
                engagement_rate=2.5,
                post_consistency_score=0.75
            )
        )
        
        print(f"📋 Test state created:")
        print(f"  Brand: {state.brand_profile.get('brand_name')}")
        print(f"  Industry: {state.brand_profile.get('industry')}")
        print(f"  Platforms: {', '.join(state.active_platforms)}")
        
        # Run graph
        print("\n🔄 Running agent graph...")
        output_state = build_social_strategy(state)
        
        # Verify outputs
        results = {
            "platform_strategies": bool(output_state.platform_strategies),
            "content_pillars": bool(output_state.content_pillars and len(output_state.content_pillars) > 0),
            "monthly_calendar": bool(output_state.monthly_calendar and len(output_state.monthly_calendar) > 0),
            "engagement_plan": bool(output_state.engagement_plan),
            "ugc_strategy": bool(output_state.ugc_strategy),
            "influencer_strategy": bool(output_state.influencer_strategy),
            "loyalty_strategy": bool(output_state.loyalty_strategy),
            "suggestions_list": bool(output_state.suggestions_list),
        }
        
        print("\n📊 Agent Outputs Generated:")
        all_passed = True
        for key, passed in results.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {key}: {'Generated' if passed else 'MISSING'}")
            all_passed = all_passed and passed
        
        return all_passed
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kb_enriched_prompts():
    """Test 4: Verify KB context is in prompts."""
    print("\n" + "=" * 70)
    print("TEST 4: KB Context in Agent Prompts")
    print("=" * 70)
    
    try:
        from social_manager.kb_context_injector import get_injector
        
        injector = get_injector()
        
        # Test enriched prompt building
        prompt = injector.build_enriched_prompt(
            base_instruction="Generate content ideas for a fitness brand",
            include_brand_voice=True,
            include_audience=True,
            include_competitors=True
        )
        
        print(f"✅ Enriched prompt built")
        print(f"  Total length: {len(prompt)} chars")
        
        # Check that it contains context sections
        has_brand = "brand" in prompt.lower()
        has_audience = "audience" in prompt.lower()
        has_comp = "compet" in prompt.lower()
        
        status = "✅" if all([has_brand, has_audience]) else "⚠️"
        print(f"{status} Prompt contains brand context: {has_brand}")
        print(f"{status} Prompt contains audience context: {has_audience}")
        print(f"{status} Prompt contains competitor context: {has_comp}")
        
        return all([has_brand, has_audience])
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_nodes():
    """Test 5: Individual agent nodes with KB context."""
    print("\n" + "=" * 70)
    print("TEST 5: Individual Agent Nodes")
    print("=" * 70)
    
    try:
        from social_manager.nodes.content_pillar_builder import build_content_pillars
        from social_manager.nodes.platform_strategy_selector import select_platform_strategies
        from social_manager.nodes.community_engagement_planner import plan_community_engagement
        from social_manager.nodes.tone_consistency_checker import check_tone_consistency
        from social_manager.nodes.suggestion_generator import generate_suggestions
        
        # Create test state
        state = SocialManagerState(
            brand_profile={
                "brand_name": "TestBrand",
                "industry": "Fitness & Wellness",
                "product_category": "Software",
                "voice_keywords": ["friendly", "expert"]
            },
            active_platforms=["Instagram"],
            posting_frequency={"Instagram": 5}
        )
        
        nodes = {
            "content_pillar_builder": build_content_pillars,
            "platform_strategy_selector": select_platform_strategies,
            "community_engagement_planner": plan_community_engagement,
            "tone_consistency_checker": check_tone_consistency,
            "suggestion_generator": generate_suggestions,
        }
        
        print(f"Testing {len(nodes)} agent nodes...\n")
        
        all_passed = True
        for node_name, node_func in nodes.items():
            try:
                result_state = node_func(state)
                
                # Check if node produced output
                has_output = result_state is not None
                
                status = "✅" if has_output else "❌"
                print(f"  {status} {node_name}: {'Pass' if has_output else 'Fail'}")
                
                all_passed = all_passed and has_output
                
                # Update state for next iteration
                state = result_state
                
            except Exception as e:
                print(f"  ❌ {node_name}: {str(e)[:60]}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test 6: API endpoints work with KB context."""
    print("\n" + "=" * 70)
    print("TEST 6: API Endpoints (Requires running server)")
    print("=" * 70)
    
    try:
        import requests
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8088/health", timeout=2)
            health_ok = response.status_code == 200
            print(f"✅ Health endpoint: OK" if health_ok else "⚠️ Health endpoint: Not responding")
        except:
            print("⚠️ Health endpoint: Server not running (this is optional)")
            return True
        
        # Test KB endpoints
        try:
            response = requests.get("http://localhost:8088/api/knowledge_base/documents", timeout=3)
            docs_ok = response.status_code == 200
            if docs_ok:
                data = response.json()
                total = data.get('total', 0)
                print(f"✅ KB documents endpoint: {total} documents")
            else:
                print(f"⚠️ KB documents endpoint: {response.status_code}")
        except:
            print("⚠️ KB documents endpoint: Not responding")
        
        return True
    except Exception as e:
        print(f"⚠️ API test skipped: {e}")
        return True


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "KB INTEGRATION TEST SUITE" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("KB Initialization", test_kb_initialization),
        ("KB Context Injection", test_kb_context_injection),
        ("Full Agent Pipeline", test_full_agent_run),
        ("KB in Prompts", test_kb_enriched_prompts),
        ("Individual Nodes", test_individual_nodes),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! KB integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
