"""
Real Sentiment Analysis for social listening and comment monitoring.
Uses HuggingFace transformers for sentiment detection.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SentimentLabel(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class SentimentResult:
    """Sentiment analysis result."""
    text: str
    sentiment: SentimentLabel
    confidence: float
    score: float  # -1.0 (negative) to 1.0 (positive)
    
    
class SentimentLLMSchema(BaseModel):
    sentiment: str  # positive, negative, neutral
    confidence: float
    score: float

class RealSentimentAnalyzer:
    """Analyze sentiment of social media content."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        pass
    
    async def analyze_text(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text using LLM."""
        if not text or len(text.strip()) == 0:
            return SentimentResult(
                text=text,
                sentiment=SentimentLabel.NEUTRAL,
                confidence=0.5,
                score=0.0
            )
        
        prompt = f"Analyze the sentiment of the following social media text: '{text}'. Determine if it is positive, negative, or neutral. Provide a confidence score (0.0 to 1.0) and a sentiment score (-1.0 to 1.0)."
        
        try:
            from social_manager.llm import client as llm_client
            result = await llm_client.generate_structured(prompt, SentimentLLMSchema)
            
            sentiment_map = {
                "positive": SentimentLabel.POSITIVE,
                "negative": SentimentLabel.NEGATIVE,
                "neutral": SentimentLabel.NEUTRAL
            }
            
            return SentimentResult(
                text=text,
                sentiment=sentiment_map.get(result.sentiment.lower(), SentimentLabel.NEUTRAL),
                confidence=result.confidence,
                score=result.score
            )
        except Exception as e:
            logger.error(f"LLM Sentiment analysis failed: {e}")
            return SentimentResult(
                text=text,
                sentiment=SentimentLabel.NEUTRAL,
                confidence=0.5,
                score=0.0
            )
    
    async def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze sentiment for multiple texts."""
        results = []
        for text in texts:
            result = await self.analyze_text(text)
            results.append(result)
        return results
    
    async def analyze_comments(self, comments: List[Dict]) -> List[Dict]:
        """Analyze sentiment of social media comments."""
        analyzed = []
        
        for comment in comments:
            text = comment.get("text", "") or comment.get("content", "")
            sentiment_result = await self.analyze_text(text)
            
            analyzed.append({
                "id": comment.get("id", ""),
                "author": comment.get("author", ""),
                "text": text,
                "sentiment": sentiment_result.sentiment.value,
                "confidence": sentiment_result.confidence,
                "score": sentiment_result.score,
                "created_at": comment.get("created_at", ""),
                "platform": comment.get("platform", "unknown")
            })
        
        return analyzed
    
    async def get_sentiment_summary(self, comments: List[Dict]) -> Dict:
        """Get sentiment summary statistics."""
        analyzed = await self.analyze_comments(comments)
        
        total = len(analyzed)
        positive = sum(1 for c in analyzed if c["sentiment"] == "positive")
        negative = sum(1 for c in analyzed if c["sentiment"] == "negative")
        neutral = sum(1 for c in analyzed if c["sentiment"] == "neutral")
        
        avg_score = sum(c["score"] for c in analyzed) / total if total > 0 else 0
        
        return {
            "total_analyzed": total,
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "positive_percentage": (positive / total * 100) if total > 0 else 0,
            "negative_percentage": (negative / total * 100) if total > 0 else 0,
            "neutral_percentage": (neutral / total * 100) if total > 0 else 0,
            "average_sentiment_score": round(avg_score, 2),
            "overall_sentiment": "positive" if avg_score > 0.2 else ("negative" if avg_score < -0.2 else "neutral"),
            "comments": analyzed
        }


# Singleton instance
_sentiment_analyzer = None


def get_sentiment_analyzer() -> RealSentimentAnalyzer:
    """Get or create sentiment analyzer instance."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = RealSentimentAnalyzer()
    return _sentiment_analyzer
