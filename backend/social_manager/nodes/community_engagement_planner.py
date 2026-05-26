from __future__ import annotations
from typing import List
from social_manager.state import SocialManagerState, EngagementPlan
from social_manager.kb_context_injector import get_injector
from social_manager.llm import client
from social_manager.llm_utils import extract_json_from_text
import json

def plan_community_engagement(state: SocialManagerState) -> SocialManagerState:
    """Generate engagement plan enriched with knowledge base insights."""
    injector = get_injector()
    
    # Get KB context for enriched decision-making
    brand_voice = injector.get_brand_voice_context(max_chars=1500)
    audience = injector.get_audience_context(max_chars=1500)
    strategy = injector.get_social_strategy_context(max_chars=1500)
    
    # Build enriched prompt
    brand = state.brand_profile or {}
    industry = brand.get("industry", "general")
    
    prompt = f"""You are a Community Engagement Strategist. Create a comprehensive engagement plan.

BRAND CONTEXT:
{brand_voice}

AUDIENCE INSIGHTS:
{audience}

SOCIAL STRATEGY:
{strategy}

Brand: {brand.get('brand_name', 'Brand')}
Industry: {industry}
Active Platforms: {', '.join(state.active_platforms or [])}

Generate a JSON object with these fields:
- comment_response: Best practices for responding to comments (2-3 sentences)
- dm_script: Template for DM responses when users reach out
- poll_ideas: 3-4 poll question ideas relevant to industry/audience
- weekly_live: Description of weekly live session format and timing
- qa_topics: 3-4 Q&A topics most relevant to audience interests
- gamification: 3-4 engagement gamification ideas (badges, challenges, rewards)

Return ONLY valid JSON, no other text."""
    
    try:
        text = client.generate(prompt, system_instruction="You are an engagement expert. Return valid JSON only.")
        data = extract_json_from_text(text, json_type="object")
        if not data:
            data = json.loads(text)
        plan = EngagementPlan(
            comment_response=data.get("comment_response", "Respond within 2 hours; use name; ask follow-up"),
            dm_script=data.get("dm_script", "Hi [Name]! Thanks for reaching out—how can we help today?"),
            poll_ideas=data.get("poll_ideas", ["Which topic interests you?", "Rate this idea", "Your favorite variant?"]),
            weekly_live=data.get("weekly_live", "Weekly live session every Thursday 6 PM with Q&A"),
            qa_topics=data.get("qa_topics", ["Getting started", "Troubleshooting", "Pro tips"]),
            gamification=data.get("gamification", ["Weekly challenge", "Top commenter badge", "Referral leaderboard"]),
        )
    except Exception as e:
        # Fallback to default if LLM fails
        plan = EngagementPlan(
            comment_response="Respond within 2 hours; use name; ask follow-up",
            dm_script="Hi [Name]! Thanks for reaching out—how can we help today?",
            poll_ideas=[
                "Which topic should we cover next?",
                "Rate this feature idea",
                "Pick your favorite product variant",
            ],
            weekly_live="Weekly live session every Thursday 6 PM with Q&A",
            qa_topics=["Getting started", "Troubleshooting", "Pro tips"],
            gamification=["Weekly challenge", "Top commenter badge", "Referral leaderboard"],
        )
    
    state.engagement_plan = plan
    return state
