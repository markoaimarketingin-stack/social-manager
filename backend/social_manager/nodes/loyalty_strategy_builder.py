from __future__ import annotations
from social_manager.state import SocialManagerState, LoyaltyStrategy
from social_manager.kb_context_injector import get_injector
from social_manager.llm import client
from social_manager.llm_utils import extract_json_from_text
import json
import logging

logger = logging.getLogger(__name__)

def build_loyalty_strategy(state: SocialManagerState) -> SocialManagerState:
    """Generate loyalty program strategy enriched with KB insights."""
    injector = get_injector()
    
    # Get KB context
    brand_voice = injector.get_brand_voice_context(max_chars=1500)
    audience = injector.get_audience_context(max_chars=1500)
    campaign = injector.get_campaign_context(max_chars=1500)
    
    brand = state.brand_profile or {}
    industry = brand.get("industry", "general")
    
    prompt = f"""You are a Loyalty Program Designer. Create a loyalty strategy for this brand.

BRAND VOICE:
{brand_voice}

TARGET AUDIENCE:
{audience}

CAMPAIGN BRIEF:
{campaign}

Brand: {brand.get('brand_name', 'Brand')}
Industry: {industry}

Generate a JSON object with:
- vip_group: How to structure VIP/top customer community (1-2 sentences)
- referral_incentives: Referral program structure
- exclusive_content: List of 3-4 exclusive content types for loyal members
- early_access: Early access benefits description
- badge_system: Badge/tier system design (e.g., levels and their meanings)

Return ONLY valid JSON, no other text."""
    
    try:
        text = client.generate(prompt, system_instruction="You are a loyalty program expert. Return valid JSON only.")
        data = extract_json_from_text(text, json_type="object")
        if not data:
            data = json.loads(text)
        loyalty = LoyaltyStrategy(
            vip_group=data.get("vip_group", "Private Discord/FB group for top fans"),
            referral_incentives=data.get("referral_incentives", "Give $10, Get $10 store credit"),
            exclusive_content=data.get("exclusive_content", ["Monthly masterclass", "Pro templates", "Behind-the-scenes"]),
            early_access=data.get("early_access", "Beta access to new products"),
            badge_system=data.get("badge_system", "Levels: Explorer → Insider → Champion"),
        )
    except Exception as e:
        logger.warning(f"KB enrichment failed for loyalty strategy: {e}")
        # Fallback to default
        loyalty = LoyaltyStrategy(
            vip_group="Private Discord/FB group for top fans",
            referral_incentives="Give $10, Get $10 store credit",
            exclusive_content=["Monthly masterclass", "Pro templates", "Behind-the-scenes"],
            early_access="Beta access to new products",
            badge_system="Levels: Explorer → Insider → Champion",
        )
    
    state.loyalty_strategy = loyalty
    return state
