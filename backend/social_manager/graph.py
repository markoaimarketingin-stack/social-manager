"""
Social Manager multi-agent graph with subgraph architecture.

Agents:
- StrategyAgent: brand profiling, platform selection, pillar building
- CalendarAgent: content calendar generation
- CopyAgent: tone consistency, copy variants
- PlatformAdapterAgent: platform-specific post preparation (branching)
- PublisherAgent: manages async publishing jobs
- CommunityAgent: handles mentions, DMs, comments
- AnalyticsAgent: metrics ingestion and KPI computation
- ApprovalsComplianceAgent: mandatory approval gates, policy checks
- InfluencerAgent: influencer collaboration planning
- LocalizationAgent: locale-aware variants and schedules
- ExperimentationAgent: A/B testing setup and analysis

For MVP: simple sequential path with optional platform branching.
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


class StrategyAgentSubgraph:
    """Handles brand profiling, platform selection, pillar building."""
    
    def __init__(self):
        self.graph = StateGraph(SocialManagerState)
        self.graph.add_node("platform_strategy", self._wrap(select_platform_strategies))
        self.graph.add_node("content_pillars", self._wrap(build_content_pillars))
        
        self.graph.set_entry_point("platform_strategy")
        self.graph.add_edge("platform_strategy", "content_pillars")
        self.graph.add_edge("content_pillars", END)
        
        self.app = self.graph.compile()
    
    def _wrap(self, fn: Callable[[SocialManagerState], SocialManagerState]):
        def inner(state: dict) -> dict:
            obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
            out = fn(obj)
            return out.model_dump()
        return inner
    
    def run(self, state: SocialManagerState) -> SocialManagerState:
        result = self.app.invoke(state.model_dump())
        return SocialManagerState(**result)


class CalendarAndCopyAgentSubgraph:
    """Handles calendar generation, tone consistency, and copy variants."""
    
    def __init__(self):
        self.graph = StateGraph(SocialManagerState)
        self.graph.add_node("calendar", self._wrap(generate_monthly_calendar))
        self.graph.add_node("tone_check", self._wrap(check_tone_consistency))
        
        self.graph.set_entry_point("calendar")
        self.graph.add_edge("calendar", "tone_check")
        self.graph.add_edge("tone_check", END)
        
        self.app = self.graph.compile()
    
    def _wrap(self, fn: Callable[[SocialManagerState], SocialManagerState]):
        def inner(state: dict) -> dict:
            obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
            out = fn(obj)
            # Enrich structured_context with advanced analytics after calendar
            if fn.__name__ == "generate_monthly_calendar":
                out.structured_context["viral_hooks"] = generate_viral_hooks(out)
                out.structured_context["seasonal_opportunities"] = detect_seasonal_opportunities(out)
                out.structured_context["engagement_score"] = compute_engagement_score(out)
            return out.model_dump()
        return inner
    
    def run(self, state: SocialManagerState) -> SocialManagerState:
        result = self.app.invoke(state.model_dump())
        return SocialManagerState(**result)


class CommunityAndInfluencerAgentSubgraph:
    """Handles engagement planning, UGC, influencer collaboration, loyalty."""
    
    def __init__(self):
        self.graph = StateGraph(SocialManagerState)
        self.graph.add_node("engagement", self._wrap(plan_community_engagement))
        self.graph.add_node("ugc", self._wrap(design_ugc_campaign))
        self.graph.add_node("influencers", self._wrap(plan_influencer_collab))
        self.graph.add_node("loyalty", self._wrap(build_loyalty_strategy))
        
        self.graph.set_entry_point("engagement")
        self.graph.add_edge("engagement", "ugc")
        self.graph.add_edge("ugc", "influencers")
        self.graph.add_edge("influencers", "loyalty")
        self.graph.add_edge("loyalty", END)
        
        self.app = self.graph.compile()
    
    def _wrap(self, fn: Callable[[SocialManagerState], SocialManagerState]):
        def inner(state: dict) -> dict:
            obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
            out = fn(obj)
            return out.model_dump()
        return inner
    
    def run(self, state: SocialManagerState) -> SocialManagerState:
        result = self.app.invoke(state.model_dump())
        return SocialManagerState(**result)


class SocialManagerGraph:
    """
    Main orchestrator compiling multiple subgraphs.
    
    Flow:
    1. StrategyAgent: platform selection + pillar building
    2. CalendarAndCopyAgent: calendar generation + tone checking
    3. CommunityAndInfluencerAgent: engagement, UGC, influencers, loyalty
    4. Suggestions: final recommendations
    5. Platform branching (future): per-platform publish tasks
    """
    
    def __init__(self):
        self.graph = StateGraph(SocialManagerState)
        
        # Add subgraph nodes
        strategy_sg = StrategyAgentSubgraph()
        calendar_sg = CalendarAndCopyAgentSubgraph()
        community_sg = CommunityAndInfluencerAgentSubgraph()
        
        self.graph.add_node("strategy", self._wrap_subgraph(strategy_sg.run))
        self.graph.add_node("calendar_copy", self._wrap_subgraph(calendar_sg.run))
        self.graph.add_node("community", self._wrap_subgraph(community_sg.run))
        self.graph.add_node("suggestions", self._wrap(generate_suggestions))
        
        # Linear flow
        self.graph.set_entry_point("strategy")
        self.graph.add_edge("strategy", "calendar_copy")
        self.graph.add_edge("calendar_copy", "community")
        self.graph.add_edge("community", "suggestions")
        self.graph.add_edge("suggestions", END)
        
        self.app = self.graph.compile()
    
    def _wrap_subgraph(self, subgraph_fn):
        def inner(state: dict):
            obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
            result = subgraph_fn(obj)
            return result.model_dump()
        return inner
    
    def _wrap(self, fn: Callable[[SocialManagerState], SocialManagerState]):
        def inner(state: dict):
            obj = state if isinstance(state, SocialManagerState) else SocialManagerState(**state)
            out = fn(obj)
            return out.model_dump()
        return inner
    
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

