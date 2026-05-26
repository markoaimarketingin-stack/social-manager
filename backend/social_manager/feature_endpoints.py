"""
API Endpoints for the 5 New Features
Integrate Trend, Competitor, Segmentation, Positioning, and Copy Generation
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from social_manager.trend_intelligence import get_trend_intelligence
from social_manager.competitor_intelligence import get_competitor_intelligence
from social_manager.market_segmentation import get_market_segmentation
from social_manager.brand_positioning import get_brand_positioning
from social_manager.copy_generator import get_copy_generator

# Create routers for each feature
trends_router = APIRouter(prefix="/api/intelligence/trends", tags=["Trend Intelligence"])
competitor_router = APIRouter(prefix="/api/intelligence/competitors", tags=["Competitor Intelligence"])
segmentation_router = APIRouter(prefix="/api/intelligence/segments", tags=["Market Segmentation"])
positioning_router = APIRouter(prefix="/api/intelligence/positioning", tags=["Brand Positioning"])
copy_router = APIRouter(prefix="/api/creative/copy", tags=["Copy Generation"])


# ===== TREND INTELLIGENCE ENDPOINTS =====

@trends_router.get("/trending")
async def get_trending_topics(
    category: Optional[str] = Query("fitness", description="Topic category"),
    limit: int = Query(10, description="Number of trends to return")
):
    """Get trending topics from all sources."""
    trends = get_trend_intelligence()
    brand_keywords = [category, "community", "transformation"]
    top_trends = trends.get_top_trends_for_brand(brand_keywords, limit=limit)
    
    return {
        "status": "success",
        "category": category,
        "trends_count": len(top_trends),
        "trends": [
            {
                "name": t.name,
                "source": t.source,
                "volume": t.volume,
                "momentum": t.momentum,
                "relevance_score": round(t.relevance_score, 2),
                "related_topics": t.related_topics,
            }
            for t in top_trends
        ],
        "sync_time": datetime.utcnow(),
    }


@trends_router.get("/opportunities")
async def get_trend_opportunities(
    brand_keywords: Optional[List[str]] = Query(["fitness", "health"])
):
    """Get emerging trend opportunities for content creation."""
    trends = get_trend_intelligence()
    opportunities = trends.get_emerging_opportunities(brand_keywords)
    
    return {
        "status": "success",
        "brand_keywords": brand_keywords,
        "emerging_opportunities": opportunities,
    }


@trends_router.get("/content-ideas")
async def get_content_ideas_from_trends(
    category: str = Query("fitness")
):
    """Generate content ideas based on current trends."""
    trends = get_trend_intelligence()
    top_trends = trends.get_top_trends_for_brand([category], limit=5)
    ideas = trends._generate_content_ideas(top_trends)
    
    return {
        "status": "success",
        "category": category,
        "content_ideas": ideas,
    }


# ===== COMPETITOR INTELLIGENCE ENDPOINTS =====

@competitor_router.post("/add")
async def add_competitor(
    name: str,
    instagram_handle: Optional[str] = None,
    linkedin_handle: Optional[str] = None,
    x_handle: Optional[str] = None,
    tier: str = "direct_competitor"
):
    """Add a new competitor to track."""
    competitors = get_competitor_intelligence()
    
    handles = {}
    if instagram_handle:
        handles["instagram"] = instagram_handle
    if linkedin_handle:
        handles["linkedin"] = linkedin_handle
    if x_handle:
        handles["x"] = x_handle
    
    competitor = competitors.add_competitor(name, handles, tier)
    
    return {
        "status": "success",
        "competitor": {
            "id": competitor.id,
            "name": competitor.name,
            "platforms": competitor.platforms,
            "tier": competitor.tier,
        }
    }


@competitor_router.get("/{competitor_name}/summary")
async def get_competitor_summary(competitor_name: str):
    """Get comprehensive summary of a competitor."""
    comp_intel = get_competitor_intelligence()
    
    # In real implementation, would fetch from database
    competitor = comp_intel.add_competitor(
        name=competitor_name,
        handles={"instagram": f"@{competitor_name.lower()}", "linkedin": competitor_name},
        tier="direct_competitor"
    )
    
    summary = comp_intel.get_competitor_summary(competitor)
    
    return {
        "status": "success",
        "competitor_summary": summary,
    }


@competitor_router.get("/analysis/share-of-voice")
async def get_share_of_voice_analysis(
    competitors: Optional[List[str]] = Query(["You", "Competitor A", "Competitor B"])
):
    """Calculate share of voice across competitors."""
    comp_intel = get_competitor_intelligence()
    
    # Convert to competitor objects (simplified)
    competitor_objs = [
        comp_intel.add_competitor(name, {"instagram": f"@{name.lower()}"})
        for name in competitors[1:]  # Skip "You"
    ]
    
    sov = comp_intel.calculate_share_of_voice(competitor_objs)
    
    return {
        "status": "success",
        "metric": "followers",
        "share_of_voice": sov,
    }


@competitor_router.get("/gaps/opportunities")
async def get_competitive_gaps():
    """Identify competitive gaps to exploit."""
    comp_intel = get_competitor_intelligence()
    competitor = comp_intel.add_competitor("Competitor A", {"instagram": "@compA"})
    gaps = comp_intel.identify_competitive_gaps([competitor])
    
    return {
        "status": "success",
        "competitive_gaps": gaps,
    }


# ===== MARKET SEGMENTATION ENDPOINTS =====

@segmentation_router.get("/industry/{industry}")
async def get_industry_segments(industry: str = "fitness"):
    """Get dynamic market segments for an industry using LLM."""
    segmentation = get_market_segmentation()
    
    # Use LLM to generate segments for any industry
    segments = await segmentation.generate_market_segments_for_industry(industry)
    
    return {
        "status": "success",
        "industry": industry,
        "segments_count": len(segments),
        "segments": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "size": s.size_estimate,
                "growth_rate": f"{s.growth_rate}%",
                "primary_platform": s.primary_platform,
                "messaging": s.messaging_angle,
            }
            for s in segments
        ],
    }


@segmentation_router.post("/custom")
async def create_custom_segment(
    name: str,
    description: str,
    size_estimate: int,
    primary_platform: str,
    messaging_angle: str
):
    """Create a custom market segment."""
    segmentation = get_market_segmentation()
    segment = segmentation.create_segment(
        name=name,
        description=description,
        size_estimate=size_estimate,
        primary_platform=primary_platform,
        messaging_angle=messaging_angle,
    )
    
    return {
        "status": "success",
        "segment": {
            "id": segment.id,
            "name": segment.name,
            "description": segment.description,
            "size": segment.size_estimate,
            "platform": segment.primary_platform,
        }
    }


@segmentation_router.get("/{segment_name}/messaging")
async def get_segment_messaging(segment_name: str):
    """Get tailored messaging strategy for a segment."""
    segmentation = get_market_segmentation()
    segments = segmentation.add_default_segments_for_fitness()
    
    segment = next((s for s in segments if s.name == segment_name), None)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    messaging = segmentation.get_segment_messaging(segment)
    
    return {
        "status": "success",
        "segment": segment_name,
        "messaging_strategy": messaging,
    }


@segmentation_router.get("/{segment_name}/content-mix")
async def get_segment_content_mix(segment_name: str):
    """Get recommended content mix for a specific segment."""
    segmentation = get_market_segmentation()
    segments = segmentation.add_default_segments_for_fitness()
    
    segment = next((s for s in segments if s.name == segment_name), None)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    content_mix = segmentation.recommend_content_mix(segment)
    
    return {
        "status": "success",
        "segment": segment_name,
        "content_recommendations": content_mix,
    }


# ===== BRAND POSITIONING ENDPOINTS =====

@positioning_router.post("/create")
async def create_positioning_statement(
    brand_name: str,
    target_audience: str,
    customer_need: str,
    product_category: str,
    unique_benefit: str,
    proof_point: str
):
    """Create a formal brand positioning statement."""
    positioning = get_brand_positioning(brand_name)
    
    stmt = await positioning.create_positioning_statement(
        target_audience=target_audience,
        customer_need=customer_need,
        product_category=product_category,
        unique_benefit=unique_benefit,
        proof_point=proof_point,
    )
    
    return {
        "status": "success",
        "positioning_statement": stmt.to_markdown(),
        "elevator_pitch": positioning.generate_elevator_pitch(),
    }


@positioning_router.post("/uvp")
async def create_uvp(
    brand_name: str,
    functional_benefits: List[str],
    emotional_benefits: List[str],
    social_benefits: List[str]
):
    """Create a Unique Value Proposition."""
    positioning = get_brand_positioning(brand_name)
    
    uvp = await positioning.create_uvp(
        functional=functional_benefits,
        emotional=emotional_benefits,
        social=social_benefits,
        rational_beliefs=["Proven results", "Expert team", "Science-backed"],
        emotional_beliefs=["Inspiring community", "Supportive environment"],
        competitor_advantages={
            "Community": "We actually engage vs abandoned groups",
            "Accessibility": "Premium results at fair prices",
            "Personality": "Founder-led vs faceless corporation",
        },
    )
    
    return {
        "status": "success",
        "uvp": {
            "functional_benefits": uvp.functional_benefits,
            "emotional_benefits": uvp.emotional_benefits,
            "social_benefits": uvp.social_benefits,
            "proof_points": uvp.rational_reasons_to_believe,
        }
    }


@positioning_router.get("/guidelines/{brand_name}")
async def get_positioning_guidelines(brand_name: str):
    """Get brand positioning guidelines document."""
    positioning = get_brand_positioning(brand_name)
    await positioning.create_positioning_statement(
        target_audience="Busy professionals",
        customer_need="fitness without stress",
        product_category="Personalized fitness",
        unique_benefit="Community + Efficiency",
        proof_point="1000+ transformations in 90 days"
    )
    
    guidelines = positioning.generate_positioning_guidelines()
    
    return {
        "status": "success",
        "brand_name": brand_name,
        "positioning_guidelines": guidelines,
    }


# ===== COPY GENERATION ENDPOINTS =====

@copy_router.post("/reel")
async def generate_reel_copy(
    hook: str,
    benefit: str,
    cta: Optional[str] = "Save this for the gym"
):
    """Generate optimized Reel copy."""
    generator = get_copy_generator()
    copy = await generator.generate_reel_copy(hook, benefit, cta)
    
    return {
        "status": "success",
        "post_type": "reel",
        "copy": copy,
    }


@copy_router.post("/carousel")
async def generate_carousel_copy(
    topic: str,
    slide_count: int = 5,
    angle: Optional[str] = "educational"
):
    """Generate copy for carousel posts."""
    generator = get_copy_generator()
    copy_list = await generator.generate_carousel_copy(topic, slide_count, angle)
    
    return {
        "status": "success",
        "post_type": "carousel",
        "slides": slide_count,
        "copy": [
            {"slide": i+1, "text": text}
            for i, text in enumerate(copy_list)
        ],
    }


@copy_router.post("/variants")
async def generate_copy_variants(
    topic: str,
    content_type: str = "reel",
    variant_count: int = 4
):
    """Generate A/B test variants for copy testing."""
    generator = get_copy_generator()
    variants = await generator.generate_copy_variants(topic, content_type, variant_count)
    
    return {
        "status": "success",
        "topic": topic,
        "variants": [
            {
                "variant_id": v.variant_id,
                "tone": v.tone,
                "copy": v.text,
                "length": v.length,
                "emotional_hook": v.emotional_hook,
                "cta_type": v.cta_type,
                "predicted_engagement": round(v.predicted_performance, 3),
            }
            for v in variants
        ],
    }


@copy_router.post("/complete-post")
async def generate_complete_post(
    pillar: str,
    platform: str,
    topic: str,
    include_variants: bool = True
):
    """Generate complete post with copy, hashtags, emojis, and variants."""
    generator = get_copy_generator()
    post = await generator.generate_complete_post_copy(pillar, platform, topic, include_variants)
    
    return {
        "status": "success",
        "post": {
            "pillar": post.pillar,
            "platform": post.platform,
            "topic": post.topic,
            "primary_copy": post.primary_copy,
            "variant_count": len(post.variants),
            "hashtags": post.hashtag_set[:15],
            "best_posting_time": post.best_posting_time,
        },
        "variants": [
            {
                "variant_id": v.variant_id,
                "tone": v.tone,
                "copy": v.text[:100] + "...",
            }
            for v in post.variants[:3]
        ] if include_variants else [],
    }


@copy_router.get("/guidance/{platform}/{content_type}")
async def get_copy_guidance(platform: str, content_type: str):
    """Get best practices for writing copy on specific platform/format."""
    generator = get_copy_generator()
    guidance = generator.generate_copy_guidance(platform, content_type)
    
    return {
        "status": "success",
        "platform": platform,
        "content_type": content_type,
        "best_practices": guidance,
    }


# Aggregate all routers
all_feature_routers = [
    trends_router,
    competitor_router,
    segmentation_router,
    positioning_router,
    copy_router,
]
