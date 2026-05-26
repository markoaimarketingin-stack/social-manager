"""
Knowledge Base Schema and Models for Social Community Manager Agent.
This module defines the foundational knowledge that the agent uses to make decisions.
Includes platform rules, content strategies, engagement tactics, and best practices.
"""

from __future__ import annotations
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, DateTime, 
    Boolean, JSON, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from typing import List, Dict, Optional

Base = declarative_base()


# ===== PLATFORM KNOWLEDGE =====

class PlatformKnowledge(Base):
    """Platform-specific capabilities and best practices."""
    __tablename__ = "platform_knowledge"
    
    id = Column(Integer, primary_key=True)
    platform_name = Column(String, unique=True, nullable=False, index=True)  # Instagram, LinkedIn, X, YouTube, TikTok
    description = Column(Text)
    primary_audience_type = Column(String)  # B2C, B2B, B2B2C
    optimal_post_frequency_per_week = Column(Integer)
    max_caption_length = Column(Integer)
    supported_formats = Column(JSON)  # ["reel", "carousel", "story", ...]
    best_posting_times = Column(JSON)  # {day: [hours]}
    average_engagement_rate_benchmark = Column(Float)
    hashtag_recommendation_count = Column(Integer)
    algorithm_prefers_content_type = Column(String)  # "video", "carousel", "text", etc.
    native_analytics_available = Column(Boolean, default=True)
    allows_scheduling = Column(Boolean, default=True)
    allows_direct_messaging = Column(Boolean, default=True)
    video_length_limits = Column(JSON)  # {format: max_seconds}
    character_limits = Column(JSON)  # {field: limit}
    created_at = Column(DateTime, default=datetime.utcnow)
    
    post_format_knowledge = relationship("PostFormatKnowledge", back_populates="platform")
    platform_tone_patterns = relationship("PlatformTonePattern", back_populates="platform")


class PostFormatKnowledge(Base):
    """Post format capabilities and performance data."""
    __tablename__ = "post_format_knowledge"
    
    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey("platform_knowledge.id"), nullable=False, index=True)
    format_name = Column(String, nullable=False)  # reel, carousel, story, post, etc.
    average_engagement_rate = Column(Float)
    average_reach = Column(Integer)
    average_save_rate = Column(Float)
    average_share_rate = Column(Float)
    recommended_content_types = Column(JSON)  # ["educational", "entertaining", ...]
    recommended_length = Column(String)  # "15-60 seconds", "100-300 characters"
    max_file_size_mb = Column(Float)
    supported_file_types = Column(JSON)  # ["jpg", "mp4", "gif", ...]
    is_viral_format = Column(Boolean, default=False)
    requires_captions = Column(Boolean, default=False)
    allows_links = Column(Boolean, default=True)
    average_ctr = Column(Float)  # Click-through rate
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('platform_id', 'format_name', name='uix_platform_format'),)
    
    platform = relationship("PlatformKnowledge", back_populates="post_format_knowledge")


class PlatformTonePattern(Base):
    """Platform-specific tone and voice guidelines."""
    __tablename__ = "platform_tone_patterns"
    
    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey("platform_knowledge.id"), nullable=False, index=True)
    tone_type = Column(String, nullable=False)  # professional, casual, entertaining, educational
    recommended_language_style = Column(String)  # formal, conversational, slang-friendly
    emoji_frequency = Column(String)  # high, medium, low, none
    hashtag_best_practice = Column(String)
    average_caption_word_count = Column(Integer)
    include_question = Column(Boolean, default=True)
    personality_notes = Column(Text)
    example_good_captions = Column(JSON)  # {"caption": "...", "tone": "..."}
    created_at = Column(DateTime, default=datetime.utcnow)
    
    platform = relationship("PlatformKnowledge", back_populates="platform_tone_patterns")


# ===== CONTENT PILLAR KNOWLEDGE =====

