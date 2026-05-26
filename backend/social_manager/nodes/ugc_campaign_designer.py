from __future__ import annotations
from social_manager.state import SocialManagerState, UGCStrategy
from social_manager.kb_context_injector import get_injector
from social_manager.llm import client
from social_manager.llm_utils import extract_json_from_text
import json
import logging

logger = logging.getLogger(__name__)

def design_ugc_campaign(state: SocialManagerState) -> SocialManagerState:
    """Generate UGC campaign strategy enriched with KB insights."""
    injector = get_injector()
    
    # Get KB context
    brand_voice = injector.get_brand_voice_context(max_chars=1500)
    audience = injector.get_audience_context(max_chars=1500)
    campaign = injector.get_campaign_context(max_chars=1500)
    
    brand = state.brand_profile or {}
    industry = brand.get("industry", "general")
    product_cat = brand.get("product_category", "general")
    
    prompt = f"""You are a UGC Campaign Designer. Create a user-generated content campaign.

BRAND VOICE:
{brand_voice}

TARGET AUDIENCE:
{audience}

CAMPAIGN BRIEF:
{campaign}

Brand: {brand.get('brand_name', 'Brand')}
Industry: {industry}
Product Category: {product_cat}

Generate a JSON object with:
- theme: Campaign theme/prompt for users (1-2 sentences)
- hashtag: Campaign hashtag (e.g., #BrandChallenge)
- incentive: What users get for participating
- submission_method: How users submit (tag, hashtag, DM, etc)
- repurposing_plan: List of 3-4 ways to repurpose UGC content

Return ONLY valid JSON, no other text."""
    
    try:
        text = client.generate(prompt, system_instruction="You are a UGC expert. Return valid JSON only.")
        data = extract_json_from_text(text, json_type="object")
        if not data:
            data = json.loads(text)
        
        # Generate hashtag from brand name if not provided
        default_hashtag = "#{0}Challenge".format((brand.get('brand_name','brand')).replace(" ", ""))
        
        strategy = UGCStrategy(
            theme=data.get("theme", f"Show us your {product_cat} transformation"),
            hashtag=data.get("hashtag", default_hashtag),
            incentive=data.get("incentive", "Feature + 10% discount"),
            submission_method=data.get("submission_method", "Tag us + hashtag; optional DM for consent"),
            repurposing_plan=data.get("repurposing_plan", [
                "Compile monthly highlight reel",
                "Quote-post best captions",
                "Turn top entries into case studies",
            ]),
        )
    except Exception as e:
        logger.warning(f"KB enrichment failed for UGC campaign: {e}")
        # Fallback to default
        default_hashtag = "#{0}Challenge".format((brand.get('brand_name','brand')).replace(" ", ""))
        strategy = UGCStrategy(
            theme=f"Show us your {product_cat} transformation",
            hashtag=default_hashtag,
            incentive="Feature + 10% discount",
            submission_method="Tag us + hashtag; optional DM for consent",
            repurposing_plan=[
                "Compile monthly highlight reel",
                "Quote-post best captions",
                "Turn top entries into case studies",
            ],
        )
    
    state.ugc_strategy = strategy
    return state
