from __future__ import annotations
from datetime import datetime
from typing import List, Dict
from social_manager.state import SocialManagerState

# 1. Viral Hook Generator (simple pattern mining from existing calendar)

def generate_viral_hooks(state: SocialManagerState) -> List[str]:
    hooks = []
    past = state.monthly_calendar or []
    for e in past[:50]:
        if any(k in e.hook.lower() for k in ["secret", "mistake", "before", "after", "why", "how"]):
            hooks.append(e.hook)
    # Suggest new by templating
    base = [
        "The 3 mistakes you're making with {pillar}",
        "Before/After: {pillar} results in 30 days",
        "Why {pillar} works better than you think",
        "How to start with {pillar} in 5 steps",
    ]
    pillars = [p.name for p in (state.content_pillars or [])] or ["your niche"]
    synthetic = [t.format(pillar=pillars[i % len(pillars)]) for i, t in enumerate(base)]
    return list(dict.fromkeys(hooks + synthetic))[:10]

# 2. Engagement Score

def compute_engagement_score(state: SocialManagerState) -> Dict[str, float]:
    er = (state.engagement_metrics.engagement_rate or 0) / 10  # normalize 0-1 from percent
    fg = min(max((state.engagement_metrics.follower_growth or 0) / 1000, 0), 1)
    pc = state.engagement_metrics.post_consistency_score or 0
    score = round((0.5 * er + 0.3 * pc + 0.2 * fg) * 100, 1)
    return {"score": score, "er": er, "fg": fg, "pc": pc}

# 3. Seasonal Opportunity Detector (simple date & keywords)

SEASONAL_EVENTS = {
    1: ["New Year", "CES"],
    2: ["Valentine's"],
    3: ["Women's Day"],
    4: ["Easter", "Earth Day"],
    5: ["Mother's Day"],
    6: ["Father's Day"],
    7: ["Summer Sale"],
    8: ["Back to School"],
    9: ["Industry Expo"],
    10: ["Halloween"],
    11: ["Singles Day", "Black Friday", "Cyber Monday"],
    12: ["Holiday Season", "Anniversary"]
}


def detect_seasonal_opportunities(state: SocialManagerState) -> List[str]:
    m = datetime.utcnow().month
    return SEASONAL_EVENTS.get(m, [])

# 5. Repurposing Engine

def repurpose_longform(title: str) -> Dict[str, List[str]]:
    return {
        "from_blog": [
            f"Carousel: 5 takeaways from {title}",
            f"Reel: 3 myths about {title}",
            f"Quote post: Best line from {title}",
            f"Thread: Lessons from {title}",
            f"Checklist: Steps to apply {title}",
        ],
        "from_video": [
            f"Reel 1: Hook from {title}",
            f"Reel 2: Tip from {title}",
            f"Reel 3: Case snippet from {title}",
            f"Quote image: Pull-quote from {title}",
            f"BTS: Making of {title}",
        ],
    }
