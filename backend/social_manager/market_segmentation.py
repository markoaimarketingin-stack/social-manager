"""
Market Segmentation Module
Multi-persona management with dynamic segment creation based on audience data
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import logging
from social_manager.llm import client as llm_client

logger = logging.getLogger(__name__)

class AudienceSegment(BaseModel):
    """Individual audience segment within a market."""
    id: Optional[int] = None
    name: str
    description: str
    size_estimate: int  # estimated number of people
    growth_rate: float  # % growth per month
    demographics: Dict = {}  # age, gender, location, income, education, etc.
    psychographics: Dict = {}  # interests, values, lifestyle, pain points
    behaviors: Dict = {}  # purchase frequency, platform usage, content preferences
    messaging_angle: str  # How to talk to this segment
    content_preferences: List[str] = []  # reel, carousel, educational, entertaining, etc.
    primary_platform: str = "instagram"
    secondary_platforms: List[str] = []
    pain_points: List[str] = []
    goals: List[str] = []
    objections: List[str] = []
    created_at: Optional[datetime] = None
    
    def __init__(self, **data):
        if data.get('created_at') is None:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)

class SegmentLLMSchema(BaseModel):
    name: str
    description: str
    size_estimate: int
    growth_rate: float
    demographics: Dict[str, str]
    psychographics: Dict[str, str]
    behaviors: Dict[str, str]
    messaging_angle: str
    content_preferences: List[str]
    primary_platform: str
    secondary_platforms: List[str]
    pain_points: List[str]
    goals: List[str]
    objections: List[str]

class SegmentsListLLMSchema(BaseModel):
    segments: List[SegmentLLMSchema]

class MarketSegmentation:
    """
    Manage multiple audience segments with dynamic creation and analysis.
    """
    
    def __init__(self):
        self.segments: List[AudienceSegment] = []
        
    def create_segment(self, name: str, description: str, **kwargs) -> AudienceSegment:
        """Create a new audience segment."""
        segment = AudienceSegment(
            name=name,
            description=description,
            **kwargs
        )
        self.segments.append(segment)
        return segment
        
    async def generate_market_segments_for_industry(self, industry: str) -> List[AudienceSegment]:
        """Dynamically generate market segments for any industry using LLM."""
        prompt = f"""You are an expert market researcher. Generate 3 distinct, highly detailed audience segments for the {industry} industry.
