"""
Knowledge Base Seed Data and Initialization.
Populates the knowledge base with industry best practices, platform guidelines, and strategies.
"""

from datetime import datetime
from social_manager.knowledge_base_schema import (
    Base, PlatformKnowledge, PostFormatKnowledge, PlatformTonePattern,
    ContentPillarTemplate, CTATemplate, HookTemplate, EngagementTactic,
    CommentResponseTemplate, InfluencerTierKnowledge, CollaborationTypeKnowledge,
    BrandArchetypeKnowledge, IndustryBestPractice, AudiencePersonaTemplate,
    UGCCampaignTemplate, LoyaltyStrategyKnowledge, EngagementBenchmark,
    OptimalPostingTime, ContentDecisionRule, EngagementRule,
    SeasonalOpportunity, BrandSafetyGuide, ContentRepurposingStrategy
)
from sqlalchemy.orm import Session


def seed_platform_knowledge(session: Session):
    """Seed platform-specific knowledge."""
    platforms = [
        {
            "platform_name": "Instagram",
            "description": "Visual-first platform for B2C brands. Strong for lifestyle, beauty, fitness.",
            "primary_audience_type": "B2C",
            "optimal_post_frequency_per_week": 5,
            "max_caption_length": 2200,
            "supported_formats": ["reel", "carousel", "single", "story", "video", "igtv"],
            "best_posting_times": {"Monday": [9, 11, 19], "Tuesday": [9, 11, 19], "Wednesday": [9, 11, 19], "Thursday": [9, 11, 19], "Friday": [9, 11, 17], "Saturday": [10, 18], "Sunday": [10, 18]},
            "average_engagement_rate_benchmark": 3.5,
            "hashtag_recommendation_count": 30,
            "algorithm_prefers_content_type": "video",
            "native_analytics_available": True,
            "allows_scheduling": True,
            "allows_direct_messaging": True,
            "video_length_limits": {"reel": 90, "story": 15, "igtv": 3600},
            "character_limits": {"caption": 2200, "comment": 1000},
        },
        {
            "platform_name": "LinkedIn",
            "description": "Professional network for B2B content, thought leadership, and recruitment.",
            "primary_audience_type": "B2B",
            "optimal_post_frequency_per_week": 3,
            "max_caption_length": 3000,
            "supported_formats": ["text", "image", "doc", "video", "carousel"],
            "best_posting_times": {"Monday": [8, 10, 12], "Tuesday": [8, 10, 12], "Wednesday": [8, 10, 12], "Thursday": [8, 10, 12], "Friday": [8, 10, 12]},
            "average_engagement_rate_benchmark": 1.8,
            "hashtag_recommendation_count": 10,
            "algorithm_prefers_content_type": "text",
            "native_analytics_available": True,
            "allows_scheduling": True,
            "allows_direct_messaging": True,
            "video_length_limits": {"video": 10800},
            "character_limits": {"post": 3000, "comment": 2000},
        },
        {
            "platform_name": "X (Twitter)",
            "description": "Real-time conversation platform for news, updates, engagement.",
            "primary_audience_type": "B2B/B2C",
            "optimal_post_frequency_per_week": 7,
            "max_caption_length": 280,
            "supported_formats": ["tweet", "thread", "image", "video", "gif"],
            "best_posting_times": {"Monday": [9, 12, 17], "Tuesday": [9, 12, 17], "Wednesday": [9, 12, 17], "Thursday": [9, 12, 17], "Friday": [9, 12, 17]},
            "average_engagement_rate_benchmark": 1.2,
            "hashtag_recommendation_count": 3,
            "algorithm_prefers_content_type": "engagement",
            "native_analytics_available": True,
            "allows_scheduling": True,
            "allows_direct_messaging": True,
            "video_length_limits": {"video": 2048},
            "character_limits": {"tweet": 280, "thread": 35000},
        },
        {
            "platform_name": "YouTube",
            "description": "Long-form video platform for tutorials, vlogs, and detailed content.",
            "primary_audience_type": "B2C",
            "optimal_post_frequency_per_week": 2,
            "max_caption_length": 5000,
            "supported_formats": ["long", "short", "premiere", "live"],
            "best_posting_times": {"Tuesday": [18], "Wednesday": [18], "Thursday": [18], "Friday": [14], "Saturday": [14], "Sunday": [14]},
            "average_engagement_rate_benchmark": 5.2,
            "hashtag_recommendation_count": 10,
            "algorithm_prefers_content_type": "watch_time",
            "native_analytics_available": True,
            "allows_scheduling": True,
            "allows_direct_messaging": False,
            "video_length_limits": {"short": 60, "long": 720000},
            "character_limits": {"title": 100, "description": 5000},
        },
        {
            "platform_name": "TikTok",
            "description": "Short-form video platform for Gen Z, highly viral potential.",
            "primary_audience_type": "B2C",
            "optimal_post_frequency_per_week": 7,
            "max_caption_length": 2200,
            "supported_formats": ["video", "duet", "stitch", "green_screen"],
            "best_posting_times": {"Monday": [6, 10, 19], "Tuesday": [6, 10, 19], "Wednesday": [6, 10, 19], "Thursday": [6, 10, 19], "Friday": [6, 10, 19], "Saturday": [11, 19], "Sunday": [11, 19]},
            "average_engagement_rate_benchmark": 7.5,
            "hashtag_recommendation_count": 8,
            "algorithm_prefers_content_type": "watch_time",
            "native_analytics_available": True,
            "allows_scheduling": False,
            "allows_direct_messaging": True,
            "video_length_limits": {"video": 600},
            "character_limits": {"caption": 2200, "comment": 1024},
        }
    ]
    
    for platform_data in platforms:
        existing = session.query(PlatformKnowledge).filter_by(platform_name=platform_data["platform_name"]).first()
        if not existing:
            platform = PlatformKnowledge(**platform_data)
            session.add(platform)
    
    session.commit()