class ContentPillarTemplate(Base):
    """Reusable content pillar frameworks."""
    __tablename__ = "content_pillar_templates"
    
    id = Column(Integer, primary_key=True)
    pillar_name = Column(String, nullable=False)  # Education, Entertainment, Behind-the-Scenes, etc.
    industry_category = Column(String, index=True)  # fitness, e-commerce, SaaS, etc.
    description = Column(Text)
    business_goal = Column(String)  # awareness, consideration, conversion, retention, advocacy
    recommended_weight_percentage = Column(Float)  # % of total content
    content_topics = Column(JSON)  # ["topic1", "topic2", ...]
    post_types = Column(JSON)  # ["carousel", "reel", "long_form", ...]
    
    cta_types_associated = Column(JSON)  # ["learn_more", "shop", ...]
    average_engagement_multiplier = Column(Float)  # relative engagement
    ideal_posting_frequency_per_month = Column(Integer)
    content_examples = Column(JSON)  # Examples for each platform
    hashtag_themes = Column(JSON)  # Themed hashtags to use
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== CTA & HOOK KNOWLEDGE =====

class CTATemplate(Base):
    """Call-to-Action templates and performance data."""
    __tablename__ = "cta_templates"
    
    id = Column(Integer, primary_key=True)
    cta_type = Column(String, unique=True, nullable=False)  # shop, learn_more, subscribe, etc.
    cta_text = Column(String)  # "Shop now", "Learn more"
    cta_description = Column(Text)
    business_goal = Column(String)  # awareness, consideration, conversion, retention
    average_ctr = Column(Float)  # Expected click-through rate
    works_best_with_content_types = Column(JSON)  # content types that work
    works_best_with_platforms = Column(JSON)
    expected_conversion_rate = Column(Float)
    variations = Column(JSON)  # ["Shop now", "Get Access", "Start Free Trial", ...]
    created_at = Column(DateTime, default=datetime.utcnow)


class HookTemplate(Base):
    """Viral hook formulas and patterns."""
    __tablename__ = "hook_templates"
    
    id = Column(Integer, primary_key=True)
    hook_name = Column(String, nullable=False)  # curiosity, benefit, controversy, etc.
    hook_pattern = Column(String)  # Template: "You didn't know [benefit]", etc.
    hook_description = Column(Text)
    average_engagement_lift = Column(Float)  # Expected engagement increase %
    works_best_with_platforms = Column(JSON)
    content_categories = Column(JSON)  # education, entertainment, product, etc.
    hook_examples = Column(JSON)  # Real examples
    psychology_principle = Column(String)  # What principle it uses: FOMO, curiosity, etc.
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== ENGAGEMENT TACTIC KNOWLEDGE =====

class EngagementTactic(Base):
    """Community engagement strategies and best practices."""
    __tablename__ = "engagement_tactics"
    
    id = Column(Integer, primary_key=True)
    tactic_name = Column(String, nullable=False)  # polls, live_sessions, Q&A, etc.
    tactic_description = Column(Text)
    expected_engagement_rate_lift = Column(Float)  # % increase in engagement
    best_platforms = Column(JSON)
    execution_steps = Column(JSON)  # How to execute
    timing_guidelines = Column(String)  # When to execute (daily, weekly, etc.)
    response_template = Column(Text)  # Template for responding
    best_performing_variations = Column(JSON)
    community_sentiment_impact = Column(String)  # positive, neutral, variable
    time_investment_hours = Column(Float)  # Average time needed
    created_at = Column(DateTime, default=datetime.utcnow)


class CommentResponseTemplate(Base):
    """Templates for responding to different comment types."""
    __tablename__ = "comment_response_templates"
    
    id = Column(Integer, primary_key=True)
    comment_type = Column(String)  # praise, question, concern, criticism, spam
    response_template = Column(Text)
    tone = Column(String)  # professional, friendly, empathetic, etc.
    should_tag_support = Column(Boolean, default=False)
    emoji_recommendation = Column(String)
    response_time_guideline = Column(String)  # "within 1 hour", "same day"
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== INFLUENCER KNOWLEDGE =====

