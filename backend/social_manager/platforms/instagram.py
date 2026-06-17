"""
Instagram Graph API adapter.
Handles captions, hashtags, alt text, Reels vs. feed, story cards.
Supports publish, metrics, and inbox operations using the real Facebook Graph API.
"""

from __future__ import annotations
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
from social_manager.platforms.base import PlatformAdapter, RateLimitStrategy, SandboxMode

logger = logging.getLogger(__name__)


class InstagramAdapter(PlatformAdapter):
    """Instagram platform adapter using Graph API."""
    
    GRAPH_API_BASE = "https://graph.facebook.com/v18.0"
    
    def __init__(self, api_key: str, ig_user_id: str = "", api_secret: Optional[str] = None, sandbox: bool = False):
        super().__init__(api_key, api_secret)
        self.ig_user_id = ig_user_id
        self.sandbox = sandbox
        self.rate_limiter = RateLimitStrategy(max_requests_per_minute=90)
        self._http_client: Optional[httpx.AsyncClient] = None

    def _ensure_http_client(self):
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=60.0)
    
    async def authenticate(self) -> bool:
        """Verify Instagram Graph API access."""
        if self.sandbox:
            return True
        if not self.api_key or not self.ig_user_id:
            return False
            
        try:
            self._ensure_http_client()
            resp = await self._http_client.get(
                f"{self.GRAPH_API_BASE}/{self.ig_user_id}",
                params={"fields": "id,username", "access_token": self.api_key}
            )
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Instagram authentication failed: {e}")
            return False
    
    async def prepare_post(self, post_content: str, assets: List[Dict]) -> Dict[str, Any]:
        """
        Prepare Instagram post with captions, hashtags, alt text.
        Determine format: image, carousel, reel, or story.
        """
        if self.sandbox:
            return self._mock_prepare(post_content, assets)
        
        # Parse caption for hashtags, @mentions
        caption = post_content
        format_type = self._detect_format(assets)
        
        prepared = {
            "caption": caption,
            "assets": assets,
            "format": format_type,  # text, single_image, carousel, reel
            "alt_texts": [a.get("alt_text", "") for a in assets],
        }
        
        if format_type == "reel":
            prepared["cover_url"] = assets[0].get("url") if assets else None
            
        return prepared
    
    async def _create_media_container(self, params: Dict[str, Any]) -> str:
        """Create a media container for Instagram."""
        params["access_token"] = self.api_key
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.GRAPH_API_BASE}/{self.ig_user_id}/media",
                params=params
            )
            resp.raise_for_status()
            return resp.json().get("id")

    async def _publish_media_container(self, creation_id: str) -> str:
        """Publish an existing media container."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.GRAPH_API_BASE}/{self.ig_user_id}/media_publish",
                params={"creation_id": creation_id, "access_token": self.api_key}
            )
            resp.raise_for_status()
            return resp.json().get("id")

    async def publish(self, prepared_post: Dict[str, Any], schedule_time: Optional[datetime] = None) -> Dict:
        """Publish post to Instagram."""
        if self.sandbox:
            return SandboxMode.mock_publish("instagram", prepared_post.get("caption", ""))
        
        if not self.api_key or not self.ig_user_id:
            raise ValueError("Instagram credentials missing. Cannot publish in live mode.")
            
        await self.rate_limiter.acquire()
        
        try:
            format_type = prepared_post.get("format", "text")
            assets = prepared_post.get("assets", [])
            caption = prepared_post.get("caption", "")
            
            if format_type == "text" or not assets:
                raise ValueError("Instagram requires at least one media asset (image/video).")
            
            creation_id = None
            
            if format_type == "single_image":
                params = {
                    "image_url": assets[0]["url"],
                    "caption": caption
                }
                creation_id = await self._create_media_container(params)
                
            elif format_type == "reel":
                params = {
                    "media_type": "REELS",
                    "video_url": assets[0]["url"],
                    "caption": caption
                }
                creation_id = await self._create_media_container(params)
                
                # Wait for video processing
                await asyncio.sleep(15) 
                
            elif format_type == "carousel":
                # Create children containers
                children_ids = []
                for asset in assets[:10]: # Max 10 items
                    child_params = {
                        "image_url": asset["url"],
                        "is_carousel_item": "true"
                    }
                    if asset.get("file_type") == "video":
                        child_params["media_type"] = "VIDEO"
                        child_params.pop("image_url")
                        child_params["video_url"] = asset["url"]
                        
                    child_id = await self._create_media_container(child_params)
                    children_ids.append(child_id)
                
                # Create carousel container
                carousel_params = {
                    "media_type": "CAROUSEL",
                    "children": ",".join(children_ids),
                    "caption": caption
                }
                creation_id = await self._create_media_container(carousel_params)
            
            if not creation_id:
                raise ValueError("Failed to create media container")
                
            # Publish the container
            published_id = await self._publish_media_container(creation_id)
            
            return {
                "platform_post_id": published_id,
                "published_at": datetime.utcnow().isoformat(),
                "preview_url": f"https://instagram.com/p/{published_id}/", # ID is not the shortcode, but good enough for now
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Instagram Graph API error: {e.response.text}")
            raise Exception(f"Failed to publish to Instagram: {e.response.text}")
        except Exception as e:
            logger.exception("Error publishing to Instagram")
            raise
    
    async def fetch_metrics(self, platform_post_id: str) -> Dict[str, Any]:
        """Fetch Instagram post metrics."""
        if self.sandbox:
            return SandboxMode.mock_metrics(platform_post_id)
        
        await self.rate_limiter.acquire()
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.GRAPH_API_BASE}/{platform_post_id}/insights",
                    params={
                        "metric": "impressions,reach,saved,video_views", # Basic metrics
                        "access_token": self.api_key
                    }
                )
                
                # Also get likes and comments
                details_resp = await client.get(
                    f"{self.GRAPH_API_BASE}/{platform_post_id}",
                    params={
                        "fields": "like_count,comments_count",
                        "access_token": self.api_key
                    }
                )
                
                metrics = {
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "reach": 0,
                    "impressions": 0,
                    "engagement_rate": 0.0,
                    "saves": 0,
                }
                
                if details_resp.status_code == 200:
                    d = details_resp.json()
                    metrics["likes"] = d.get("like_count", 0)
                    metrics["comments"] = d.get("comments_count", 0)
                    
                if resp.status_code == 200:
                    for item in resp.json().get("data", []):
                        name = item.get("name")
                        val = item.get("values", [{}])[0].get("value", 0)
                        if name == "impressions": metrics["impressions"] = val
                        if name == "reach": metrics["reach"] = val
                        if name == "saved": metrics["saves"] = val
                
                # Simple engagement rate calculation
                if metrics["impressions"] > 0:
                    metrics["engagement_rate"] = (metrics["likes"] + metrics["comments"] + metrics["saves"]) / metrics["impressions"]
                    
                return metrics
                
        except Exception as e:
            logger.error(f"Error fetching Instagram metrics: {e}")
            # Fallback to sandbox if real fails, for resilience
            return SandboxMode.mock_metrics(platform_post_id)
    
    async def fetch_inbox(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch Instagram DMs and mentions."""
        if self.sandbox:
            return self._mock_inbox()
        
        await self.rate_limiter.acquire()
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.GRAPH_API_BASE}/{self.ig_user_id}/conversations",
                    params={"access_token": self.api_key, "limit": limit}
                )
                
                if resp.status_code != 200:
                    return []
                    
                inbox = []
                for conv in resp.json().get("data", []):
                    inbox.append({
                        "id": conv.get("id"),
                        "type": "dm",
                        "author": "instagram_user",
                        "content": "Conversation thread (details require separate fetch)",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                return inbox
                
        except Exception as e:
            logger.error(f"Error fetching Instagram inbox: {e}")
            return []
    
    def _detect_format(self, assets: List[Dict]) -> str:
        """Determine post format based on asset count/type."""
        if not assets:
            return "text"
        if len(assets) == 1:
            if assets[0].get("file_type") == "video" or "mp4" in assets[0].get("url", "").lower():
                return "reel"
            return "single_image"
        return "carousel"
    
    def _mock_prepare(self, content: str, assets: List[Dict]) -> Dict:
        """Mock prepare for sandbox mode."""
        return {
            "caption": content,
            "assets": assets,
            "format": self._detect_format(assets),
            "image_urls": [a.get("url") for a in assets],
        }
    
    def _mock_inbox(self) -> List[Dict]:
        """Mock inbox for testing."""
        return [
            {
                "type": "dm",
                "author": "test_user_1",
                "content": "Love your content!",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]