def seed_post_format_knowledge(session: Session):
    """Seed post format performance data."""
    formats = [
        # Instagram Formats
        {"platform_name": "Instagram", "format_name": "reel", "average_engagement_rate": 5.2, "average_reach": 45000, "average_save_rate": 12, "average_share_rate": 8, "recommended_content_types": ["educational", "entertaining", "motivational"], "recommended_length": "15-60 seconds", "max_file_size_mb": 4.0, "supported_file_types": ["mp4", "mov"], "is_viral_format": True, "requires_captions": True, "allows_links": False, "average_ctr": 2.3},
        {"platform_name": "Instagram", "format_name": "carousel", "average_engagement_rate": 3.8, "average_reach": 30000, "average_save_rate": 18, "average_share_rate": 5, "recommended_content_types": ["educational", "how-to", "comparison"], "recommended_length": "3-10 images", "max_file_size_mb": 8.0, "supported_file_types": ["jpg", "png"], "is_viral_format": False, "requires_captions": True, "allows_links": False, "average_ctr": 1.8},
        {"platform_name": "Instagram", "format_name": "single", "average_engagement_rate": 2.5, "average_reach": 20000, "average_save_rate": 15, "average_share_rate": 3, "recommended_content_types": ["lifestyle", "product", "quote"], "recommended_length": "100-300 characters", "max_file_size_mb": 8.0, "supported_file_types": ["jpg", "png"], "is_viral_format": False, "requires_captions": True, "allows_links": False, "average_ctr": 1.2},
        {"platform_name": "Instagram", "format_name": "story", "average_engagement_rate": 4.0, "average_reach": 25000, "average_save_rate": 8, "average_share_rate": 12, "recommended_content_types": ["behind-the-scenes", "polls", "quick-tips"], "recommended_length": "5-15 seconds", "max_file_size_mb": 100.0, "supported_file_types": ["jpg", "mp4"], "is_viral_format": False, "requires_captions": False, "allows_links": True, "average_ctr": 3.5},
        
        # LinkedIn Formats
        {"platform_name": "LinkedIn", "format_name": "text", "average_engagement_rate": 2.1, "average_reach": 15000, "average_save_rate": 5, "average_share_rate": 4, "recommended_content_types": ["thought_leadership", "insights", "industry_news"], "recommended_length": "150-500 words", "max_file_size_mb": 0, "supported_file_types": [], "is_viral_format": False, "requires_captions": False, "allows_links": True, "average_ctr": 1.5},
        {"platform_name": "LinkedIn", "format_name": "document", "average_engagement_rate": 3.5, "average_reach": 25000, "average_save_rate": 22, "average_share_rate": 8, "recommended_content_types": ["whitepaper", "ebook", "report"], "recommended_length": "5-50 pages", "max_file_size_mb": 10.0, "supported_file_types": ["pdf"], "is_viral_format": False, "requires_captions": False, "allows_links": False, "average_ctr": 2.8},
        {"platform_name": "LinkedIn", "format_name": "video", "average_engagement_rate": 4.2, "average_reach": 35000, "average_save_rate": 12, "average_share_rate": 7, "recommended_content_types": ["testimonial", "tutorial", "announcement"], "recommended_length": "30-90 seconds", "max_file_size_mb": 5.0, "supported_file_types": ["mp4", "mov"], "is_viral_format": True, "requires_captions": True, "allows_links": False, "average_ctr": 2.1},
        
        # X (Twitter) Formats
        {"platform_name": "X (Twitter)", "format_name": "tweet", "average_engagement_rate": 1.5, "average_reach": 10000, "average_save_rate": 2, "average_share_rate": 3, "recommended_content_types": ["hot_take", "announcement", "response"], "recommended_length": "280 characters", "max_file_size_mb": 0, "supported_file_types": [], "is_viral_format": False, "requires_captions": False, "allows_links": True, "average_ctr": 2.0},
        {"platform_name": "X (Twitter)", "format_name": "thread", "average_engagement_rate": 3.2, "average_reach": 35000, "average_save_rate": 8, "average_share_rate": 15, "recommended_content_types": ["educational", "breakdown", "story"], "recommended_length": "5-15 tweets", "max_file_size_mb": 0, "supported_file_types": [], "is_viral_format": True, "requires_captions": False, "allows_links": True, "average_ctr": 3.5},
        {"platform_name": "X (Twitter)", "format_name": "image", "average_engagement_rate": 2.8, "average_reach": 22000, "average_save_rate": 5, "average_share_rate": 8, "recommended_content_types": ["data_viz", "meme", "screenshot"], "recommended_length": "1200x675px", "max_file_size_mb": 5.0, "supported_file_types": ["jpg", "png", "gif"], "is_viral_format": False, "requires_captions": True, "allows_links": False, "average_ctr": 2.2},
        
        # YouTube Formats
        {"platform_name": "YouTube", "format_name": "long", "average_engagement_rate": 6.5, "average_reach": 100000, "average_save_rate": 20, "average_share_rate": 5, "recommended_content_types": ["tutorial", "vlog", "deep_dive"], "recommended_length": "10-45 minutes", "max_file_size_mb": 256.0, "supported_file_types": ["mp4", "mov"], "is_viral_format": False, "requires_captions": True, "allows_links": True, "average_ctr": 4.2},
        {"platform_name": "YouTube", "format_name": "short", "average_engagement_rate": 8.2, "average_reach": 80000, "average_save_rate": 15, "average_share_rate": 12, "recommended_content_types": ["entertaining", "trending", "quick_tip"], "recommended_length": "15-60 seconds", "max_file_size_mb": 256.0, "supported_file_types": ["mp4", "mov"], "is_viral_format": True, "requires_captions": True, "allows_links": False, "average_ctr": 5.8},
        
        # TikTok Formats
        {"platform_name": "TikTok", "format_name": "video", "average_engagement_rate": 9.5, "average_reach": 150000, "average_save_rate": 18, "average_share_rate": 22, "recommended_content_types": ["trending", "dance", "quick_tip", "challenge"], "recommended_length": "15-60 seconds", "max_file_size_mb": 287.6, "supported_file_types": ["mp4", "mov"], "is_viral_format": True, "requires_captions": True, "allows_links": False, "average_ctr": 6.5},
    ]
    
    for format_data in formats:
        platform = session.query(PlatformKnowledge).filter_by(platform_name=format_data.pop("platform_name")).first()
        if platform:
            existing = session.query(PostFormatKnowledge).filter_by(platform_id=platform.id, format_name=format_data["format_name"]).first()
            if not existing:
                format_obj = PostFormatKnowledge(platform_id=platform.id, **format_data)
                session.add(format_obj)
    
    session.commit()


