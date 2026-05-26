from __future__ import annotations
from typing import Dict
from social_manager.state import SocialManagerState, PlatformStrategy


PLATFORM_DEFAULTS = {
    "Instagram": PlatformStrategy(
        platform="Instagram",
        post_format_mix={"reel": 40, "carousel": 40, "single": 20},
        frequency_per_week=5,
        tone_variation="Upbeat, visual-first, community-centric",
        reel_vs_carousel_ratio="1:1",
        story_cadence="Daily quick updates",
    ),
    "LinkedIn": PlatformStrategy(
        platform="LinkedIn",
        post_format_mix={"text": 40, "image": 30, "doc": 15, "video": 15},
        frequency_per_week=3,
        tone_variation="Professional, insightful, value-led",
    ),
    "YouTube": PlatformStrategy(
        platform="YouTube",
        post_format_mix={"long": 70, "short": 30},
        frequency_per_week=2,
        tone_variation="Educational, storytelling, trustworthy",
    ),
    "Twitter": PlatformStrategy(
        platform="Twitter",
        post_format_mix={"thread": 40, "tweet": 40, "image": 20},
        frequency_per_week=7,
        tone_variation="Conversational, timely, witty",
    ),
    "Facebook": PlatformStrategy(
        platform="Facebook",
        post_format_mix={"image": 35, "link": 35, "video": 30},
        frequency_per_week=4,
        tone_variation="Friendly, community and events focused",
    ),
}


def select_platform_strategies(state: SocialManagerState) -> SocialManagerState:
    if not state.active_platforms:
        return state
    
    # Normalize platform names to match PLATFORM_DEFAULTS keys
    platform_name_map = {p.lower(): p for p in PLATFORM_DEFAULTS.keys()}
    
    strategies: Dict[str, PlatformStrategy] = {}
    normalized_platforms = []
    
    for p in state.active_platforms:
        # Try exact match first, then case-insensitive match
        normalized = platform_name_map.get(p.lower(), p)
        base = PLATFORM_DEFAULTS.get(normalized)
        if base:
            strategies[normalized] = base
            normalized_platforms.append(normalized)
    
    # Update state with normalized platform names and strategies
    state.active_platforms = normalized_platforms
    state.platform_strategies = {k: v for k, v in strategies.items()}
    
    # Also derive posting_frequency if not provided
    if not state.posting_frequency:
        state.posting_frequency = {k: v.frequency_per_week for k, v in strategies.items()}
    return state
