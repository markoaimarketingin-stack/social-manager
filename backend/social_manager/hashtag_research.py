"""
Hashtag Research and Generation tool for optimized social media reach.
"""

import logging
from typing import List, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class HashtagDifficulty(str, Enum):
    """Hashtag competition level."""
    EASY = "easy"  # <100K posts
    MEDIUM = "medium"  # 100K-1M posts
    HARD = "hard"  # >1M posts


class HashtagResearch:
    """Research and recommend hashtags for content."""
    
    def __init__(self):
        """Initialize hashtag research tool."""
        self.hashtag_database = self._create_hashtag_database()
    
    def _create_hashtag_database(self) -> Dict[str, List[Dict]]:
        """Create hashtag research database by niche."""
        return {
            "fitness": [
                {"tag": "FitnessTips", "volume": 2400000, "growth": "rising", "difficulty": "hard"},
                {"tag": "GymLife", "volume": 1800000, "growth": "rising", "difficulty": "hard"},
                {"tag": "FitnessJourney", "volume": 1200000, "growth": "rising", "difficulty": "hard"},
                {"tag": "WorkoutMotivation", "volume": 950000, "growth": "stable", "difficulty": "hard"},
                {"tag": "FitnessGoals", "volume": 720000, "growth": "rising", "difficulty": "hard"},
                {"tag": "HealthyLifestyle", "volume": 580000, "growth": "rising", "difficulty": "hard"},
                {"tag": "FitnessTransformation", "volume": 420000, "growth": "rising", "difficulty": "medium"},
                {"tag": "FitnessMotivation", "volume": 380000, "growth": "stable", "difficulty": "medium"},
                {"tag": "TrainHard", "volume": 290000, "growth": "stable", "difficulty": "medium"},
                {"tag": "FitFam", "volume": 250000, "growth": "falling", "difficulty": "medium"},
                {"tag": "WorkoutBuddy", "volume": 180000, "growth": "stable", "difficulty": "medium"},
                {"tag": "NicheBodybuilding", "volume": 45000, "growth": "rising", "difficulty": "easy"},
            ],
            "marketing": [
                {"tag": "MarketingTips", "volume": 2800000, "growth": "rising", "difficulty": "hard"},
                {"tag": "DigitalMarketing", "volume": 2200000, "growth": "rising", "difficulty": "hard"},
                {"tag": "MarketingStrategy", "volume": 1600000, "growth": "rising", "difficulty": "hard"},
                {"tag": "ContentMarketing", "volume": 1400000, "growth": "rising", "difficulty": "hard"},
                {"tag": "SocialMediaMarketing", "volume": 1200000, "growth": "rising", "difficulty": "hard"},
                {"tag": "MarketingIdeas", "volume": 820000, "growth": "stable", "difficulty": "hard"},
                {"tag": "MarketingFunnel", "volume": 380000, "growth": "rising", "difficulty": "medium"},
                {"tag": "GrowthMarketing", "volume": 290000, "growth": "rising", "difficulty": "medium"},
                {"tag": "MarketingAgency", "volume": 210000, "growth": "stable", "difficulty": "medium"},
                {"tag": "MarketingConsultant", "volume": 95000, "growth": "rising", "difficulty": "easy"},
                {"tag": "LocalMarketingTips", "volume": 52000, "growth": "stable", "difficulty": "easy"},
            ],
            "technology": [
                {"tag": "TechTrends", "volume": 2100000, "growth": "rising", "difficulty": "hard"},
                {"tag": "WebDevelopment", "volume": 1800000, "growth": "rising", "difficulty": "hard"},
                {"tag": "AI", "volume": 2800000, "growth": "rising", "difficulty": "hard"},
                {"tag": "MachineLearning", "volume": 1400000, "growth": "rising", "difficulty": "hard"},
                {"tag": "DevOps", "volume": 580000, "growth": "rising", "difficulty": "medium"},
                {"tag": "CloudComputing", "volume": 720000, "growth": "stable", "difficulty": "medium"},
                {"tag": "DataScience", "volume": 890000, "growth": "rising", "difficulty": "hard"},
                {"tag": "Cybersecurity", "volume": 640000, "growth": "rising", "difficulty": "medium"},
                {"tag": "TechTips", "volume": 420000, "growth": "rising", "difficulty": "medium"},
                {"tag": "SoftwareDeveloper", "volume": 350000, "growth": "stable", "difficulty": "medium"},
            ],
            "lifestyle": [
                {"tag": "LifestyleContent", "volume": 3200000, "growth": "rising", "difficulty": "hard"},
                {"tag": "DailyLife", "volume": 2400000, "growth": "stable", "difficulty": "hard"},
                {"tag": "Inspiration", "volume": 2100000, "growth": "rising", "difficulty": "hard"},
                {"tag": "Mindfulness", "volume": 1600000, "growth": "rising", "difficulty": "hard"},
                {"tag": "HealthyLiving", "volume": 1200000, "growth": "rising", "difficulty": "hard"},
                {"tag": "WellnessJourney", "volume": 680000, "growth": "rising", "difficulty": "medium"},
                {"tag": "PersonalGrowth", "volume": 820000, "growth": "rising", "difficulty": "medium"},
                {"tag": "SelfCare", "volume": 1100000, "growth": "rising", "difficulty": "hard"},
                {"tag": "LifeGoals", "volume": 450000, "growth": "stable", "difficulty": "medium"},
                {"tag": "MindBodySoul", "volume": 290000, "growth": "rising", "difficulty": "medium"},
            ]
        }
    
    def research_hashtags(self, keyword: str, niche: str = "general", limit: int = 10) -> List[Dict]:
        """Research hashtags for a given keyword."""
        hashtags = self.hashtag_database.get(niche.lower(), [])
        
        # Filter by keyword
        matches = [h for h in hashtags if keyword.lower() in h["tag"].lower()]
        
        # Sort by volume (descending)
        matches = sorted(matches, key=lambda x: x["volume"], reverse=True)
        
        # Add metadata
        for h in matches:
            h["reach_potential"] = self._calculate_reach_potential(h)
            h["competition_level"] = h["difficulty"]
        
        return matches[:limit]
    
    def _calculate_reach_potential(self, hashtag: Dict) -> str:
        """Calculate reach potential based on volume and growth."""
        volume = hashtag["volume"]
        growth = hashtag["growth"]
        
        if growth == "rising" and volume < 500000:
            return "very_high"
        elif growth == "rising" or volume < 500000:
            return "high"
        elif volume < 2000000:
            return "medium"
        else:
            return "low"
    
    def generate_hashtag_strategy(
        self,
        post_topic: str,
        niche: str = "general",
        content_type: str = "post"
    ) -> Dict:
        """Generate optimal hashtag strategy for a post."""
        
        # Get relevant hashtags
        all_hashtags = self.hashtag_database.get(niche.lower(), [])
        
        # Separate by difficulty
        easy = [h for h in all_hashtags if h["difficulty"] == "easy"]
        medium = [h for h in all_hashtags if h["difficulty"] == "medium"]
        hard = [h for h in all_hashtags if h["difficulty"] == "hard"]
        
        # Sort by growth within difficulty
        easy.sort(key=lambda x: x["growth"] == "rising", reverse=True)
        medium.sort(key=lambda x: x["growth"] == "rising", reverse=True)
        hard.sort(key=lambda x: x["growth"] == "rising", reverse=True)
        
        # Build balanced strategy
        strategy = {
            "post_type": content_type,
            "niche": niche,
            "trending_hashtags": [h["tag"] for h in easy[:3]] + [h["tag"] for h in medium[:2]],
            "niche_hashtags": [h["tag"] for h in medium[:3]] + [h["tag"] for h in hard[:2]],
            "broad_hashtags": [h["tag"] for h in hard[:3]],
            "total_recommended": 8,
            "hashtag_list": "#" + " #".join(
                [h['tag'] for h in easy[:2]] +
                [h['tag'] for h in medium[:3]] +
                [h['tag'] for h in hard[:3]]
            ),
            "tips": [
                "Use 3-4 trending/easy hashtags for immediate reach",
                "Use 3-4 niche hashtags for targeted engagement",
                "Use 2-3 broad hashtags for discoverability",
                "Mix difficulty levels for balanced reach",
                f"Avoid overusing hashtags on {content_type} - stay under 30"
            ]
        }
        
        return strategy
    
    def get_trending_hashtags(self, niche: str = "general", limit: int = 5) -> List[Dict]:
        """Get currently trending hashtags in a niche."""
        hashtags = self.hashtag_database.get(niche.lower(), [])
        
        # Filter for rising trends
        trending = [h for h in hashtags if h["growth"] == "rising"]
        trending.sort(key=lambda x: x["volume"], reverse=True)
        
        return trending[:limit]
    
    def get_low_competition_hashtags(self, niche: str = "general", limit: int = 10) -> List[Dict]:
        """Get low-competition hashtags for better visibility."""
        hashtags = self.hashtag_database.get(niche.lower(), [])
        
        # Filter for easy difficulty
        easy_hashtags = [h for h in hashtags if h["difficulty"] == "easy"]
        easy_hashtags.sort(key=lambda x: x["volume"], reverse=True)
        
        return easy_hashtags[:limit]


# Singleton instance
_hashtag_research = None


def get_hashtag_research() -> HashtagResearch:
    """Get or create hashtag research instance."""
    global _hashtag_research
    if _hashtag_research is None:
        _hashtag_research = HashtagResearch()
    return _hashtag_research