def seed_content_pillar_templates(session: Session):
    """Seed content pillar templates."""
    pillars = [
        {
            "pillar_name": "Educational",
            "industry_category": "all",
            "description": "Value-driven content that teaches audience something new.",
            "business_goal": "awareness",
            "recommended_weight_percentage": 35,
            "content_topics": ["how-to", "tips", "tutorials", "guides", "industry_trends", "statistics"],
            "post_types": ["carousel", "reel", "text", "video", "document"],
            "cta_types_associated": ["learn_more", "download", "subscribe"],
            "average_engagement_multiplier": 1.8,
            "ideal_posting_frequency_per_month": 12,
            "hashtag_themes": ["#HowTo", "#Tips", "#Tutorial", "#Learning"],
        },
        {
            "pillar_name": "Entertainment",
            "industry_category": "all",
            "description": "Entertaining content that brings joy and keeps audience engaged.",
            "business_goal": "awareness",
            "recommended_weight_percentage": 25,
            "content_topics": ["memes", "trending", "funny", "relatable", "challenges", "behind_the_scenes"],
            "post_types": ["reel", "video", "story", "tweet", "short"],
            "cta_types_associated": ["engage", "share"],
            "average_engagement_multiplier": 2.1,
            "ideal_posting_frequency_per_month": 10,
            "hashtag_themes": ["#FYP", "#Viral", "#Trending", "#Entertainment"],
        },
        {
            "pillar_name": "Behind-the-Scenes",
            "industry_category": "all",
            "description": "Authentic content showing team, process, culture.",
            "business_goal": "consideration",
            "recommended_weight_percentage": 15,
            "content_topics": ["team", "culture", "process", "day_in_life", "office", "production"],
            "post_types": ["story", "reel", "video", "carousel"],
            "cta_types_associated": ["follow", "engage"],
            "average_engagement_multiplier": 1.6,
            "ideal_posting_frequency_per_month": 6,
            "hashtag_themes": ["#BehindTheScenes", "#TeamCulture", "#DayInMyLife"],
        },
        {
            "pillar_name": "Product/Service",
            "industry_category": "e-commerce",
            "description": "Direct product or service promotion and features.",
            "business_goal": "conversion",
            "recommended_weight_percentage": 15,
            "content_topics": ["product_launch", "features", "benefits", "pricing", "unboxing", "demo"],
            "post_types": ["carousel", "reel", "single", "video"],
            "cta_types_associated": ["shop", "buy_now", "sign_up"],
            "average_engagement_multiplier": 1.3,
            "ideal_posting_frequency_per_month": 8,
            "hashtag_themes": ["#ProductLaunch", "#NewProduct", "#ShopNow"],
        },
        {
            "pillar_name": "Customer Stories",
            "industry_category": "all",
            "description": "Testimonials, case studies, and success stories.",
            "business_goal": "consideration",
            "recommended_weight_percentage": 10,
            "content_topics": ["testimonial", "case_study", "success_story", "transformation", "review"],
            "post_types": ["carousel", "reel", "video", "text"],
            "cta_types_associated": ["learn_more", "join"],
            "average_engagement_multiplier": 1.9,
            "ideal_posting_frequency_per_month": 4,
            "hashtag_themes": ["#CaseStudy", "#SuccessStory", "#CustomerLove"],
        },
        {
            "pillar_name": "Thought Leadership",
            "industry_category": "B2B",
            "description": "Expert opinions, insights, and industry perspectives.",
            "business_goal": "consideration",
            "recommended_weight_percentage": 30,
            "content_topics": ["opinion", "industry_insight", "trend", "prediction", "advice"],
            "post_types": ["text", "video", "document", "carousel"],
            "cta_types_associated": ["engage", "connect"],
            "average_engagement_multiplier": 2.2,
            "ideal_posting_frequency_per_month": 8,
            "hashtag_themes": ["#ThoughtLeadership", "#IndustryInsights", "#Expert"],
        },
    ]
    
    for pillar_data in pillars:
        existing = session.query(ContentPillarTemplate).filter_by(pillar_name=pillar_data["pillar_name"]).first()
        if not existing:
            pillar = ContentPillarTemplate(**pillar_data)
            session.add(pillar)
    
    session.commit()