class InfluencerTierKnowledge(Base):
    """Influencer tier characteristics and collaboration strategies."""
    __tablename__ = "influencer_tier_knowledge"
    
    id = Column(Integer, primary_key=True)
    tier_name = Column(String, unique=True, nullable=False)  # nano, micro, macro, mega
    follower_range_min = Column(Integer)
    follower_range_max = Column(Integer)
    average_engagement_rate = Column(Float)
    average_partnership_cost_range = Column(String)  # "$100-500", etc.
    collaboration_types = Column(JSON)  # sponsored_post, takeover, affiliate, etc.
    finding_strategy = Column(Text)
    outreach_approach = Column(String)  # direct_dm, email, manager, etc.
    contract_typical_terms = Column(JSON)
    expected_roi_multiplier = Column(Float)
    best_industries = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class CollaborationTypeKnowledge(Base):
    """Partnership types and performance metrics."""
    __tablename__ = "collaboration_type_knowledge"
    
    id = Column(Integer, primary_key=True)
    collaboration_type = Column(String, unique=True, nullable=False)  # sponsor, affiliate, giveaway, takeover, etc.
    description = Column(Text)
    average_reach_multiplier = Column(Float)
    average_engagement_rate = Column(Float)
    content_guidelines = Column(JSON)
    disclosure_requirements = Column(String)  # FTC guidelines, platform rules
    contract_duration = Column(String)  # "2-4 weeks", "1 month", etc.
    performance_metrics = Column(JSON)  # What to measure
    risk_factors = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== BRAND & BUSINESS KNOWLEDGE =====

class BrandArchetypeKnowledge(Base):
    """Brand archetypes and their characteristics."""
    __tablename__ = "brand_archetype_knowledge"
    
    id = Column(Integer, primary_key=True)
    archetype_name = Column(String, unique=True, nullable=False)  # Hero, Creator, Caregiver, Lover, Everyman, etc.
    core_values = Column(JSON)
    brand_personality_traits = Column(JSON)
    communication_style = Column(Text)
    typical_industries = Column(JSON)
    audience_psychology = Column(Text)
    content_pillars_aligned = Column(JSON)
    color_psychology = Column(JSON)
    icon_recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class IndustryBestPractice(Base):
    """Industry-specific best practices and benchmarks."""
    __tablename__ = "industry_best_practices"
    
    id = Column(Integer, primary_key=True)
    industry_name = Column(String, nullable=False, index=True)  # fitness, e-commerce, SaaS, etc.
    target_demographics = Column(JSON)
    platform_priority_ranking = Column(JSON)  # [{"platform": "Instagram", "priority": 1}, ...]
    content_length_preferences = Column(JSON)
    best_posting_time = Column(JSON)
    top_content_pillars = Column(JSON)
    engagement_benchmarks = Column(JSON)  # {"engagement_rate": 2.5, ...}
    conversion_benchmarks = Column(JSON)
    common_pain_points = Column(JSON)
    proven_growth_tactics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class AudiencePersonaTemplate(Base):
    """Audience persona templates."""
    __tablename__ = "audience_persona_templates"
    
    id = Column(Integer, primary_key=True)
    persona_name = Column(String, nullable=False)
    industry = Column(String)
    age_range = Column(String)
    primary_pain_points = Column(JSON)
    primary_aspirations = Column(JSON)
    buying_stage = Column(String)  # awareness, consideration, decision, retention, advocacy
    content_preferences = Column(JSON)  # Types they engage with
    trusted_information_sources = Column(JSON)
    preferred_platforms = Column(JSON)
    decision_making_criteria = Column(JSON)
    objections_to_address = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== UGC (USER-GENERATED CONTENT) KNOWLEDGE =====

class UGCCampaignTemplate(Base):
    """UGC campaign strategies and execution playbooks."""
    __tablename__ = "ugc_campaign_templates"
    
    id = Column(Integer, primary_key=True)
    campaign_name = Column(String, nullable=False)
    campaign_description = Column(Text)
    business_goal = Column(String)
    hashtag_strategy = Column(String)
    incentive_types = Column(JSON)  # discount, prize, recognition, exclusive_access
    submission_methods = Column(JSON)  # hashtag_tag, dm, url_form, email
    campaign_duration_days = Column(Integer)
    expected_submission_volume = Column(Integer)
    average_engagement_lift = Column(Float)
    repurposing_strategy = Column(JSON)  # How to use UGC in ads, stories, etc.
    moderation_guidelines = Column(JSON)
    legal_requirements = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== LOYALTY & RETENTION KNOWLEDGE =====

class LoyaltyStrategyKnowledge(Base):
    """Customer loyalty and retention program strategies."""
    __tablename__ = "loyalty_strategy_knowledge"
    
    id = Column(Integer, primary_key=True)
    strategy_type = Column(String)  # vip_tiers, referral, exclusive_content, badge_system, etc.
    strategy_description = Column(Text)
    expected_retention_lift = Column(Float)  # % increase in retention
    cost_to_implement = Column(String)  # low, medium, high
    best_for_business_stages = Column(JSON)  # early, growth, mature
    implementation_steps = Column(JSON)
    required_resources = Column(JSON)
    related_tactics = Column(JSON)
    success_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== ANALYTICS & BENCHMARKS =====

