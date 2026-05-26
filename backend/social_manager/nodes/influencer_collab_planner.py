from __future__ import annotations
from social_manager.state import SocialManagerState, InfluencerStrategy
from social_manager.kb_context_injector import get_injector
from social_manager.llm import client
import json
import logging

logger = logging.getLogger(__name__)

def plan_influencer_collab(state: SocialManagerState) -> SocialManagerState:
    """Generate influencer collaboration strategy enriched with KB insights."""
    injector = get_injector()
    
    # Get KB context
    brand_voice = injector.get_brand_voice_context(max_chars=1500)
    audience = injector.get_audience_context(max_chars=1500)
    strategy = injector.get_social_strategy_context(max_chars=1500)
    
    brand = state.brand_profile or {}
    industry = brand.get("industry", "general")
    
    prompt = f"""You are an Influencer Collaboration Strategist. Create an influencer outreach strategy.

BRAND VOICE:
{brand_voice}

TARGET AUDIENCE:
{audience}

SOCIAL STRATEGY:
{strategy}

Brand: {brand.get('brand_name', 'Brand')}
Industry: {industry}
Product Category: {brand.get('product_category', 'general')}

Generate a JSON object with:
- micro_vs_macro: Strategy for choosing micro vs macro influencers (2-3 sentences)
- outreach_template: Email/DM template for influencer outreach
- collab_ideas: List of 3-4 collaboration ideas specific to this industry/brand
- giveaway_strategy: How to structure influencer giveaways
- affiliate_model: Affiliate/commission structure

Return ONLY valid JSON, no other text."""
    
    try:
        text = client.generate(prompt, system_instruction="You are an influencer strategy expert. Return valid JSON only.")
        data = extract_json_from_text(text, json_type="object")
        if not data:
            data = json.loads(text)
        strategy = InfluencerStrategy(
            micro_vs_macro=data.get("micro_vs_macro", "Focus on micro (10k-100k) for authenticity; occasional macro for reach"),
            outreach_template=data.get("outreach_template", 
                "Hi [Creator], we love your content on [topic]. We'd like to collaborate on [idea] for our community. We offer affiliate + giveaway support. Interested?"),
            collab_ideas=data.get("collab_ideas", [
                "Tutorial series",
                "Before/After challenge",
                "Live co-host Q&A",
            ]),
            giveaway_strategy=data.get("giveaway_strategy", "Monthly themed giveaway with UGC entries"),
            affiliate_model=data.get("affiliate_model", "Unique links + tiered commission"),
        )
    except Exception as e:
        logger.warning(f"KB enrichment failed for influencer planning: {e}")
        # Fallback to default
        strategy = InfluencerStrategy(
            micro_vs_macro="Focus on micro (10k-100k) for authenticity; occasional macro for reach",
            outreach_template=(
                "Hi [Creator], we love your content on [topic]. "
                "We'd like to collaborate on [idea] for our community. "
                "We offer affiliate + giveaway support. Interested?"
            ),
            collab_ideas=[
                "Tutorial series",
                "Before/After challenge",
                "Live co-host Q&A",
            ],
            giveaway_strategy="Monthly themed giveaway with UGC entries",
            affiliate_model="Unique links + tiered commission",
        )
    
    state.influencer_strategy = strategy
    return state
