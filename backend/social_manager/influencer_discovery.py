"""
Influencer Discovery and Analysis tool for finding relevant influencers.
"""

import os
import logging
from typing import List, Dict, Optional
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class InfluencerTier(str, Enum):
    """Influencer categorization by follower count."""
    NANO = "nano"  # 1K-10K
    MICRO = "micro"  # 10K-100K
    MID = "mid"  # 100K-1M
    MACRO = "macro"  # 1M-10M
    MEGA = "mega"  # 10M+


class InfluencerDiscovery:
    """Discover and analyze influencers for partnership opportunities."""
    
    def __init__(self):
        """Initialize influencer discovery."""
        self.database = self._create_demo_database()
    
    def _create_demo_database(self) -> List[Dict]:
        """Create demo influencer database."""
        return [
            {
                "id": 1,
                "name": "Sarah Wellness Co",
                "handle": "sarahwellnessco",
                "platform": "Instagram",
                "followers": 45000,
                "engagement_rate": 0.082,
                "niche": ["fitness", "wellness", "health"],
                "audience_age": "25-45",
                "average_likes": 3200,
                "average_comments": 580,
                "growth_rate": 0.15,
                "authenticity_score": 0.88
            },
            {
                "id": 2,
                "name": "Tech Marcus",
                "handle": "techmarcus",
                "platform": "Instagram",
                "followers": 230000,
                "engagement_rate": 0.065,
                "niche": ["technology", "startups", "AI"],
                "audience_age": "20-35",
                "average_likes": 14000,
                "average_comments": 2100,
                "growth_rate": 0.12,
                "authenticity_score": 0.92
            },
            {
                "id": 3,
                "name": "Lifestyle Jess",
                "handle": "stylewithjess",
                "platform": "TikTok",
                "followers": 850000,
                "engagement_rate": 0.095,
                "niche": ["lifestyle", "fashion", "beauty"],
                "audience_age": "18-30",
                "average_likes": 95000,
                "average_comments": 12000,
                "growth_rate": 0.28,
                "authenticity_score": 0.85
            },
            {
                "id": 4,
                "name": "Business Brian",
                "handle": "businessbrian",
                "platform": "LinkedIn",
                "followers": 125000,
                "engagement_rate": 0.072,
                "niche": ["business", "entrepreneurship", "marketing"],
                "audience_age": "30-55",
                "average_likes": 3500,
                "average_comments": 890,
                "growth_rate": 0.08,
                "authenticity_score": 0.94
            },
            {
                "id": 5,
                "name": "Food Finds",
                "handle": "foodfindseverywhere",
                "platform": "Instagram",
                "followers": 320000,
                "engagement_rate": 0.078,
                "niche": ["food", "travel", "lifestyle"],
                "audience_age": "22-42",
                "average_likes": 22000,
                "average_comments": 3200,
                "growth_rate": 0.18,
                "authenticity_score": 0.89
            }
        ]
    
    def search_influencers(
        self,
        niches: List[str],
        min_followers: int = 0,
        max_followers: int = 10000000,
        platform: Optional[str] = None,
        engagement_threshold: float = 0.0
    ) -> List[Dict]:
        """Search for influencers matching criteria."""
        results = []
        
        for influencer in self.database:
            # Check platform filter
            if platform and influencer["platform"].lower() != platform.lower():
                continue
            
            # Check follower range
            if not (min_followers <= influencer["followers"] <= max_followers):
                continue
            
            # Check engagement threshold
            if influencer["engagement_rate"] < engagement_threshold:
                continue
            
            # Check niche overlap
            if not any(niche.lower() in [n.lower() for n in influencer["niche"]] for niche in niches):
                continue
            
            # Add tier classification
            tier = self._get_tier(influencer["followers"])
            influencer_copy = influencer.copy()
            influencer_copy["tier"] = tier
            influencer_copy["match_score"] = self._calculate_match_score(influencer, niches)
            
            results.append(influencer_copy)
        
        # Sort by match score
        return sorted(results, key=lambda x: x["match_score"], reverse=True)
    
    def _get_tier(self, followers: int) -> str:
        """Get influencer tier based on follower count."""
        if followers < 10000:
            return InfluencerTier.NANO.value
        elif followers < 100000:
            return InfluencerTier.MICRO.value
        elif followers < 1000000:
            return InfluencerTier.MID.value
        elif followers < 10000000:
            return InfluencerTier.MACRO.value
        else:
            return InfluencerTier.MEGA.value
    
    def _calculate_match_score(self, influencer: Dict, niches: List[str]) -> float:
        """Calculate how well influencer matches target niches."""
        niche_overlap = sum(1 for niche in niches if any(niche.lower() in n.lower() for n in influencer["niche"]))
        niche_score = (niche_overlap / len(niches)) if niches else 0
        
        # Weighted score combining niche match and engagement
        match_score = (niche_score * 0.6) + (influencer["engagement_rate"] * 100 * 0.4)
        return round(match_score, 2)
    
    def get_influencer_profile(self, influencer_id: int) -> Optional[Dict]:
        """Get detailed profile for a specific influencer."""
        for inf in self.database:
            if inf["id"] == influencer_id:
                tier = self._get_tier(inf["followers"])
                inf_copy = inf.copy()
                inf_copy["tier"] = tier
                inf_copy["profile_strength"] = self._calculate_profile_strength(inf)
                inf_copy["recommendations"] = self._get_partnership_recommendations(inf)
                return inf_copy
        return None
    
    def _calculate_profile_strength(self, influencer: Dict) -> float:
        """Rate overall profile quality (0-1)."""
        factors = [
            min(influencer["followers"] / 1000000, 1.0),  # Normalized follower count
            influencer["engagement_rate"] / 0.1,  # Engagement rate
            influencer["growth_rate"],  # Growth rate
            influencer["authenticity_score"]  # Authenticity
        ]
        return round(sum(factors) / len(factors), 2)
    
    def _get_partnership_recommendations(self, influencer: Dict) -> List[str]:
        """Get partnership recommendations based on profile."""
        recs = []
        
        if influencer["engagement_rate"] > 0.08:
            recs.append("High engagement - excellent for brand awareness campaigns")
        
        if influencer["growth_rate"] > 0.2:
            recs.append("Rapidly growing - good for long-term partnerships")
        
        if influencer["authenticity_score"] > 0.9:
            recs.append("Highly authentic - ideal for trust-building campaigns")
        
        tier = self._get_tier(influencer["followers"])
        if tier in ["micro", "nano"]:
            recs.append("Micro-influencer - high ROI for targeted campaigns")
        elif tier == "macro":
            recs.append("Macro-influencer - ideal for mass reach campaigns")
        
        return recs
    
    def get_micro_influencers(
        self,
        niches: List[str],
        min_engagement: float = 0.07,
        limit: int = 10
    ) -> List[Dict]:
        """Find high-potential micro-influencers (10K-100K followers)."""
        results = self.search_influencers(
            niches,
            min_followers=10000,
            max_followers=100000,
            engagement_threshold=min_engagement
        )
        return results[:limit]
    
    def get_trending_influencers(self, niche: str, limit: int = 5) -> List[Dict]:
        """Get trending influencers in a niche (sorted by growth rate)."""
        candidates = self.search_influencers([niche])
        sorted_by_growth = sorted(candidates, key=lambda x: x["growth_rate"], reverse=True)
        return sorted_by_growth[:limit]


# Singleton instance
_influencer_discovery = None


def get_influencer_discovery() -> InfluencerDiscovery:
    """Get or create influencer discovery instance."""
    global _influencer_discovery
    if _influencer_discovery is None:
        _influencer_discovery = InfluencerDiscovery()
    return _influencer_discovery
