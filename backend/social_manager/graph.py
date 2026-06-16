"""
Social Manager multi-agent graph with 6 Core Agent architecture.

Agents:
- Supervisor Agent: Orchestrates tasks, request approvals, generates suggestions.
- Memory Agent: Injects brand voice, guidelines, target personas, and past context.
- Content Agent: Selects platform strategies, builds pillars, drafts monthly calendar.
- Compliance Agent: Runs safety checks and scores policy violations.
- Publisher Agent: Packages posts and structures the publishing schedules.
- Analytics Agent: Enriches drafts with viral hooks, seasonal patterns, and engagement scores.
"""

from __future__ import annotations
from typing import Callable
from langgraph.graph import StateGraph, END
from social_manager.state import SocialManagerState
from social_manager.nodes.content_pillar_builder import build_content_pillars
from social_manager.nodes.platform_strategy_selector import select_platform_strategies
from social_manager.nodes.content_calendar_generator import generate_monthly_calendar
from social_manager.nodes.community_engagement_planner import plan_community_engagement
from social_manager.nodes.ugc_campaign_designer import design_ugc_campaign
from social_manager.nodes.influencer_collab_planner import plan_influencer_collab
from social_manager.nodes.loyalty_strategy_builder import build_loyalty_strategy
from social_manager.nodes.suggestion_generator import generate_suggestions
from social_manager.nodes.tone_consistency_checker import check_tone_consistency
from social_manager.advanced import generate_viral_hooks, compute_engagement_score, detect_seasonal_opportunities


class SocialManagerGraph:
    """
    Main orchestrator compiling the 6 core agents defined in the plan:
    Supervisor, Memory, Content, Compliance, Publisher, and Analytics.
    """
    
    def __init__(self):
        self.graph = StateGraph(SocialManagerState)
        
        # Add nodes for the 6 Core Agents
        self.graph.add_node("supervisor", self._supervisor_agent)
        self.graph.add_node("memory", self._memory_agent)
        self.graph.add_node("content", self._content_agent)
        self.graph.add_node("compliance", self._compliance_agent)
        self.graph.add_node("publisher", self._publisher_agent)
        self.graph.add_node("analytics", self._analytics_agent)
        
        # Sequential execution flow
        self.graph.set_entry_point("supervisor")
        self.graph.add_edge("supervisor", "memory")
        self.graph.add_edge("memory", "content")
        self.graph.add_edge("content", "compliance")
        self.graph.add_edge("compliance", "publisher")
        self.graph.add_edge("publisher", "analytics")
        self.graph.add_edge("analytics", END)
        
        self.app = self.graph.compile()

    def _supervisor_agent(self, state: dict) -> dict:
        obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
        # Interpret intent and generate initial suggestions
        obj = generate_suggestions(obj)
        
        # Audit trails
        if "strategy_logs" not in obj.structured_context:
            obj.structured_context["strategy_logs"] = []
        obj.structured_context["strategy_logs"].append(
            f"Supervisor Agent: Initialized task workflow. Suggested actions: {len(obj.suggestions_list)} generated."
        )
        return obj.model_dump()

    def _memory_agent(self, state: dict) -> dict:
        obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
        from social_manager.kb_context_injector import get_injector
        
        # Retrieve brand, audience and strategy details
        injector = get_injector()
        brand_voice = injector.get_brand_voice_context(max_chars=500)
        audience = injector.get_audience_context(max_chars=500)
        
        # Inject into state for content creation reference
        obj.structured_context["brand_voice_context"] = brand_voice
        obj.structured_context["audience_context"] = audience
        
        if "strategy_logs" not in obj.structured_context:
            obj.structured_context["strategy_logs"] = []
        obj.structured_context["strategy_logs"].append(
            f"Memory Agent: Injected brand guidelines (length: {len(brand_voice)}) and audience segments (length: {len(audience)})."
        )
        return obj.model_dump()

    def _content_agent(self, state: dict) -> dict:
        obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
        
        # 1. Run Platform selection & content pillars
        obj = select_platform_strategies(obj)
        obj = build_content_pillars(obj)
        
        # 2. Generate monthly content calendar
        obj = generate_monthly_calendar(obj)
        
        # 3. Check tone consistency
        obj = check_tone_consistency(obj)
        
        # 4. Structure campaigns / community outreach / loyalty / influencer programs
        obj = plan_community_engagement(obj)
        obj = design_ugc_campaign(obj)
        obj = plan_influencer_collab(obj)
        obj = build_loyalty_strategy(obj)
        
        if "strategy_logs" not in obj.structured_context:
            obj.structured_context["strategy_logs"] = []
        obj.structured_context["strategy_logs"].append(
            f"Content Agent: Created {len(obj.content_pillars)} pillars, monthly calendar, and campaign strategies."
        )
        return obj.model_dump()

    def _compliance_agent(self, state: dict) -> dict:
        obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
        from social_manager.approvals import policy_engine
        
        violations_count = 0
        approved_count = 0
        
        for entry in obj.monthly_calendar:
            content_to_check = f"{entry.hook} {entry.caption_outline}"
            check_res = policy_engine.check_content(content_to_check)
            if not check_res["passed"]:
                violations_count += 1
            else:
                approved_count += 1
                
        obj.structured_context["compliance_checked"] = True
        obj.structured_context["compliance_violations"] = violations_count
        
        if "strategy_logs" not in obj.structured_context:
            obj.structured_context["strategy_logs"] = []
        obj.structured_context["strategy_logs"].append(
            f"Compliance Agent: Ran policy scans. Approved drafts: {approved_count}, Violations flagged: {violations_count}."
        )
        return obj.model_dump()

    def _publisher_agent(self, state: dict) -> dict:
        obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
        
        # Structure posting metadata / scheduling queue details
        obj.structured_context["publisher_ready"] = True
        
        if "strategy_logs" not in obj.structured_context:
            obj.structured_context["strategy_logs"] = []
        obj.structured_context["strategy_logs"].append(
            f"Publisher Agent: Configured scheduling configurations."
        )
        return obj.model_dump()

    def _analytics_agent(self, state: dict) -> dict:
        obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
        
        # Ingest advanced metrics patterns
        obj.structured_context["viral_hooks"] = generate_viral_hooks(obj)
        obj.structured_context["seasonal_opportunities"] = detect_seasonal_opportunities(obj)
        obj.structured_context["engagement_score"] = compute_engagement_score(obj)
        
        if "strategy_logs" not in obj.structured_context:
            obj.structured_context["strategy_logs"] = []
        obj.structured_context["strategy_logs"].append(
            f"Analytics Agent: Ingested predictions (viral hooks: {len(obj.structured_context['viral_hooks'])})."
        )
        return obj.model_dump()

    def run(self, state: SocialManagerState) -> SocialManagerState:
        result = self.app.invoke(state.model_dump())
        return SocialManagerState(**result)


def build_social_strategy(initial_state: SocialManagerState) -> SocialManagerState:
    """
    Main entry point for the social manager workflow.
    
    Guardrails:
    - If onboarding incomplete: return suggestions only
    - If no platforms selected: return suggestions only
    - Otherwise: run full multi-agent flow
    """
    smg = SocialManagerGraph()
    
    # Onboarding guardrails
    if not initial_state.is_onboarding_complete():
        initial_state = SocialManagerState(**initial_state.model_dump())
        initial_state = generate_suggestions(initial_state)
        return initial_state
    
    if not initial_state.has_platforms():
        initial_state = generate_suggestions(initial_state)
        return initial_state
    
    return smg.run(initial_state)


