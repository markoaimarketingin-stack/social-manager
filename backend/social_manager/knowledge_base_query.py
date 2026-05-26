"""
Knowledge Base Query and Retrieval Module.
Provides functions to query the knowledge base for agent decision-making.
"""

from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from social_manager.knowledge_base_schema import (
    PlatformKnowledge, PostFormatKnowledge, ContentPillarTemplate, CTATemplate,
    HookTemplate, EngagementTactic, InfluencerTierKnowledge, IndustryBestPractice,
    EngagementBenchmark, OptimalPostingTime, SeasonalOpportunity, BrandSafetyGuide,
    ContentRepurposingStrategy
)


class KnowledgeBaseQuery:
    """Query interface for knowledge base retrieval."""
    
    def __init__(self, db_session: Session):
        self.session = db_session
    
    # ===== PLATFORM KNOWLEDGE =====
    
    def get_platform_by_name(self, platform_name: str) -> Optional[PlatformKnowledge]:
        """Get complete platform knowledge."""
        return self.session.query(PlatformKnowledge).filter_by(platform_name=platform_name).first()
    
    def get_all_platforms(self) -> List[PlatformKnowledge]:
        """Get all available platforms."""
        return self.session.query(PlatformKnowledge).all()
    
    def get_platform_posting_frequency(self, platform_name: str) -> Optional[int]:
        """Get optimal posting frequency for a platform per week."""
        platform = self.get_platform_by_name(platform_name)
        return platform.optimal_post_frequency_per_week if platform else None
    
    def get_platform_supported_formats(self, platform_name: str) -> List[str]:
        """Get list of supported formats for a platform."""
        platform = self.get_platform_by_name(platform_name)
        return platform.supported_formats if platform else []
    
    def get_platform_best_posting_times(self, platform_name: str) -> Optional[Dict]:
        """Get best posting times for platform by day of week."""
        platform = self.get_platform_by_name(platform_name)
        return platform.best_posting_times if platform else None
    
    # ===== POST FORMAT KNOWLEDGE =====
    
    def get_format_performance(self, platform_name: str, format_name: str) -> Optional[PostFormatKnowledge]:
        """Get performance data for specific format on platform."""
        platform = self.get_platform_by_name(platform_name)
        if not platform:
            return None
        
        return self.session.query(PostFormatKnowledge).filter(
            PostFormatKnowledge.platform_id == platform.id,
            PostFormatKnowledge.format_name == format_name
        ).first()
    
    def get_best_format_by_engagement(self, platform_name: str) -> Optional[PostFormatKnowledge]:
        """Get highest-engagement format for a platform."""
        platform = self.get_platform_by_name(platform_name)
        if not platform:
            return None
        
        return self.session.query(PostFormatKnowledge).filter_by(
            platform_id=platform.id
        ).order_by(PostFormatKnowledge.average_engagement_rate.desc()).first()
    
    def get_viral_formats(self, platform_name: str) -> List[PostFormatKnowledge]:
        """Get formats with high viral potential."""
        platform = self.get_platform_by_name(platform_name)
        if not platform:
            return []
        
        return self.session.query(PostFormatKnowledge).filter(
            PostFormatKnowledge.platform_id == platform.id,
            PostFormatKnowledge.is_viral_format == True
        ).all()
    
    # ===== CONTENT PILLAR KNOWLEDGE =====
    
    def get_content_pillar(self, pillar_name: str) -> Optional[ContentPillarTemplate]:
        """Get content pillar template by name."""
        return self.session.query(ContentPillarTemplate).filter_by(pillar_name=pillar_name).first()
    
    def get_content_pillars_by_industry(self, industry: str) -> List[ContentPillarTemplate]:
        """Get recommended content pillars for an industry."""
        practice = self.session.query(IndustryBestPractice).filter_by(industry_name=industry).first()
        if not practice or not practice.top_content_pillars:
            return []
        
        pillars = []
        for pillar_name in practice.top_content_pillars:
            pillar = self.get_content_pillar(pillar_name)
            if pillar:
                pillars.append(pillar)
        return pillars
    
    def get_content_mix_by_industry(self, industry: str) -> Dict[str, float]:
        """Get recommended content mix percentages for industry."""
        practice = self.session.query(IndustryBestPractice).filter_by(industry_name=industry).first()
        if not practice:
            return {}
        
        mix = {}
        for pillar_name in practice.top_content_pillars:
            pillar = self.get_content_pillar(pillar_name)
            if pillar:
                mix[pillar_name] = pillar.recommended_weight_percentage
        return mix
    
    # ===== CTA & HOOK KNOWLEDGE =====
    
    def get_cta(self, cta_type: str) -> Optional[CTATemplate]:
        """Get CTA template by type."""
        return self.session.query(CTATemplate).filter_by(cta_type=cta_type).first()
    
    def get_best_cta_for_platform(self, platform_name: str, business_goal: str) -> Optional[CTATemplate]:
        """Get best CTA for platform and business goal."""
        return self.session.query(CTATemplate).filter(
            CTATemplate.works_best_with_platforms.contains(platform_name),
            CTATemplate.business_goal == business_goal
        ).order_by(CTATemplate.average_ctr.desc()).first()
    
    def get_hook(self, hook_name: str) -> Optional[HookTemplate]:
        """Get hook template by name."""
        return self.session.query(HookTemplate).filter_by(hook_name=hook_name).first()
    
    def get_best_hook_for_platform(self, platform_name: str) -> Optional[HookTemplate]:
        """Get highest-performing hook for platform."""
        return self.session.query(HookTemplate).filter(
            HookTemplate.works_best_with_platforms.contains(platform_name)
        ).order_by(HookTemplate.average_engagement_lift.desc()).first()
    
    def get_hooks_by_category(self, category: str) -> List[HookTemplate]:
        """Get hooks recommended for content category."""
        return self.session.query(HookTemplate).filter(
            HookTemplate.content_categories.contains(category)
        ).all()
    
    # ===== ENGAGEMENT TACTICS =====
    
    def get_engagement_tactic(self, tactic_name: str) -> Optional[EngagementTactic]:
        """Get engagement tactic by name."""
        return self.session.query(EngagementTactic).filter_by(tactic_name=tactic_name).first()
    
    def get_engagement_tactics_for_platform(self, platform_name: str) -> List[EngagementTactic]:
        """Get recommended engagement tactics for platform."""
        return self.session.query(EngagementTactic).filter(
            EngagementTactic.best_platforms.contains(platform_name)
        ).order_by(EngagementTactic.expected_engagement_rate_lift.desc()).all()
    
    def get_tactics_by_time_investment(self, max_hours: float) -> List[EngagementTactic]:
        """Get tactics that fit within time investment."""
        return self.session.query(EngagementTactic).filter(
            EngagementTactic.time_investment_hours <= max_hours
        ).order_by(EngagementTactic.expected_engagement_rate_lift.desc()).all()
    
    # ===== INFLUENCER KNOWLEDGE =====
    
    def get_influencer_tier(self, tier_name: str) -> Optional[InfluencerTierKnowledge]:
        """Get influencer tier characteristics."""
        return self.session.query(InfluencerTierKnowledge).filter_by(tier_name=tier_name).first()
    
    def get_influencer_tier_by_follower_count(self, follower_count: int) -> Optional[InfluencerTierKnowledge]:
        """Get influencer tier based on follower count."""
        return self.session.query(InfluencerTierKnowledge).filter(
            InfluencerTierKnowledge.follower_range_min <= follower_count,
            InfluencerTierKnowledge.follower_range_max >= follower_count
        ).first()
    
    # ===== INDUSTRY KNOWLEDGE =====
    
    def get_industry_practice(self, industry: str) -> Optional[IndustryBestPractice]:
        """Get industry best practices."""
        return self.session.query(IndustryBestPractice).filter_by(industry_name=industry).first()
    
    def get_platform_priority_for_industry(self, industry: str) -> List[Tuple[str, int]]:
        """Get platform priority ranking for industry."""
        practice = self.get_industry_practice(industry)
        if not practice:
            return []
        
        return [(p["platform"], p["priority"]) for p in practice.platform_priority_ranking]
    
    def get_best_posting_time_for_industry(self, industry: str) -> Optional[Dict]:
        """Get best posting times for industry."""
        practice = self.get_industry_practice(industry)
        return practice.best_posting_time if practice else None
    
    def get_engagement_benchmark(self, industry: str, platform: str, follower_range: str = None) -> Optional[EngagementBenchmark]:
        """Get engagement benchmarks for industry/platform."""
        query = self.session.query(EngagementBenchmark).filter_by(
            industry=industry,
            platform=platform
        )
        if follower_range:
            query = query.filter_by(follower_range=follower_range)
        return query.first()
    
    # ===== SEASONAL OPPORTUNITIES =====
    
    def get_seasonal_opportunities_by_industry(self, industry: str) -> List[SeasonalOpportunity]:
        """Get seasonal opportunities for industry."""
        return self.session.query(SeasonalOpportunity).filter(
            SeasonalOpportunity.industry.in_([industry, "all"])
        ).all()
    
    def get_current_seasonal_opportunity(self, industry: str, month_day: str) -> Optional[SeasonalOpportunity]:
        """Get current seasonal opportunity if any."""
        opportunities = self.get_seasonal_opportunities_by_industry(industry)
        for opp in opportunities:
            if month_day.startswith(opp.event_date[:5]):
                return opp
        return None
    
    # ===== BRAND SAFETY =====
    
    def get_brand_safety_guide(self, brand_type: str) -> Optional[BrandSafetyGuide]:
        """Get brand safety guidelines for brand type."""
        return self.session.query(BrandSafetyGuide).filter_by(brand_type=brand_type).first()
    
    # ===== CONTENT REPURPOSING =====
    
    def get_repurposing_strategy(self, source_platform: str, source_format: str, target_platform: str, target_format: str) -> Optional[ContentRepurposingStrategy]:
        """Get strategy for repurposing content across platforms."""
        return self.session.query(ContentRepurposingStrategy).filter_by(
            source_platform=source_platform,
            source_format=source_format,
            target_platform=target_platform,
            target_format=target_format
        ).first()
    
    # ===== SMART RECOMMENDATIONS =====
    
    def recommend_content_mix(self, industry: str, active_platforms: List[str]) -> Dict:
        """Recommend optimal content mix for industry and platforms."""
        practice = self.get_industry_practice(industry)
        if not practice:
            return {}
        
        recommendation = {
            "industry": industry,
            "platforms": active_platforms,
            "content_pillars": {},
            "platform_strategies": {},
            "posting_frequency": {},
            "expected_engagement": {}
        }
        
        # Content pillar mix
        for pillar_name in practice.top_content_pillars:
            pillar = self.get_content_pillar(pillar_name)
            if pillar:
                recommendation["content_pillars"][pillar_name] = {
                    "weight": pillar.recommended_weight_percentage,
                    "frequency_per_month": pillar.ideal_posting_frequency_per_month,
                    "formats": pillar.post_types
                }
        
        # Platform-specific strategies
        for platform in active_platforms:
            platform_obj = self.get_platform_by_name(platform)
            best_format = self.get_best_format_by_engagement(platform)
            cta = self.get_best_cta_for_platform(platform, "awareness")
            
            recommendation["platform_strategies"][platform] = {
                "posting_frequency": platform_obj.optimal_post_frequency_per_week if platform_obj else None,
                "best_format": best_format.format_name if best_format else None,
                "recommended_cta": cta.cta_type if cta else None,
                "posting_times": self.get_platform_best_posting_times(platform)
            }
        
        # Engagement benchmark
        benchmark = self.get_engagement_benchmark(industry, active_platforms[0] if active_platforms else "Instagram")
        if benchmark:
            recommendation["expected_engagement"]["benchmark_engagement_rate"] = benchmark.average_engagement_rate
            recommendation["expected_engagement"]["benchmark_conversion_rate"] = benchmark.conversion_rate
        
        return recommendation
    
    def suggest_viral_content_strategy(self, platform: str, industry: str) -> Dict:
        """Suggest viral content strategy for platform and industry."""
        best_hook = self.get_best_hook_for_platform(platform)
        viral_formats = self.get_viral_formats(platform)
        tactics = self.get_engagement_tactics_for_platform(platform)
        
        return {
            "platform": platform,
            "industry": industry,
            "viral_hook": best_hook.hook_pattern if best_hook else None,
            "viral_formats": [f.format_name for f in viral_formats],
            "engagement_tactics": [t.tactic_name for t in tactics[:3]],
            "expected_lift": best_hook.average_engagement_lift if best_hook else 0
        }
