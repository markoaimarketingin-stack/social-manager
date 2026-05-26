"""
Example usage of the Agent Knowledge Base.
Demonstrates how the agent can leverage the knowledge base for decision-making.
"""

from social_manager.db import SessionLocal
from social_manager.knowledge_base_query import KnowledgeBaseQuery


def example_plan_content_strategy():
    """Example: Plan comprehensive content strategy using knowledge base."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Plan Content Strategy for Fitness Brand on Instagram")
    print("="*80)
    
    session = SessionLocal()
    kb = KnowledgeBaseQuery(session)
    
    # Scenario: Fitness brand wants to plan content for Instagram & TikTok
    industry = "Fitness & Wellness"
    platforms = ["Instagram", "TikTok"]
    
    # Get comprehensive recommendation
    strategy = kb.recommend_content_mix(industry, platforms)
    
    print(f"\n📊 STRATEGY FOR: {industry}")
    print(f"📱 Platforms: {', '.join(platforms)}")
    
    print(f"\n✅ CONTENT PILLAR MIX:")
    for pillar, details in strategy["content_pillars"].items():
        print(f"  • {pillar}: {details['weight']}% weight, {details['frequency_per_month']} posts/month")
        print(f"    Formats: {', '.join(details['formats'][:3])}")
    
    print(f"\n📳 PLATFORM-SPECIFIC STRATEGIES:")
    for platform, strat in strategy["platform_strategies"].items():
        print(f"\n  {platform}:")
        print(f"    • Posting frequency: {strat['posting_frequency']} posts/week")
        print(f"    • Best format: {strat['best_format']}")
        print(f"    • Recommended CTA: {strat['recommended_cta']}")
        print(f"    • Best posting times: {strat['posting_times']}")
    
    print(f"\n🎯 EXPECTED ENGAGEMENT:")
    print(f"  • Benchmark rate: {strategy['expected_engagement']['benchmark_engagement_rate']}%")
    print(f"  • Expected conversion: {strategy['expected_engagement']['benchmark_conversion_rate']}%")
    
    session.close()


def example_viral_content_strategy():
    """Example: Create viral content strategy."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Design Viral Content Strategy for TikTok")
    print("="*80)
    
    session = SessionLocal()
    kb = KnowledgeBaseQuery(session)
    
    platform = "TikTok"
    industry = "Fitness & Wellness"
    
    # Get viral strategy
    strategy = kb.suggest_viral_content_strategy(platform, industry)
    
    print(f"\n📱 PLATFORM: {platform}")
    print(f"🏢 INDUSTRY: {industry}")
    
    print(f"\n🎣 VIRAL HOOK:")
    print(f"  Pattern: {strategy['viral_hook']}")
    
    print(f"\n📸 RECOMMENDED FORMATS:")
    for fmt in strategy['viral_formats']:
        print(f"  • {fmt}")
    
    print(f"\n💬 ENGAGEMENT TACTICS TO COMBINE:")
    for i, tactic in enumerate(strategy['engagement_tactics'], 1):
        print(f"  {i}. {tactic}")
    
    print(f"\n📈 EXPECTED ENGAGEMENT LIFT: +{strategy['expected_lift']}%")
    
    session.close()