For each segment provide realistic demographic, psychographic, and behavioral data. Make size_estimate a realistic large number (e.g., 1000000)."""
        
        try:
            result = await llm_client.generate_structured(prompt, SegmentsListLLMSchema)
            
            created_segments = []
            for seg_data in result.segments:
                segment = self.create_segment(**seg_data.model_dump())
                created_segments.append(segment)
            return created_segments
        except Exception as e:
            logger.error(f"Failed to generate segments: {e}")
            if industry.lower() == "fitness":
                return self.add_default_segments_for_fitness()
            return []
            
    def add_default_segments_for_fitness(self) -> List[AudienceSegment]:
        """
        Create default segments for fitness/wellness industry.
        Shows template for other industries.
        """
        segments_data = [
            {
                "name": "Gym Beginners",
                "description": "People just starting their fitness journey, aged 18-30",
                "size_estimate": 2500000,
                "growth_rate": 8.5,
                "demographics": {
                    "age_range": "18-30",
                    "gender": "Mixed (53% female)",
                    "location": "Urban/Suburban",
                    "income": "$30K-$60K",
                    "education": "Some college +",
                },
                "psychographics": {
                    "motivation": "Body confidence, dating appeal",
                    "values": "Health, self-improvement, social acceptance",
                    "lifestyle": "Busy professionals, limited time",
                    "pain_points": "Overwhelmed, no time, low confidence, don't know where to start",
                },
                "behaviors": {
                    "platform_usage": "Instagram (5hrs/day), TikTok (3hrs/day), YouTube (2hrs/day)",
                    "purchase_frequency": "High (impulse buyers)",
                    "content_preference": "Entertainment + education (reels, transformations)",
                    "decision_time": "Fast (3-5 days)",
                },
                "messaging_angle": "You got this! Starting your journey is the hardest part.",
                "content_preferences": ["reels", "before-afters", "beginner tips", "motivational"],
                "primary_platform": "instagram",
                "secondary_platforms": ["tiktok", "youtube"],
                "pain_points": [
                    "Don't know where to start",
                    "Afraid of being judged at gym",
                    "No time available",
                    "Past failed attempts",
                    "Low confidence",
                ],
                "goals": [
                    "Build confidence through fitness",
                    "Transform body in 90 days",
                    "Develop consistent habit",
                    "Feel stronger",
                ],
                "objections": [
                    "It's too hard to stick with",
                    "Can't afford a trainer",
                    "Don't have time",
                    "Already tried and failed",
                ],
            },
            {
                "name": "Career-Focused Professionals",
                "description": "30-45 year olds balancing career and wellness",
                "size_estimate": 1800000,
                "growth_rate": 5.2,
                "demographics": {
                    "age_range": "30-45",
                    "gender": "Mixed (55% male)",
                    "location": "Urban, high income areas",
                    "income": "$80K-$200K+",
                    "education": "College degree +",
                },
                "psychographics": {
                    "motivation": "Health, longevity, performance",
                    "values": "Efficiency, results, status",
                    "lifestyle": "Very busy, seeks optimization",
                    "pain_points": "Time-constrained, need efficiency",
                },
                "behaviors": {
                    "platform_usage": "LinkedIn (2hrs/day), Instagram (1.5hrs/day)",
                    "purchase_frequency": "Medium (thoughtful decision)",
                    "content_preference": "Data-driven, thought leadership, science-backed",
                    "decision_time": "Medium (7-14 days)",
                },
                "messaging_angle": "Optimize your health like you optimize your business.",
                "content_preferences": ["long-form video", "podcasts", "data viz", "case studies"],
                "primary_platform": "linkedin",
                "secondary_platforms": ["instagram", "youtube"],
                "pain_points": [
                    "No time to exercise",
                    "Stress and burnout",
                    "Desk posture issues",
                    "Can't see results fast enough",
                ],
                "goals": [
                    "Maintain health while being busy",
                    "Increase energy and focus",
                    "Lose weight efficiently",
                    "Build strength without gym time",
                ],
                "objections": [
                    "I'm too busy",
                    "It's expensive",
                    "Previous programs didn't work",
                    "Can't commit to 1-hour sessions",
                ],
            },
            {
                "name": "Community Seekers",
                "description": "People motivated by social connection and group accountability",
                "size_estimate": 950000,
                "growth_rate": 12.3,
                "demographics": {
                    "age_range": "25-50",
                    "gender": "Mixed (60% female)",
                    "location": "Mixed urban/suburban",
                    "income": "$40K-$100K",
                    "education": "High school +",
                },
                "psychographics": {
                    "motivation": "Community, belonging, accountability",
                    "values": "Social connection, support, encouragement",
                    "lifestyle": "Extroverted, group oriented",
                    "pain_points": "Motivation through groups, not solo",
                },
                "behaviors": {
                    "platform_usage": "All platforms (high engagement)",
                    "purchase_frequency": "High (community selling it)",
                    "content_preference": "User testimonials, group challenges, celebrations",
                    "decision_time": "Fast if community convinced (2-3 days)",
                },
                "messaging_angle": "You're never alone on this journey - join thousands.",
                "content_preferences": ["community features", "challenges", "testimonials", "group wins"],
                "primary_platform": "instagram",
                "secondary_platforms": ["tiktok", "facebook"],
                "pain_points": [
                    "Solo workouts feel lonely",
                    "No accountability without community",
                    "Easy to quit alone",
                    "Want to feel part of something",
                ],
                "goals": [
                    "Be part of supportive community",
                    "Succeed with accountability partners",
                    "Find friends with similar goals",
                    "Share journey with others",
                ],
                "objections": [
                    "Not sure if I'll fit in",
                    "Don't want to be judged",
                    "Previous communities felt toxic",
                    "Online community isn't real",
                ],
            },
            {
                "name": "Advanced Athletes",
                "description": "People with existing fitness foundation seeking optimization",
                "size_estimate": 650000,
                "growth_rate": 6.8,
                "demographics": {
                    "age_range": "20-55",
                    "gender": "Mixed (50/50)",
                    "location": "Urban",
                    "income": "$60K-$250K",
                    "education": "College degree +",
                },
                "psychographics": {
                    "motivation": "Mastery, peak performance, optimization",
                    "values": "Excellence, science, progression",
                    "lifestyle": "Dedicated to fitness, always learning",
                    "pain_points": "Plateaus, injury prevention, advanced programming",
                },
                "behaviors": {
                    "platform_usage": "YouTube (4hrs/day), TikTok (1.5hrs/day)",
                    "purchase_frequency": "High (invests in optimization)",
                    "content_preference": "Science-backed, advanced techniques, data",
                    "decision_time": "Slow (researches thoroughly)",
                },
                "messaging_angle": "Take your already-impressive physique to the next level.",
                "content_preferences": ["advanced programming", "nutrition science", "form breakdown"],
                "primary_platform": "youtube",
                "secondary_platforms": ["tiktok", "instagram"],
                "pain_points": [
                    "Hitting plateau",
                    "Preventing injuries",
                    "Advanced programming complexity",
                    "Balancing volume and recovery",
                ],
                "goals": [
                    "Achieve advanced physique goals",
                    "Continuously progress and break plateaus",
                    "Prevent injuries while progressing",
                    "Optimize training and nutrition",
                ],
                "objections": [
                    "Program doesn't match my goals",
                    "I already know this information",
                    "Not science-backed enough",
                    "Too basic for my level",
                ],
            },
        ]
        
        created_segments = []
        for seg_data in segments_data:
            segment = self.create_segment(**seg_data)
            created_segments.append(segment)
        
        return created_segments
    
    def segment_by_engagement_level(self) -> Dict[str, AudienceSegment]:
        """
        Dynamically segment audience by their engagement level with your content.
        """
        return {
            "highly_engaged": {
                "name": "Highly Engaged Fans",
                "description": "5%+ engagement rate, frequent interactions",
                "content_strategy": "Exclusive offers, early access, community leadership roles",
            },
            "moderately_engaged": {
                "name": "Regular Followers",
                "description": "2-5% engagement rate, consistent presence",
                "content_strategy": "Value delivery, variety, education mixed with promotion",
            },
            "low_engaged": {
                "name": "Silent Observers",
                "description": "<2% engagement rate, mostly lurking",
                "content_strategy": "Viral potential, entertainment, curiosity-driven hooks",
            },
            "dormant": {
                "name": "Dormant Followers",
                "description": "Haven't engaged in 30+ days",
                "content_strategy": "Reactivation campaigns, best hits, valuable summaries",
            },
        }
    
    def get_segment_messaging(self, segment: AudienceSegment) -> Dict:
        """Generate tailored messaging for a specific segment."""
        return {
            "segment": segment.name,
            "primary_message": segment.messaging_angle,
            "pain_point_based_messaging": [
                f"Solve: {pain}" for pain in segment.pain_points
            ],
            "goal_based_messaging": [
                f"Achieve: {goal}" for goal in segment.goals
            ],
            "objection_handling": {
                pain: f"Overcome '{pain}' with [specific benefit]"
                for pain in segment.objections
            },
        }
    
    def recommend_content_mix(self, segment: AudienceSegment) -> Dict:
        """Recommend optimal content mix for segment."""
        return {
            "segment": segment.name,
            "primary_platform": segment.primary_platform,
            "secondary_platforms": segment.secondary_platforms,
            "content_mix": {
                "entertainment": "30-40%",
                "education": "35-45%",
                "inspiration": "15-20%",
                "promotion": "5-10%",
            },
            "format_recommendations": {
                "instagram": ["reels 60%", "carousel 25%", "stories 15%"],
                "tiktok": ["short videos 70%", "trends 20%", "educational 10%"],
                "linkedin": ["thought leadership 50%", "case studies 30%", "personal 20%"],
                "youtube": ["long-form 70%", "shorts 30%"],
            },
            "posting_frequency": f"{len(segment.secondary_platforms) + 1} posts/week on primary",
            "best_times": "Based on segment platform usage patterns",
        }
    
    def get_all_segments_summary(self) -> Dict:
        """Get summary of all segments."""
        total_size = sum(s.size_estimate for s in self.segments)
        
        return {
            "total_segments": len(self.segments),
            "estimated_total_addressable_market": total_size,
            "segments": [
                {
                    "name": s.name,
                    "size": s.size_estimate,
                    "market_share": f"{(s.size_estimate/total_size)*100:.1f}%",
                    "growth_rate": f"{s.growth_rate}%",
                    "primary_platform": s.primary_platform,
                    "messaging": s.messaging_angle,
                }
                for s in self.segments
            ],
        }


# Convenience function
def get_market_segmentation() -> MarketSegmentation:
    """Factory function for market segmentation."""
    return MarketSegmentation()
