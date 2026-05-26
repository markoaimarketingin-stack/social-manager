from __future__ import annotations
from typing import List
from datetime import datetime, timedelta
import random
from social_manager.state import SocialManagerState, CalendarEntry
from social_manager.llm import client
from social_manager.kb_context_injector import get_injector
from social_manager.llm_utils import extract_json_from_text
import json
import logging

logger = logging.getLogger(__name__)

CATEGORIES = [
    ("value", 0.4),
    ("engagement", 0.3),
    ("social_proof", 0.2),
    ("promotional", 0.1),
]

FORMATS_BY_PLATFORM = {
    "Instagram": ["reel", "carousel", "single", "story"],
    "LinkedIn": ["text", "image", "doc", "video"],
    "YouTube": ["long", "short"],
    "Twitter": ["tweet", "thread", "image"],
    "Facebook": ["image", "link", "video"],
}


def weighted_category(day_index: int) -> str:
    # Enforce approximate distribution across 30 days
    r = random.random()
    acc = 0.0
    for name, w in CATEGORIES:
        acc += w
        if r <= acc:
            return name
    return CATEGORIES[-1][0]


def generate_monthly_calendar(state: SocialManagerState, days: int = 30) -> SocialManagerState:
    if not state.content_pillars or not state.active_platforms:
        return state

    injector = get_injector()
    
    # Get KB context for enriched calendar generation
    brand_voice = injector.get_brand_voice_context(max_chars=1500)
    audience = injector.get_audience_context(max_chars=1500)
    strategy = injector.get_social_strategy_context(max_chars=1500)
    
    start = datetime.utcnow().date()
    calendar: List[CalendarEntry] = []
    pillars = state.content_pillars
    brand = state.brand_profile or {}

    for i in range(days):
        d = start + timedelta(days=i)
        for platform in state.active_platforms:
            freq = state.posting_frequency.get(platform, 3)
            # Approx distribute posts per week; here simple every other day if freq<7
            should_post = (i % max(1, 7 // max(1, min(freq, 7)))) == 0
            if not should_post:
                continue
            pillar = random.choice(pillars)
            fmt_list = FORMATS_BY_PLATFORM.get(platform, ["post"])
            fmt = random.choice(fmt_list)
            cat = weighted_category(i)
            hook = f"{pillar.name}: {platform} hook idea for {d.strftime('%b %d')}"
            caption = f"Outline: {pillar.goal}. Key points + CTA."
            cta = random.choice(pillar.cta_types)
            calendar.append(
                CalendarEntry(
                    date=d.isoformat(),
                    platform=platform,
                    pillar=pillar.name,
                    format=fmt,
                    hook=hook,
                    caption_outline=caption,
                    cta=cta,
                    category=cat,
                )
            )
    
    # Enhanced Gemini refinement using KB context to match brand voice and platform norms
    try:
        sample = calendar[: min(30, len(calendar))]
        if sample and client.available:
            payload_lines = []
            for idx, e in enumerate(sample):
                payload_lines.append(
                    f"{{'i':{idx},'platform':'{e.platform}','pillar':'{e.pillar}','format':'{e.format}','hook':'{e.hook}','category':'{e.category}'}}"
                )
            
            voice = (brand or {}).get("voice_keywords", [])
            
            prompt = f"""You are a Social Content Copy Chief. Refine the following social post hooks and captions to align perfectly with brand voice and platform norms.

BRAND VOICE & GUIDELINES:
{brand_voice}

TARGET AUDIENCE INSIGHTS:
{audience}

SOCIAL STRATEGY:
{strategy}

BRAND: {brand.get('brand_name', 'Brand')}
Voice Keywords: {', '.join(voice) if voice else 'none specified'}

For each post, optimize:
1. Hook to be platform-native and thumb-stopping
2. Caption outline to drive engagement for the category
3. CTA to be clear and conversion-focused

Return a JSON array with objects containing only: {{"i": (int), "hook": (string), "caption_outline": (string), "platform_tips": (string)}}

Posts to refine:
{json.dumps([json.loads(line) for line in payload_lines], indent=2)}"""
            
            text = client.generate(prompt, system_instruction="You are a social copy expert. Return valid JSON array only, no other text.")
            data = extract_json_from_text(text, json_type="array")
            if not data:
                data = json.loads(text)
            mapping = {int(o.get("i", -1)): o for o in data if isinstance(o, dict) and "i" in o}
            for idx, e in enumerate(sample):
                if idx in mapping:
                    o = mapping[idx]
                    e.hook = o.get("hook", e.hook)
                    e.caption_outline = o.get("caption_outline", e.caption_outline)
    except Exception as e:
        logger.warning(f"KB-enriched refinement failed, using basic refinement: {e}")
        # Fallback: basic refinement without KB context
        try:
            sample = calendar[: min(30, len(calendar))]
            if sample and client.available:
                payload_lines = []
                for idx, e in enumerate(sample):
                    payload_lines.append(
                        f"{{'i':{idx},'platform':'{e.platform}','pillar':'{e.pillar}','hook':'{e.hook}','caption':'{e.caption_outline}'}}"
                    )
                voice = (brand or {}).get("voice_keywords", [])
                prompt = (
                    "Refine the following social post hooks and captions to align with the brand voice and platform norms. "
                    "Return JSON array with objects {i, hook, caption_outline} only. Voice keywords: "
                    + ", ".join(voice)
                    + "\nPosts:\n"
                    + "\n".join(payload_lines)
                )
                text = client.generate(prompt, system_instruction="You are a social copy chief.")
                data = extract_json_from_text(text, json_type="array")
                if not data:
                    data = json.loads(text)
                mapping = {int(o.get("i", -1)): o for o in data if isinstance(o, dict) and "i" in o}
                for idx, e in enumerate(sample):
                    if idx in mapping:
                        o = mapping[idx]
                        e.hook = o.get("hook", e.hook)
                        e.caption_outline = o.get("caption_outline", e.caption_outline)
        except Exception:
            pass

    state.monthly_calendar = calendar
    return state
