"""Knowledge Base Context Injection for Agent Nodes

Provides utilities to fetch and inject knowledge base context into agent prompts.
"""

from typing import Optional
from social_manager.knowledge_base import KnowledgeBaseManager
import logging

logger = logging.getLogger(__name__)


class KBContextInjector:
    """Injects knowledge base context into agent decisions."""
    
    def __init__(self):
        self.kb_manager = KnowledgeBaseManager()
    
    def get_brand_voice_context(self, max_chars: int = 2000) -> str:
        """Get brand voice guidelines for tone consistency."""
        try:
            context = self.kb_manager.build_context_for_llm(
                category="brand_voice",
                max_chars=max_chars
            )
            return context if context else ""
        except Exception as e:
            logger.warning(f"Failed to get brand voice context: {e}")
            return ""
    
    def get_audience_context(self, max_chars: int = 2000) -> str:
        """Get audience insights for targeting."""
        try:
            context = self.kb_manager.build_context_for_llm(
                category="audience",
                max_chars=max_chars
            )
            return context if context else ""
        except Exception as e:
            logger.warning(f"Failed to get audience context: {e}")
            return ""
    
    def get_competitor_context(self, max_chars: int = 2000) -> str:
        """Get competitor analysis for differentiation."""
        try:
            context = self.kb_manager.build_context_for_llm(
                category="competitor",
                max_chars=max_chars
            )
            return context if context else ""
        except Exception as e:
            logger.warning(f"Failed to get competitor context: {e}")
            return ""
    
    def get_campaign_context(self, max_chars: int = 2000) -> str:
        """Get campaign briefs for strategy alignment."""
        try:
            context = self.kb_manager.build_context_for_llm(
                category="campaign",
                max_chars=max_chars
            )
            return context if context else ""
        except Exception as e:
            logger.warning(f"Failed to get campaign context: {e}")
            return ""
    
    def get_social_strategy_context(self, max_chars: int = 2000) -> str:
        """Get social strategy for content planning."""
        try:
            context = self.kb_manager.build_context_for_llm(
                category="strategy",
                max_chars=max_chars
            )
            return context if context else ""
        except Exception as e:
            logger.warning(f"Failed to get social strategy context: {e}")
            return ""
    
    def build_enriched_prompt(
        self,
        base_instruction: str,
        include_brand_voice: bool = False,
        include_audience: bool = False,
        include_competitors: bool = False,
        include_campaign: bool = False,
        include_strategy: bool = False
    ) -> str:
        """
        Build an enriched prompt with knowledge base context.
        
        Args:
            base_instruction: Base instruction for the agent
            include_*: Which contexts to include
            
        Returns:
            Enriched prompt with KB context
        """
        parts = []
        
        # Add base instruction
        parts.append(base_instruction)
        
        # Add context sections
        if include_brand_voice:
            brand_context = self.get_brand_voice_context(1500)
            if brand_context:
                parts.append("\n\n📖 **Brand Voice Guidelines:**\n" + brand_context)
        
        if include_audience:
            audience_context = self.get_audience_context(1500)
            if audience_context:
                parts.append("\n\n👥 **Target Audience Insights:**\n" + audience_context)
        
        if include_competitors:
            comp_context = self.get_competitor_context(1500)
            if comp_context:
                parts.append("\n\n🏆 **Competitive Analysis:**\n" + comp_context)
        
        if include_campaign:
            campaign_context = self.get_campaign_context(1500)
            if campaign_context:
                parts.append("\n\n📢 **Campaign Brief:**\n" + campaign_context)
        
        if include_strategy:
            strategy_context = self.get_social_strategy_context(1500)
            if strategy_context:
                parts.append("\n\n📊 **Social Strategy:**\n" + strategy_context)
        
        parts.append("\n\n---\n**Reference:** Use the above knowledge base documents to inform your recommendations.")
        
        return "".join(parts)


# Singleton instance
_injector = None


def get_injector() -> KBContextInjector:
    """Get or create the KB context injector singleton."""
    global _injector
    if _injector is None:
        _injector = KBContextInjector()
    return _injector