class EngagementBenchmark(Base):
    """Industry and platform-specific benchmarks."""
    __tablename__ = "engagement_benchmarks"
    
    id = Column(Integer, primary_key=True)
    industry = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    follower_range = Column(String)  # 0-10k, 10k-100k, etc.
    average_engagement_rate = Column(Float)
    average_save_rate = Column(Float)
    average_reach = Column(Integer)
    average_ctr = Column(Float)
    conversion_rate = Column(Float)
    seasonal_lift = Column(JSON)  # Seasonal engagement patterns
    data_last_updated = Column(DateTime)
    
    __table_args__ = (
        UniqueConstraint('industry', 'platform', 'follower_range', name='uix_industry_platform_range'),
    )


class OptimalPostingTime(Base):
    """Data on optimal posting times by platform/industry."""
    __tablename__ = "optimal_posting_times"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)
    industry = Column(String)
    day_of_week = Column(String)  # Monday, Tuesday, etc.
    best_hour = Column(Integer)  # 0-23
    engagement_expectation = Column(String)  # high, medium, low
    format_preference = Column(String)
    time_window_start = Column(Integer)  # hour start
    time_window_end = Column(Integer)  # hour end


# ===== DECISION RULES =====

class ContentDecisionRule(Base):
    """Rules for making content decisions."""
    __tablename__ = "content_decision_rules"
    
    id = Column(Integer, primary_key=True)
    rule_name = Column(String, nullable=False)
    condition = Column(String)  # "if engagement_rate < 2%", etc.
    recommended_action = Column(String)  # recommended_action
    priority_level = Column(Integer)  # 1 (highest), 2, 3
    applies_to_platforms = Column(JSON)
    applies_to_industries = Column(JSON)
    success_rate = Column(Float)  # Historical success rate
    created_at = Column(DateTime, default=datetime.utcnow)


class EngagementRule(Base):
    """Rules for engagement strategies."""
    __tablename__ = "engagement_rules"
    
    id = Column(Integer, primary_key=True)
    rule_name = Column(String, nullable=False)
    condition = Column(String)
    recommended_tactic = Column(String)
    tactic_timing = Column(String)  # When to execute
    priority_score = Column(Integer)
    applicable_industries = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== SEASONAL & TREND KNOWLEDGE =====

class SeasonalOpportunity(Base):
    """Seasonal opportunities and trends."""
    __tablename__ = "seasonal_opportunities"
    
    id = Column(Integer, primary_key=True)
    opportunity_name = Column(String, nullable=False)
    industry = Column(String)
    event_date = Column(String)  # ISO date or month pattern: "01-15" for Jan 15
    duration_days = Column(Integer)
    expected_engagement_lift = Column(Float)
    content_theme = Column(String)
    recommended_platforms = Column(JSON)
    campaign_playbook = Column(JSON)
    hashtags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== CONTENT MODERATION & BRAND SAFETY =====

class BrandSafetyGuide(Base):
    """Guidelines for maintaining brand safety and compliance."""
    __tablename__ = "brand_safety_guides"
    
    id = Column(Integer, primary_key=True)
    brand_type = Column(String, nullable=False)
    prohibited_topics = Column(JSON)
    required_disclosures = Column(JSON)
    compliance_requirements = Column(JSON)  # FTC, GDPR, etc.
    tone_guardrails = Column(JSON)
    sensitive_handling_guidelines = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== CONTENT REPURPOSING KNOWLEDGE =====

class ContentRepurposingStrategy(Base):
    """Strategies for repurposing content across platforms."""
    __tablename__ = "content_repurposing_strategies"
    
    id = Column(Integer, primary_key=True)
    source_platform = Column(String, nullable=False)
    source_format = Column(String)
    target_platform = Column(String, nullable=False)
    target_format = Column(String)
    adaptation_guidelines = Column(JSON)
    expected_performance_vs_original = Column(Float)  # % of original performance
    time_to_adapt = Column(String)  # "5 minutes", "15 minutes"
    created_at = Column(DateTime, default=datetime.utcnow)