def seed_cta_templates(session: Session):
    """Seed CTA templates."""
    ctas = [
        {
            "cta_type": "shop",
            "cta_text": "Shop Now",
            "cta_description": "Direct product purchase CTA",
            "business_goal": "conversion",
            "average_ctr": 4.2,
            "works_best_with_content_types": ["product", "carousel", "promotion"],
            "works_best_with_platforms": ["Instagram", "TikTok", "Facebook"],
            "expected_conversion_rate": 3.5,
            "variations": ["Shop Now", "Get Access", "Buy Today", "Claim Yours", "Order Now"],
        },
        {
            "cta_type": "learn_more",
            "cta_text": "Learn More",
            "cta_description": "Drive to blog, article, or detailed resource",
            "business_goal": "awareness",
            "average_ctr": 3.8,
            "works_best_with_content_types": ["educational", "how-to", "blog"],
            "works_best_with_platforms": ["LinkedIn", "Instagram", "YouTube"],
            "expected_conversion_rate": 2.1,
            "variations": ["Learn More", "Read Article", "Discover", "Explore", "Find Out"],
        },
        {
            "cta_type": "subscribe",
            "cta_text": "Subscribe",
            "cta_description": "Subscribe to newsletter, channel, or updates",
            "business_goal": "retention",
            "average_ctr": 3.2,
            "works_best_with_content_types": ["educational", "tips", "tutorial"],
            "works_best_with_platforms": ["YouTube", "LinkedIn", "Email"],
            "expected_conversion_rate": 4.5,
            "variations": ["Subscribe", "Join", "Sign Up", "Get Updates", "Follow"],
        },
        {
            "cta_type": "engage",
            "cta_text": "Comment Your Thoughts",
            "cta_description": "Drive comments and conversation",
            "business_goal": "awareness",
            "average_ctr": 5.8,
            "works_best_with_content_types": ["question", "poll", "opinion"],
            "works_best_with_platforms": ["Instagram", "TikTok", "X"],
            "expected_conversion_rate": 8.2,
            "variations": ["Comment", "Drop a Comment", "Reply Below", "Tell Us", "Let Me Know"],
        },
        {
            "cta_type": "share",
            "cta_text": "Share This",
            "cta_description": "Encourage sharing to expand reach",
            "business_goal": "awareness",
            "average_ctr": 4.5,
            "works_best_with_content_types": ["viral", "inspirational", "trending"],
            "works_best_with_platforms": ["TikTok", "Instagram", "X"],
            "expected_conversion_rate": 12.0,
            "variations": ["Share", "Pass It On", "Send to Friend", "Share with Someone"],
        },
    ]
    
    for cta_data in ctas:
        existing = session.query(CTATemplate).filter_by(cta_type=cta_data["cta_type"]).first()
        if not existing:
            cta = CTATemplate(**cta_data)
            session.add(cta)
    
    session.commit()


