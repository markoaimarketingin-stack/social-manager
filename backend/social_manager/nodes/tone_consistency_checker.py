from __future__ import annotations
from social_manager.state import SocialManagerState
from social_manager.kb_context_injector import get_injector
from social_manager.llm import client
from social_manager.llm_utils import extract_json_from_text
import json
import logging

logger = logging.getLogger(__name__)

BRAND_TONE_KEYS = ["voice_keywords", "dos", "donts"]


def check_tone_consistency(state: SocialManagerState) -> SocialManagerState:
    """Check tone consistency using KB brand voice guidelines."""
    injector = get_injector()
    
    # Get brand voice from KB
    brand_voice_context = injector.get_brand_voice_context(max_chars=2000)
    
    voice = (state.brand_profile or {}).get("voice_keywords", [])
    if not state.monthly_calendar:
        return state
    
    # Enhanced tone check using LLM with KB context
    try:
        if client.available and brand_voice_context:
            # Sample check on first 20 posts for efficiency
            sample_posts = state.monthly_calendar[:20]
            post_data = [
                {
                    "id": idx,
                    "platform": e.platform,
                    "hook": e.hook,
                    "caption": e.caption_outline,
                    "pillar": e.pillar
                }
                for idx, e in enumerate(sample_posts)
            ]
            
            prompt = f"""You are a Tone Consistency Auditor. Review these posts against the brand voice guidelines.

BRAND VOICE GUIDELINES:
{brand_voice_context}

Posts to check:
{json.dumps(post_data, indent=2)}

For each post, assess:
1. Consistency with brand voice (tone, keywords, style)
2. Platform-appropriateness
3. Audience alignment

Return a JSON object with:
{{"flagged_posts": [{{id: int, reason: string, suggestion: string}}]}}

Only flag posts that significantly diverge from brand voice."""
            
            text = client.generate(prompt, system_instruction="Return valid JSON only.")
            data = extract_json_from_text(text, json_type="object")
            if not data:
                data = json.loads(text)
            
            flagged = data.get("flagged_posts", [])
            if flagged:
                state.structured_context.setdefault("tone_warnings", []).append(
                    f"{len(flagged)} posts flagged for tone inconsistency. Review: {[f['reason'] for f in flagged[:2]]}"
                )
    except Exception as e:
        logger.warning(f"KB tone check failed, falling back to keyword check: {e}")
        # Fallback: simple keyword check
        if voice:
            flagged = []
            for entry in state.monthly_calendar:
                if not any(v.lower() in entry.caption_outline.lower() for v in voice):
                    flagged.append(entry)
            if flagged:
                state.structured_context.setdefault("tone_warnings", []).append(
                    f"{len(flagged)} posts missing voice keywords"
                )
    
    return state