def example_platform_comparison():
    """Example: Compare platforms for best practices."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Platform Comparison & Best Practices")
    print("="*80)
    
    session = SessionLocal()
    kb = KnowledgeBaseQuery(session)
    
    platforms = ["Instagram", "LinkedIn", "X (Twitter)", "TikTok"]
    
    print("\n📊 PLATFORM PERFORMANCE COMPARISON\n")
    print(f"{'Platform':<15} {'Freq/Week':<12} {'Eng. Bench':<12} {'Best Format':<20} {'Algorithm':<15}")
    print("-" * 75)
    
    for platform in platforms:
        freq = kb.get_platform_posting_frequency(platform)
        plat_obj = kb.get_platform_by_name(platform)
        best_fmt = kb.get_best_format_by_engagement(platform)
        
        print(f"{platform:<15} {freq:<12} {plat_obj.average_engagement_rate_benchmark}%{'':<8} {best_fmt.format_name if best_fmt else 'N/A':<20} {plat_obj.algorithm_prefers_content_type:<15}")
    
    print(f"\n🎯 VIRAL FORMAT ANALYSIS:")
    for platform in platforms:
        viral = kb.get_viral_formats(platform)
        if viral:
            print(f"\n  {platform}:")
            for fmt in viral:
                print(f"    • {fmt.format_name}: {fmt.average_engagement_rate}% engagement, {fmt.average_reach:,} avg reach")
    
    session.close()


def example_influencer_strategy():
    """Example: Plan influencer collaboration."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Influencer Collaboration Strategy by Budget")
    print("="*80)
    
    session = SessionLocal()
    kb = KnowledgeBaseQuery(session)
    
    budgets = {
        "Nano": 300,
        "Micro": 3000,
        "Macro": 25000,
        "Mega": 100000
    }
    
    print("\n💰 INFLUENCER TIERS BY BUDGET\n")
    
    for tier_name, budget in budgets.items():
        tier = kb.get_influencer_tier(tier_name.lower())
        
        print(f"{'='*60}")
        print(f"🎯 TIER: {tier_name.upper()}")
        print(f"💵 Budget: ${budget:,}")
        print(f"📍 Followers: {tier.follower_range_min:,} - {tier.follower_range_max:,}")
        print(f"📊 Engagement: {tier.average_engagement_rate}%")
        print(f"🔄 ROI Multiplier: {tier.expected_roi_multiplier}x")
        print(f"📧 Outreach: {tier.outreach_approach}")
        print(f"🤝 Collaboration Types: {', '.join(tier.collaboration_types)}")
    
    session.close()


def example_engagement_tactics():
    """Example: Recommend engagement tactics."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Engagement Tactics for Instagram")
    print("="*80)
    
    session = SessionLocal()
    kb = KnowledgeBaseQuery(session)
    
    platform = "Instagram"
    time_budget = 2.0  # hours per week
    
    # Get tactics for platform
    all_tactics = kb.get_engagement_tactics_for_platform(platform)
    feasible_tactics = kb.get_tactics_by_time_investment(time_budget)
    
    print(f"\n📱 PLATFORM: {platform}")
    print(f"⏱️  TIME BUDGET: {time_budget} hours/week")
    
    print(f"\n💡 TOP ENGAGEMENT TACTICS FOR {platform}:")
    for i, tactic in enumerate(all_tactics[:3], 1):
        print(f"\n  {i}. {tactic.tactic_name}")
        print(f"     Expected lift: +{tactic.expected_engagement_rate_lift}%")
        print(f"     Time required: {tactic.time_investment_hours} hours")
        print(f"     How: {', '.join(tactic.execution_steps[:2])}...")
    
    print(f"\n⚡ FEASIBLE TACTICS (within {time_budget} hour budget):")
    for tactic in feasible_tactics:
        print(f"  • {tactic.tactic_name} ({tactic.time_investment_hours} hrs, +{tactic.expected_engagement_rate_lift}% lift)")
    
    session.close()


def example_industry_benchmarks():
    """Example: Get industry benchmarks."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Industry Benchmarks & Best Practices")
    print("="*80)
    
    session = SessionLocal()
    kb = KnowledgeBaseQuery(session)
    
    industry = "E-Commerce"
    
    practice = kb.get_industry_practice(industry)
    
    print(f"\n🏢 INDUSTRY: {industry}")
    
    print(f"\n📱 PLATFORM PRIORITIES:")
    platforms = kb.get_platform_priority_for_industry(industry)
    for platform, priority in platforms:
        print(f"  {priority}. {platform}")
    
    print(f"\n📊 BENCHMARKS:")
    print(f"  • Engagement Rate: {practice.engagement_benchmarks['engagement_rate']}%")
    print(f"  • CTR: {practice.engagement_benchmarks['ctr']}%")
    print(f"  • Conversion Rate: {practice.engagement_benchmarks['conversion_rate']}%")
    
    print(f"\n📝 TOP CONTENT PILLARS:")
    for pillar in practice.top_content_pillars:
        print(f"  • {pillar}")
    
    print(f"\n🎯 PROVEN GROWTH TACTICS:")
    for tactic in practice.proven_growth_tactics:
        print(f"  • {tactic}")
    
    print(f"\n⚠️  COMMON PAIN POINTS:")
    for pain in practice.common_pain_points:
        print(f"  • {pain}")
    
    session.close()