def seed_hook_templates(session: Session):
    """Seed hook templates for viral content."""
    hooks = [
        {
            "hook_name": "Curiosity Gap",
            "hook_pattern": 'You\'ve been doing [common action] wrong your entire life. Here\'s how...',
            "hook_description": "Creates open loop that viewer wants to close.",
            "average_engagement_lift": 45,
            "works_best_with_platforms": ["Instagram", "TikTok", "YouTube"],
            "content_categories": ["tutorial", "how-to", "tip"],
            "psychology_principle": "Curiosity",
            "hook_examples": ["You've been thinking about productivity wrong", "This productivity hack will blow your mind"],
        },
        {
            "hook_name": "Benefit Hook",
            "hook_pattern": "Save [time/money/effort] by doing [action]",
            "hook_description": "Leads with concrete benefit of watching.",
            "average_engagement_lift": 35,
            "works_best_with_platforms": ["Instagram", "LinkedIn", "TikTok"],
            "content_categories": ["tutorial", "tip", "hack"],
            "psychology_principle": "Desire for gain",
            "hook_examples": ["Save 5 hours per week with this", "Cut your expenses in half doing this"],
        },
        {
            "hook_name": "Pattern Interrupt",
            "hook_pattern": "Something unexpected/surprising that stops the scroll",
            "hook_description": "Visual or statement that breaks pattern of feed.",
            "average_engagement_lift": 55,
            "works_best_with_platforms": ["TikTok", "Instagram", "X"],
            "content_categories": ["entertainment", "trending", "meme"],
            "psychology_principle": "Novelty",
            "hook_examples": ["Wait for the plot twist", "You won't believe what happened next"],
        },
        {
            "hook_name": "Question Hook",
            "hook_pattern": "[Question that viewer relates to]?",
            "hook_description": "Poses relatable question to engage viewer.",
            "average_engagement_lift": 40,
            "works_best_with_platforms": ["Instagram", "X", "LinkedIn"],
            "content_categories": ["relatable", "engagement", "poll"],
            "psychology_principle": "Engagement & belonging",
            "hook_examples": ["Ever felt like you're not productive enough?", "Struggling with inbox overload?"],
        },
        {
            "hook_name": "Controversy Hook",
            "hook_pattern": "[Debatable opinion] and here's why",
            "hook_description": "Takes a stance that invites discussion.",
            "average_engagement_lift": 60,
            "works_best_with_platforms": ["X", "LinkedIn", "YouTube"],
            "content_categories": ["opinion", "thought_leadership", "hot_take"],
            "psychology_principle": "FOMO & debate",
            "hook_examples": ["This productivity method is actually useless", "You don't need a fancy planner"],
        },
    ]
    
    for hook_data in hooks:
        existing = session.query(HookTemplate).filter_by(hook_name=hook_data["hook_name"]).first()
        if not existing:
            hook = HookTemplate(**hook_data)
            session.add(hook)
    
    session.commit()


