from __future__ import annotations
from typing import List
from social_manager.state import SocialManagerState, Suggestion
from social_manager.kb_context_injector import get_injector
from social_manager.llm import client
from social_manager.llm_utils import extract_json_from_text
import json
import logging

logger = logging.getLogger(__name__)

BASE_SUGGESTIONS = [
    Suggestion(
        title="Create a content calendar for the next month",
        description=(
            "Plan and schedule your social media posts in advance to ensure a consistent and engaging presence. "
            "Include a mix of promotional, educational, and behind-the-scenes content."
        ),
        why_it_matters="Consistency compounds reach and trust over time.",
        action_id="generate_calendar",
    ),
    Suggestion(
        title="Run a user-generated content campaign",
        description=(
            "Encourage followers to share photos or videos using your product. "
            "This builds trust and provides authentic content for future campaigns."
        ),
        why_it_matters="UGC scales authenticity and lowers content costs.",
        action_id="launch_ugc",
    ),
    Suggestion(
        title="Host a Q&A or live video session",
        description=(
            "Engage directly with your audience through live sessions. "
            "Answer questions, showcase products, and strengthen community trust."
        ),
        why_it_matters="Live engagement boosts algorithmic reach and loyalty.",
        action_id="schedule_live",
    ),
    Suggestion(
        title="Collaborate with an influencer in your niche",
        description=(
            "Partner with a relevant influencer to expand reach and credibility through sponsored or co-created content."
        ),
        why_it_matters="Borrowed trust accelerates brand discovery.",
        action_id="collab_influencer",
    ),
]


def generate_suggestions(state: SocialManagerState) -> SocialManagerState:
    """Generate strategic suggestions enriched with KB insights."""
    injector = get_injector()
    suggestions: List[Suggestion] = []
    
    # Required fields check
    if not state.is_onboarding_complete():
        suggestions.append(
            Suggestion(
                title="Complete brand tone & persona",
                description="We need brand tone and target persona to generate a robust strategy.",
                why_it_matters="Accurate strategy depends on brand voice and audience clarity.",
                action_id="complete_onboarding",
            )
        )
    if not state.has_platforms():
        suggestions.append(
            Suggestion(
                title="Select active platforms",
                description="Choose which platforms to prioritize (Instagram, LinkedIn, YouTube, Twitter, Facebook).",
                why_it_matters="Different platforms demand different content styles and cadence.",
                action_id="choose_platforms",
            )
        )
    
    # KB-enriched contextual suggestions
    try:
        brand = state.brand_profile or {}
        industry = brand.get("industry", "general")
        
        # Get KB context
        audience_context = injector.get_audience_context(max_chars=1500)
        strategy_context = injector.get_social_strategy_context(max_chars=1500)
        campaign_context = injector.get_campaign_context(max_chars=1500)
        
        # Generate contextual suggestions
        prompt = f"""You are a Social Media Strategy Advisor. Based on this industry and audience, suggest 3 high-impact actions.

INDUSTRY: {industry}

AUDIENCE INSIGHTS:
{audience_context}

STRATEGY CONTEXT:
{strategy_context}

CAMPAIGN CONTEXT:
{campaign_context}

Current state:
- Engagement rate: {(state.engagement_metrics.engagement_rate or 0) if state.engagement_metrics else 0}%
- Platforms: {', '.join(state.active_platforms or [])}

Generate a JSON array with 3 objects, each with:
- title: Action title (5-8 words)
- description: What to do and why (2-3 sentences)
- why_it_matters: Business impact (1 sentence)
- action_id: ID code (e.g., "increase_reels")

Return ONLY valid JSON array."""
        
        text = client.generate(prompt, system_instruction="Return valid JSON array only.")
        
        # Try safe JSON extraction with fallback
        try:
            data = extract_json_from_text(text, json_type="array")
            if not data:
                data = json.loads(text)
        except Exception as parse_error:
            logger.warning(f"JSON parse error: {parse_error}, text: {text[:100]}")
            data = None
        
        if isinstance(data, list):
            for item in data[:3]:
                try:
                    suggestions.append(Suggestion(**item))
                except Exception as e:
                    logger.warning(f"Failed to parse suggestion: {e}")
    except Exception as e:
        logger.warning(f"KB contextual suggestions failed, using base suggestions: {e}")
    
    # Engagement low? Add specific tactics
    if state.engagement_metrics and (
        (state.engagement_metrics.engagement_rate or 0) < 1.0
        or (state.engagement_metrics.post_consistency_score or 0) < 0.6
    ):
        suggestions.extend(
            [
                Suggestion(
                    title="Increase community polls",
                    description="Add weekly interactive polls to gather insights and spark conversation.",
                    why_it_matters="Polls lower friction and boost engagement rates.",
                    action_id="add_polls",
                ),
                Suggestion(
                    title="Plan weekly live session",
                    description="Schedule consistent live sessions with Q&A and demos.",
                    why_it_matters="Live formats deepen trust and retention.",
                    action_id="add_weekly_live",
                ),
                Suggestion(
                    title="Push UGC participation",
                    description="Offer incentives and features for community submissions.",
                    why_it_matters="UGC compounds social proof and content velocity.",
                    action_id="push_ugc",
                ),
            ]
        )
    
    # Add base suggestions if not already included
    if len(suggestions) < 4:
        suggestions.extend(BASE_SUGGESTIONS)

    state.suggestions_list = suggestions[:8]  # Cap at 8 suggestions
    return state