def example_seasonal_opportunities():
    """Example: Identify seasonal opportunities."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Seasonal Campaign Opportunities")
    print("="*80)
    
    session = SessionLocal()
    kb = KnowledgeBaseQuery(session)
    
    industry = "E-Commerce"
    
    opps = kb.get_seasonal_opportunities_by_industry(industry)
    
    print(f"\n🏢 INDUSTRY: {industry}")
    print(f"📅 SEASONAL OPPORTUNITIES:\n")
    
    for opp in opps:
        print(f"➡️  {opp.opportunity_name}")
        print(f"    📆 Date: {opp.event_date} (Duration: {opp.duration_days} days)")
        print(f"    📈 Expected boost: +{opp.expected_engagement_lift}% engagement")
        print(f"    🎨 Theme: {opp.content_theme}")
        print(f"    📋 Playbook: {', '.join(opp.campaign_playbook)}")
        print(f"    #️⃣  Hashtags: {', '.join(opp.hashtags)}")
        print()
    
    session.close()


def example_hooks_and_ctas():
    """Example: Select best hooks and CTAs."""
    print("\n" + "="*80)
    print("EXAMPLE 8: Optimal Hooks & CTAs Selection")
    print("="*80)
    
    session = SessionLocal()
    kb = KnowledgeBaseQuery(session)
    
    platform = "Instagram"
    
    print(f"\n📱 PLATFORM: {platform}")
    
    print(f"\n🎣 BEST VIRAL HOOK FOR {platform}:")
    hook = kb.get_best_hook_for_platform(platform)
    if hook:
        print(f"  Name: {hook.hook_name}")
        print(f"  Pattern: {hook.hook_pattern}")
        print(f"  Psychology: {hook.psychology_principle}")
        print(f"  Expected lift: +{hook.average_engagement_lift}%")
        print(f"  Examples:")
        for example in hook.hook_examples[:2]:
            print(f"    • {example}")
    
    print(f"\n✅ BEST CTAs FOR {platform}:")
    ctas = ["shop", "learn_more", "engage", "share"]
    for cta_type in ctas:
        cta = kb.get_cta(cta_type)
        if cta:
            print(f"  • {cta.cta_text} (CTR: {cta.average_ctr}%, Conv: {cta.expected_conversion_rate}%)")
            print(f"    Variations: {', '.join(cta.variations[:2])}")
    
    session.close()


def example_content_mix():
    """Example: Calculate content mix for month."""
    print("\n" + "="*80)
    print("EXAMPLE 9: 30-Day Content Calendar Planning")
    print("="*80)
    
    session = SessionLocal()
    kb = KnowledgeBaseQuery(session)
    
    industry = "Fitness & Wellness"
    num_days = 30
    num_posts = 15  # 15 posts in 30 days
    
    mix = kb.get_content_mix_by_industry(industry)
    
    print(f"\n🏢 INDUSTRY: {industry}")
    print(f"📅 PERIOD: 30 days")
    print(f"📊 TOTAL POSTS: {num_posts}\n")
    
    print(f"📋 CONTENT BREAKDOWN:")
    for pillar_name, percentage in mix.items():
        num_posts_pillar = round(num_posts * (percentage / 100))
        print(f"  {pillar_name}: {percentage}% ({num_posts_pillar} posts)")
    
    session.close()


if __name__ == "__main__":
    print("\n🚀 AGENT KNOWLEDGE BASE EXAMPLES")
    print("=" * 80)
    print("These examples show how the agent leverages the knowledge base")
    print("to make data-driven decisions for social media strategy.")
    
    # Run all examples
    example_plan_content_strategy()
    example_viral_content_strategy()
    example_platform_comparison()
    example_influencer_strategy()
    example_engagement_tactics()
    example_industry_benchmarks()
    example_seasonal_opportunities()
    example_hooks_and_ctas()
    example_content_mix()
    
    print("\n" + "="*80)
    print("✅ EXAMPLES COMPLETED")
    print("="*80)
    print("\n💡 Use these patterns in the agent's decision-making logic!")