def seed_engagement_tactics(session: Session):
    """Seed engagement tactics."""
    tactics = [
        {
            "tactic_name": "Polls & Voting",
            "tactic_description": "Post polls or voting questions to increase engagement.",
            "expected_engagement_rate_lift": 35,
            "best_platforms": ["Instagram", "TikTok", "X"],
            "execution_steps": ["Create clear question with 2-4 options", "Post poll sticker/feature", "Respond to results"],
            "timing_guidelines": "2-3 times per week",
            "response_template": "Thanks for voting! [Interesting insight about results]",
            "best_performing_variations": ["product decisions", "personal preferences", "hot takes"],
            "community_sentiment_impact": "positive",
            "time_investment_hours": 0.5,
        },
        {
            "tactic_name": "Ask Me Anything (AMA)",
            "tactic_description": "Host AMA session to directly engage with audience.",
            "expected_engagement_rate_lift": 50,
            "best_platforms": ["Instagram", "Reddit", "LinkedIn"],
            "execution_steps": ["Announce AMA time", "Enable stories/comments", "Answer questions live", "Follow up with collage"],
            "timing_guidelines": "Monthly",
            "response_template": "Great question! [Detailed answer with value]",
            "best_performing_variations": ["career", "business", "personal_story"],
            "community_sentiment_impact": "positive",
            "time_investment_hours": 2,
        },
        {
            "tactic_name": "User-Generated Content Campaign",
            "tactic_description": "Encourage audience to create content with branded hashtag.",
            "expected_engagement_rate_lift": 65,
            "best_platforms": ["Instagram", "TikTok", "YouTube"],
            "execution_steps": ["Create branded hashtag", "Post call to action", "Repost best submissions", "Reward participants"],
            "timing_guidelines": "Monthly campaign",
            "response_template": "Amazing submission! We're featuring this 🎉",
            "best_performing_variations": ["before & after", "transformation", "challenge"],
            "community_sentiment_impact": "positive",
            "time_investment_hours": 5,
        },
        {
            "tactic_name": "Live Sessions",
            "tactic_description": "Host live streams or live video sessions.",
            "expected_engagement_rate_lift": 45,
            "best_platforms": ["Instagram", "YouTube", "TikTok"],
            "execution_steps": ["Announce live session", "Go live with value", "Respond to comments", "Post highlight after"],
            "timing_guidelines": "Weekly",
            "response_template": "Thanks for joining! Here are key takeaways: [...]",
            "best_performing_variations": ["training", "Q&A", "behind the scenes"],
            "community_sentiment_impact": "positive",
            "time_investment_hours": 2,
        },
        {
            "tactic_name": "Comment Engagement",
            "tactic_description": "Reply to every comment with thoughtful responses.",
            "expected_engagement_rate_lift": 25,
            "best_platforms": ["Instagram", "YouTube", "X"],
            "execution_steps": ["Post content", "Wait 30 minutes for comments", "Respond to each comment", "Ask follow-up question"],
            "timing_guidelines": "For every post",
            "response_template": "[Address by name] - Great question! [Personalized answer]",
            "best_performing_variations": ["questions", "acknowledgments", "emoji responses"],
            "community_sentiment_impact": "positive",
            "time_investment_hours": 1,
        },
    ]
    
    for tactic_data in tactics:
        existing = session.query(EngagementTactic).filter_by(tactic_name=tactic_data["tactic_name"]).first()
        if not existing:
            tactic = EngagementTactic(**tactic_data)
            session.add(tactic)
    
    session.commit()


def seed_influencer_tier_knowledge(session: Session):
    """Seed influencer tier characteristics."""
    tiers = [
        {
            "tier_name": "nano",
            "follower_range_min": 1000,
            "follower_range_max": 10000,
            "average_engagement_rate": 8.5,
            "average_partnership_cost_range": "$100-500",
            "collaboration_types": ["sponsored_post", "product_seeding", "affiliate"],
            "finding_strategy": "Search hashtags, use tagging tools",
            "outreach_approach": "Direct DM",
            "contract_typical_terms": ["1 post minimum", "DM outreach", "Flexible"],
            "expected_roi_multiplier": 2.5,
            "best_industries": ["niche", "local", "authentic"],
        },
        {
            "tier_name": "micro",
            "follower_range_min": 10000,
            "follower_range_max": 100000,
            "average_engagement_rate": 4.2,
            "average_partnership_cost_range": "$500-5000",
            "collaboration_types": ["sponsored_post", "affiliate", "ambassador"],
            "finding_strategy": "Instagram search, influencer databases",
            "outreach_approach": "DM or email",
            "contract_typical_terms": ["3-6 posts", "Contract agreement", "Media assets provided"],
            "expected_roi_multiplier": 3.0,
            "best_industries": ["lifestyle", "beauty", "fitness", "niche"],
        },
        {
            "tier_name": "macro",
            "follower_range_min": 100000,
            "follower_range_max": 1000000,
            "average_engagement_rate": 2.1,
            "average_partnership_cost_range": "$5000-50000",
            "collaboration_types": ["sponsored_post", "campaigns", "brand_ambassador"],
            "finding_strategy": "Influencer agencies, verified search",
            "outreach_approach": "Agent/manager or email",
            "contract_typical_terms": ["Campaign brief", "Formal contract", "Performance metrics"],
            "expected_roi_multiplier": 4.0,
            "best_industries": ["mainstream", "fashion", "fitness", "lifestyle"],
        },
        {
            "tier_name": "mega",
            "follower_range_min": 1000000,
            "follower_range_max": 100000000,
            "average_engagement_rate": 1.2,
            "average_partnership_cost_range": "$50000+",
            "collaboration_types": ["brand_partnership", "campaign", "exclusive_deal"],
            "finding_strategy": "Top charts, awards, PR contacts",
            "outreach_approach": "Agent/manager, PR firm",
            "contract_typical_terms": ["Campaign contract", "Creative approval", "Long-term deals"],
            "expected_roi_multiplier": 3.5,
            "best_industries": ["mainstream", "entertainment", "luxury", "tech"],
        },
    ]
    
    for tier_data in tiers:
        existing = session.query(InfluencerTierKnowledge).filter_by(tier_name=tier_data["tier_name"]).first()
        if not existing:
            tier = InfluencerTierKnowledge(**tier_data)
            session.add(tier)
    
    session.commit()


