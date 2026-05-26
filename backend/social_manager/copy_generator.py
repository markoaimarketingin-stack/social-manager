"""
AI-Powered Copy Generation Module
Generate full post copy with A/B variations and emotional hook testing
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import logging
from social_manager.llm import client as llm_client

logger = logging.getLogger(__name__)

class CopyVariant(BaseModel):
    """A single copy variant for A/B testing."""
    variant_id: str  # A, B, C, etc
    text: str
    tone: str  # witty, sentimental, urgent, educational, etc
    length: int  # character count
    emotional_hook: str  # The emotional element
    cta_type: str  # link, comment, share, dm, etc
    predicted_performance: float = 0.0  # 0-1 prediction score


class PostCopy(BaseModel):
    """Complete post copy with multiple variants."""
    pillar: str
    platform: str
    content_type: str  # reel, carousel, text, etc
    topic: str
    primary_copy: str
    variants: List[CopyVariant] = []
    hashtag_set: List[str] = []
    emoji_set: List[str] = []
    best_posting_time: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __init__(self, **data):
        if data.get('created_at') is None:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)

class VariantsLLMSchema(BaseModel):
    variants: List[CopyVariant]

class CopyGenerator:
    """
    Generate AI-powered social media copy with variations using Groq LLM.
    """
    
    def __init__(self, brand_voice: str = "energetic", target_audience: str = "fitness enthusiasts"):
        self.brand_voice = brand_voice
        self.target_audience = target_audience
        
    async def generate_carousel_copy(self, 
                               topic: str,
                               slide_count: int = 5,
                               angle: str = None) -> List[str]:
        prompt = f"Write the copy for a {slide_count}-slide carousel post about {topic}. The angle should be {angle or 'educational'}. Ensure each slide copy is concise and separated by '---SLIDE---'."
        system = f"You are an expert social media copywriter. Your brand voice is {self.brand_voice}."
        
        response = llm_client.generate(prompt, system)
        slides = [s.strip() for s in response.split('---SLIDE---') if s.strip()]
        return slides[:slide_count]
    
    async def generate_reel_copy(self,
                          hook: str,
                          benefit: str,
                          cta: str = "Save this") -> str:
        prompt = f"Write a short, engaging caption for a short-form video (Reel/TikTok) using this hook: '{hook}', highlighting this benefit: '{benefit}', and ending with this CTA: '{cta}'. Keep it under 150 words."
        system = f"You are an expert social media copywriter. Your brand voice is {self.brand_voice}."
        
        return llm_client.generate(prompt, system)
    
    async def generate_text_post_copy(self,
                               theme: str,
                               story: str = None,
                               takeaway: str = None,
                               cta: str = "What's your biggest struggle?") -> str:
        prompt = f"Write an engaging text-only post about {theme}. {f'Include this story: {story}. ' if story else ''}{f'The main takeaway is: {takeaway}. ' if takeaway else ''}End with this CTA: {cta}."
        system = f"You are an expert social media copywriter. Your brand voice is {self.brand_voice}."
        
        return llm_client.generate(prompt, system)
    
    async def generate_copy_variants(self, 
                               topic: str,
                               content_type: str = "reel",
                               variant_count: int = 4) -> List[CopyVariant]:
        prompt = f"Generate {variant_count} distinct copy variants for a {content_type} post about {topic}. Use different emotional tones (e.g., witty, sentimental, urgent, educational, aspirational). Provide realistic predicted performance scores."
        system = f"You are an expert social media copywriter. Your brand voice is {self.brand_voice}. Output the variants in a structured format."
        
        try:
            result = await llm_client.generate_structured(prompt, VariantsLLMSchema, system_instruction=system)
            variants = result.variants[:variant_count]
            # Ensure unique IDs
            for i, v in enumerate(variants):
                v.variant_id = chr(65 + i)
            variants.sort(key=lambda x: x.predicted_performance, reverse=True)
            return variants
        except Exception as e:
            logger.error(f"Failed to generate copy variants: {e}")
            return []
    
    def generate_hashtag_set(self, topic: str, platform: str = "instagram", size: int = 15) -> List[str]:
        prompt = f"Generate a comma-separated list of {size} highly relevant and trending hashtags for a {platform} post about {topic}."
        response = llm_client.generate(prompt, "You are a social media hashtag optimizer.")
        hashtags = [h.strip() for h in response.split(',') if h.strip()]
        # ensure they start with #
        hashtags = [h if h.startswith('#') else f'#{h}' for h in hashtags]
        return hashtags[:size]
    
    async def generate_complete_post_copy(self,
                                   pillar: str,
                                   platform: str,
                                   topic: str,
                                   create_variants: bool = True) -> PostCopy:
        if platform == "instagram" and "reel" in pillar.lower():
            primary_copy = await self.generate_reel_copy(
                hook=f"Stop doing {topic} the wrong way",
                benefit=f"Here is how to do {topic} right",
                cta="Save this for later"
            )
        else:
            primary_copy = await self.generate_text_post_copy(
                theme=topic,
                takeaway="The real difference isn't talent, it's method.",
            )
        
        variants = []
        if create_variants:
            variants = await self.generate_copy_variants(topic, platform)
            
        hashtags = self.generate_hashtag_set(topic, platform)
        
        post_copy = PostCopy(
            pillar=pillar,
            platform=platform,
            content_type="reel" if "reel" in pillar.lower() else "carousel",
            topic=topic,
            primary_copy=primary_copy,
            variants=variants,
            hashtag_set=hashtags,
            best_posting_time="6 PM EST (when your audience is most active)",
        )
        
        return post_copy
    
    def generate_copy_guidance(self, platform: str, content_type: str) -> Dict:
        return {
            "hook": "0-3 seconds - hook or lose them",
            "copy_placement": "First line of caption",
            "optimal_length": "Shorter is usually better",
            "cta": "Include a clear CTA",
            "hashtag_count": "Use relevant hashtags",
        }


def get_copy_generator(brand_voice: str = "energetic") -> CopyGenerator:
    """Factory function for copy generation."""
    return CopyGenerator(brand_voice)
