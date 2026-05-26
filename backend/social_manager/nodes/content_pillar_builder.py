from __future__ import annotations
from typing import List, Dict
from social_manager.state import SocialManagerState, ContentPillar
from social_manager.llm import client
from social_manager.kb_context_injector import get_injector
from social_manager.llm_utils import extract_json_from_text

SYSTEM = (
    "You are Content Pillar Builder. Create 4-6 pillars with goal, post types, and CTA types. Return valid JSON only."
)

def build_content_pillars(state: SocialManagerState) -> SocialManagerState:
    # If pillars already exist (from previous run), preserve them with their weights
    if state.content_pillars and len(state.content_pillars) > 0:
        return state
    
    injector = get_injector()
    brand = state.brand_profile or {}
    persona = state.target_persona or {}
    funnel = (state.structured_context or {}).get("funnel_stage", "mixed")
    product_cat = brand.get("product_category", "general")
    industry = brand.get("industry", "general")
    
    # Get enriched context from KB
    brand_voice = injector.get_brand_voice_context(max_chars=1500)
    audience = injector.get_audience_context(max_chars=1500)
    campaign = injector.get_campaign_context(max_chars=1500)
    strategy = injector.get_social_strategy_context(max_chars=1500)

    prompt = f"""You are an expert Content Strategist. Create content pillars tailored to this brand.

BRAND VOICE & GUIDELINES:
{brand_voice}

TARGET AUDIENCE:
{audience}

CAMPAIGN STRATEGY:
{campaign}

SOCIAL STRATEGY CONTEXT:
{strategy}

BRAND DETAILS:
- Brand Name: {brand.get('brand_name', 'Brand')}
- Industry: {industry}
- Product Category: {product_cat}
- Brand Type: {brand.get('brand_type', 'general')}
- Audience Interests: {persona.get('interests', [])}
- Funnel Stage Focus: {funnel}

Create 4-6 content pillars as a JSON array of objects, each with:
- name: Pillar name (e.g., "Education")
- goal: What this pillar accomplishes (1-2 sentences)
- post_types: List of 3-5 post types/formats suitable for this pillar
- cta_types: List of 2-4 call-to-action types (e.g., "save", "share")
- weight: Relative importance (0.6 - 1.5, affects posting frequency)

Base reference examples:
- Education: Teach best practices, tips, myths
- Transformation Stories: Inspire with results, before/after
- Product Usage: Demonstrate value through demos and tutorials
- Community Highlights: Feature members, build belonging
- Behind-the-Scenes: Humanize brand, show personality
- Offers & Launches: Drive conversions

Return ONLY valid JSON array, no other text."""
    
    text = client.generate(prompt, system_instruction=SYSTEM)
    # Heuristic parse - fallback if Gemini returns natural text
    import json, re
    pillars: List[ContentPillar] = []
    try:
        # Try safe extraction first
        data = extract_json_from_text(text, json_type="array")
        if not data:
            # Fallback to manual parsing
            if text.strip().startswith("["):
                data = json.loads(text)
            else:
                # Try extracting JSON from text
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                else:
                    raise ValueError("No JSON array found")
        
        for p in data:
            pillars.append(ContentPillar(**p))
    except Exception as e:
        # Fallback to default if LLM parsing fails
        candidates = [
            ContentPillar(name="Education", goal="Teach best practices", post_types=["tips","how-to","myths"], cta_types=["save","share","comment"], weight=1.0),
            ContentPillar(name="Transformation stories", goal="Inspire with results", post_types=["before-after","case study","testimonial"], cta_types=["comment story","share","follow"], weight=1.0),
            ContentPillar(name="Product usage", goal="Demonstrate value", post_types=["demo","tutorial","use-cases"], cta_types=["try now","learn more"], weight=1.0),
            ContentPillar(name="Community highlights", goal="Build belonging", post_types=["feature","shoutout","collage"], cta_types=["tag us","join community"], weight=1.0),
            ContentPillar(name="Behind-the-scenes", goal="Humanize brand", post_types=["bts","team","process"], cta_types=["comment","follow"], weight=0.8),
            ContentPillar(name="Offers & launches", goal="Drive conversion", post_types=["promo","launch","bundle"], cta_types=["shop now","sign up"], weight=0.6),
        ]
        pillars = candidates[:6]
    
    state.content_pillars = pillars
    return state