def seed_industry_best_practices(session: Session):
    """Seed industry-specific best practices."""
    industries = [
        {
            "industry_name": "Fitness & Wellness",
            "target_demographics": ["18-35", "health_conscious", "active"],
            "platform_priority_ranking": [{"platform": "Instagram", "priority": 1}, {"platform": "TikTok", "priority": 2}, {"platform": "YouTube", "priority": 3}],
            "content_length_preferences": ["short_form", "medium_form"],
            "best_posting_time": {"Monday": 6, "Tuesday": 6, "Wednesday": 6, "Thursday": 6, "Friday": 6, "Saturday": 10},
            "top_content_pillars": ["transformation", "tips", "education", "motivation", "product"],
            "engagement_benchmarks": {"engagement_rate": 4.5, "ctr": 3.2, "conversion_rate": 2.8},
            "conversion_benchmarks": {"from_bio_link": 2.5, "from_story_link": 3.8},
            "common_pain_points": ["motivation", "consistency", "knowledge_gaps"],
            "proven_growth_tactics": ["before_after_transformation", "challenge_campaigns", "partner_with_nutritionists"],
        },
        {
            "industry_name": "E-Commerce",
            "target_demographics": ["18-55", "shoppers", "lifestyle"],
            "platform_priority_ranking": [{"platform": "Instagram", "priority": 1}, {"platform": "TikTok", "priority": 2}, {"platform": "Pinterest", "priority": 3}],
            "content_length_preferences": ["short_form", "carousel"],
            "best_posting_time": {"Tuesday": 12, "Wednesday": 12, "Thursday": 12, "Friday": 18},
            "top_content_pillars": ["product", "lifestyle", "customer_stories", "entertainment"],
            "engagement_benchmarks": {"engagement_rate": 2.8, "ctr": 4.5, "conversion_rate": 1.8},
            "conversion_benchmarks": {"from_link": 2.2, "from_story": 3.5},
            "common_pain_points": ["product_discovery", "trust", "shipping_concerns"],
            "proven_growth_tactics": ["user_generated_content", "influencer_collab", "flash_sales", "limited_drops"],
        },
        {
            "industry_name": "B2B SaaS",
            "target_demographics": ["25-55", "decision_makers", "professionals"],
            "platform_priority_ranking": [{"platform": "LinkedIn", "priority": 1}, {"platform": "X", "priority": 2}, {"platform": "YouTube", "priority": 3}],
            "content_length_preferences": ["long_form", "educational", "thought_leadership"],
            "best_posting_time": {"Monday": 8, "Tuesday": 8, "Wednesday": 8, "Thursday": 8, "Friday": 8},
            "top_content_pillars": ["thought_leadership", "education", "product", "company_culture"],
            "engagement_benchmarks": {"engagement_rate": 2.1, "ctr": 2.8, "conversion_rate": 0.8},
            "conversion_benchmarks": {"from_demo_link": 1.5, "from_webinar": 3.2},
            "common_pain_points": ["solution_discovery", "trust", "roi_proof"],
            "proven_growth_tactics": ["webinars", "case_studies", "product_videos", "thought_leadership"],
        },
    ]
    
    for industry_data in industries:
        existing = session.query(IndustryBestPractice).filter_by(industry_name=industry_data["industry_name"]).first()
        if not existing:
            industry = IndustryBestPractice(**industry_data)
            session.add(industry)
    
    session.commit()


