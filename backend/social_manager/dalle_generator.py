"""
DALL-E Image Generation for visual content creation.
Generates branded images for social media posts.
"""

import os
import logging
import base64
import asyncio
from typing import Optional, List, Dict
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class DALLEImageGenerator:
    """Generate images using OpenAI's DALL-E model."""
    
    def __init__(self):
        """Initialize DALL-E generator."""
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = "https://api.openai.com/v1/images/generations"
        self.model = "dall-e-2"
        self.session = None
        
    async def initialize(self):
        """Initialize async session."""
        self.session = aiohttp.ClientSession()
        
    async def close(self):
        """Close async session."""
        if self.session:
            await self.session.close()
    
    async def generate_image(
        self,
        prompt: str,
        style: str = "professional",
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Dict:
        """Generate a single image using DALL-E."""
        
        if not self.api_key:
            return self._get_demo_image(prompt)
        
        try:
            # Enhance prompt with style parameters
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": enhanced_prompt,
                "n": 1,
                "size": size,
                "quality": quality
            }
            
            async with self.session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    image_url = data["data"][0]["url"]
                    
                    return {
                        "success": True,
                        "image_url": image_url,
                        "prompt": prompt,
                        "size": size,
                        "model": self.model,
                        "created_at": datetime.utcnow().isoformat()
                    }
                else:
                    error_data = await resp.json()
                    logger.error(f"DALL-E API error: {error_data}")
                    return self._get_demo_image(prompt)
        
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return self._get_demo_image(prompt)
    
    def _enhance_prompt(self, prompt: str, style: str = "professional") -> str:
        """Enhance prompt with style guidance."""
        style_modifiers = {
            "professional": "professional, polished, corporate, clean, modern",
            "vibrant": "vibrant, colorful, energetic, dynamic, eye-catching",
            "minimal": "minimal, clean, simple, elegant, minimalist design",
            "playful": "playful, fun, creative, whimsical, friendly",
            "luxury": "luxury, premium, high-end, sophisticated, elegant",
            "casual": "casual, friendly, approachable, informal, welcoming"
        }
        
        modifier = style_modifiers.get(style, style_modifiers["professional"])
        return f"{prompt}, {modifier}, high quality, well-lit"
    
    def _get_demo_image(self, prompt: str) -> Dict:
        """Return demo image URL when API unavailable."""
        # Using placeholder image service
        return {
            "success": True,
            "image_url": f"https://via.placeholder.com/1024x1024?text={prompt[:30]}",
            "prompt": prompt,
            "size": "1024x1024",
            "model": "dall-e-3",
            "demo": True,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def generate_post_images(
        self,
        post_topic: str,
        brand_style: str = "professional",
        count: int = 3
    ) -> List[Dict]:
        """Generate multiple image variations for a post."""
        images = []
        
        prompts = [
            f"{post_topic} - modern style",
            f"{post_topic} - creative interpretation",
            f"{post_topic} - social media optimized"
        ]
        
        for prompt in prompts[:count]:
            image = await self.generate_image(prompt, style=brand_style)
            images.append(image)
        
        return images
    
    async def generate_thumbnail(
        self,
        title: str,
        background_concept: str = "gradient"
    ) -> Dict:
        """Generate a thumbnail image for video content."""
        prompt = f"YouTube thumbnail with title '{title}' and {background_concept} background, bold typography, attention-grabbing"
        
        return await self.generate_image(
            prompt,
            style="vibrant",
            size="1280x720",
            quality="standard"
        )
    
    async def generate_hero_image(
        self,
        campaign_theme: str,
        brand_colors: Optional[List[str]] = None
    ) -> Dict:
        """Generate a hero image for campaign landing page."""
        color_desc = f"using {', '.join(brand_colors)} color scheme" if brand_colors else "with complementary colors"
        prompt = f"Hero image for {campaign_theme} campaign, {color_desc}, professional design, high impact"
        
        return await self.generate_image(
            prompt,
            style="professional",
            size="1920x1080"
        )


# Singleton instance
_image_generator = None


def get_dalle_generator() -> DALLEImageGenerator:
    """Get or create DALL-E generator instance."""
    global _image_generator
    if _image_generator is None:
        _image_generator = DALLEImageGenerator()
    return _image_generator