def seed_seasonal_opportunities(session: Session):
    """Seed seasonal opportunities."""
    opportunities = [
        {
            "opportunity_name": "New Year Resolution",
            "industry": "all",
            "event_date": "01-01",
            "duration_days": 31,
            "expected_engagement_lift": 40,
            "content_theme": "goals, transformation, motivation",
            "recommended_platforms": ["Instagram", "TikTok", "YouTube"],
            "campaign_playbook": ["Transformation challenge", "Goal-setting content", "Accountability groups"],
            "hashtags": ["#NewYearNewMe", "#2026Goals", "#Resolution"],
        },
        {
            "opportunity_name": "Back to School",
            "industry": "education, e-commerce",
            "event_date": "08-01",
            "duration_days": 30,
            "expected_engagement_lift": 35,
            "content_theme": "preparation, supplies, tips",
            "recommended_platforms": ["Instagram", "TikTok"],
            "campaign_playbook": ["Haul videos", "Organization tips", "Product features"],
            "hashtags": ["#BackToSchool", "#SchoolPrep", "#StudentLife"],
        },
        {
            "opportunity_name": "Black Friday / Cyber Monday",
            "industry": "e-commerce",
            "event_date": "11-28",
            "duration_days": 10,
            "expected_engagement_lift": 65,
            "content_theme": "deals, scarcity, urgency",
            "recommended_platforms": ["Instagram", "TikTok", "Email"],
            "campaign_playbook": ["Countdown posts", "Deal reveals", "Exclusive access early"],
            "hashtags": ["#BlackFriday", "#CyberMonday", "#DealAlert"],
        },
        {
            "opportunity_name": "Holiday Season",
            "industry": "all",
            "event_date": "11-01",
            "duration_days": 60,
            "expected_engagement_lift": 50,
            "content_theme": "giving, celebration, family",
            "recommended_platforms": ["Instagram", "YouTube", "TikTok"],
            "campaign_playbook": ["Gift guides", "Holiday tutorials", "Festive content"],
            "hashtags": ["#HolidaySeason", "#GiftGuide", "#FestiveVibes"],
        },
    ]
    
    for opp_data in opportunities:
        existing = session.query(SeasonalOpportunity).filter_by(opportunity_name=opp_data["opportunity_name"]).first()
        if not existing:
            opp = SeasonalOpportunity(**opp_data)
            session.add(opp)
    
    session.commit()


def seed_brand_safety_guides(session: Session):
    """Seed brand safety guidelines."""
    guides = [
        {
            "brand_type": "fitness",
            "prohibited_topics": ["unsafe_weight_loss_methods", "unhealthy_eating", "discrimination"],
            "required_disclosures": ["sponsored_content", "affiliate_links", "health_claims"],
            "compliance_requirements": ["FTC_guidelines", "no_medical_claims"],
            "tone_guardrails": ["positive", "inclusive", "science_based"],
            "sensitive_handling_guidelines": ["weight_neutral_language", "inclusive_imagery"],
        },
        {
            "brand_type": "finance",
            "prohibited_topics": ["guaranteed_returns", "get_rich_quick", "illegal_schemes"],
            "required_disclosures": ["financial_advice_disclaimer", "affiliate_products", "risks"],
            "compliance_requirements": ["SEC_guidelines", "FTC_guidelines"],
            "tone_guardrails": ["factual", "disclaimer_heavy", "conservative"],
            "sensitive_handling_guidelines": ["no_pump_and_dump", "realistic_expectations"],
        },
    ]
    
    for guide_data in guides:
        existing = session.query(BrandSafetyGuide).filter_by(brand_type=guide_data["brand_type"]).first()
        if not existing:
            guide = BrandSafetyGuide(**guide_data)
            session.add(guide)
    
    session.commit()


def init_knowledge_base(engine, seed: bool = False):
    """Initialize knowledge base tables and optionally seed data."""
    Base.metadata.create_all(bind=engine)
    
    if seed:
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            seed_platform_knowledge(session)
            seed_post_format_knowledge(session)
            seed_content_pillar_templates(session)
            seed_cta_templates(session)
            seed_hook_templates(session)
            seed_engagement_tactics(session)
            seed_influencer_tier_knowledge(session)
            seed_industry_best_practices(session)
            seed_seasonal_opportunities(session)
            seed_brand_safety_guides(session)
            print("✓ Knowledge base seeded successfully!")
        finally:
            session.close()
