"""
Facebook Page adapter using the Graph API.
Handles publishing text, photos, and videos to a Facebook Page.
Supports publish, metrics, and inbox operations.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
from social_manager.platforms.base import PlatformAdapter, RateLimitStrategy, SandboxMode

logger = logging.getLogger(__name__)


class FacebookAdapter(PlatformAdapter):
    """Facebook Page adapter using Graph API."""
    
    GRAPH_API_BASE = "https://graph.facebook.com/v18.0"
    
    def __init__(self, api_key: str, page_id: str = "", api_secret: Optional[str] = None, sandbox: bool = False):
        super().__init__(api_key, api_secret)
        self.page_id = page_id
        self.sandbox = sandbox
        self.rate_limiter = RateLimitStrategy(max_requests_per_minute=200) # Facebook limits are generally higher
    
    async def authenticate(self) -> bool:
        """Verify Facebook Graph API access."""
        if self.sandbox:
            return True
        if not self.api_key or not self.page_id:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.GRAPH_API_BASE}/{self.page_id}",
                    params={"access_token": self.api_key}
                )
                return resp.status_code == 200
        except Exception as e:
            logger.error(f"Facebook authentication failed: {e}")
            return False
    
    async def prepare_post(self, post_content: str, assets: List[Dict]) -> Dict[str, Any]:
        """
        Prepare Facebook post.
        Determine format: text, photo, video.
        """
        if self.sandbox:
            return self._mock_prepare(post_content, assets)
        
        format_type = "text"
        if assets:
            if assets[0].get("file_type") == "video" or "mp4" in assets[0].get("url", "").lower():
                format_type = "video"
            else:
                format_type = "photo"
        
        prepared = {
            "message": post_content,
            "assets": assets,
            "format": format_type,
        }
        
        return prepared
    
    async def publish(self, prepared_post: Dict[str, Any], schedule_time: Optional[datetime] = None) -> Dict:
        """Publish post to Facebook Page."""
        if self.sandbox:
            return SandboxMode.mock_publish("facebook", prepared_post.get("message", ""))
        
        if not self.api_key or not self.page_id:
            raise ValueError("Facebook credentials missing. Cannot publish in live mode.")
            
        await self.rate_limiter.acquire()
        
        try:
            format_type = prepared_post.get("format", "text")
            assets = prepared_post.get("assets", [])
            message = prepared_post.get("message", "")
            
            async with httpx.AsyncClient() as client:
                if format_type == "text":
                    endpoint = f"{self.GRAPH_API_BASE}/{self.page_id}/feed"
                    params = {"message": message, "access_token": self.api_key}
                    
                elif format_type == "photo":
                    endpoint = f"{self.GRAPH_API_BASE}/{self.page_id}/photos"
                    params = {
                        "url": assets[0]["url"],
                        "message": message,
                        "access_token": self.api_key
                    }
                    
                elif format_type == "video":
                    endpoint = f"{self.GRAPH_API_BASE}/{self.page_id}/videos"
                    params = {
                        "file_url": assets[0]["url"],
                        "description": message,
                        "access_token": self.api_key
                    }
                else:
                    raise ValueError(f"Unknown Facebook post format: {format_type}")
                
                resp = await client.post(endpoint, params=params)
                resp.raise_for_status()
                
                data = resp.json()
                published_id = data.get("id") or data.get("post_id")
                
                return {
                    "platform_post_id": published_id,
                    "published_at": datetime.utcnow().isoformat(),
                    "preview_url": f"https://facebook.com/{published_id}",
                }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Facebook Graph API error: {e.response.text}")
            raise Exception(f"Failed to publish to Facebook: {e.response.text}")
        except Exception as e:
            logger.error(f"Error publishing to Facebook: {e}")
            raise
    
    async def fetch_metrics(self, platform_post_id: str) -> Dict[str, Any]:
        """Fetch Facebook post metrics."""
        if self.sandbox:
            return SandboxMode.mock_metrics(platform_post_id)
        
        await self.rate_limiter.acquire()
        
        try:
            async with httpx.AsyncClient() as client:
                # We need to fetch reactions and comments count, plus insights
                resp = await client.get(
                    f"{self.GRAPH_API_BASE}/{platform_post_id}",
                    params={
                        "fields": "reactions.summary(total_count),comments.summary(total_count),shares",
                        "access_token": self.api_key
                    }
                )
                
                # Insights for impressions/reach
                insights_resp = await client.get(
                    f"{self.GRAPH_API_BASE}/{platform_post_id}/insights",
                    params={
                        "metric": "post_impressions,post_impressions_unique",
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
                }
                
                if resp.status_code == 200:
                    d = resp.json()
                    metrics["likes"] = d.get("reactions", {}).get("summary", {}).get("total_count", 0)
                    metrics["comments"] = d.get("comments", {}).get("summary", {}).get("total_count", 0)
                    metrics["shares"] = d.get("shares", {}).get("count", 0)
                    
                if insights_resp.status_code == 200:
                    for item in insights_resp.json().get("data", []):
                        name = item.get("name")
                        val = item.get("values", [{}])[0].get("value", 0)
                        if name == "post_impressions": metrics["impressions"] = val
                        if name == "post_impressions_unique": metrics["reach"] = val
                
                if metrics["impressions"] > 0:
                    metrics["engagement_rate"] = (metrics["likes"] + metrics["comments"] + metrics["shares"]) / metrics["impressions"]
                    
                return metrics
                
        except Exception as e:
            logger.error(f"Error fetching Facebook metrics: {e}")
            return SandboxMode.mock_metrics(platform_post_id)
    
    async def fetch_inbox(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch Facebook Page conversations."""
        if self.sandbox:
            return self._mock_inbox()
        
        await self.rate_limiter.acquire()
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.GRAPH_API_BASE}/{self.page_id}/conversations",
                    params={"access_token": self.api_key, "limit": limit}
                )
                
                if resp.status_code != 200:
                    return []
                    
                inbox = []
                for conv in resp.json().get("data", []):
                    inbox.append({
                        "id": conv.get("id"),
                        "type": "dm",
                        "author": "facebook_user",
                        "content": "Conversation thread (details require separate fetch)",
                        "timestamp": conv.get("updated_time", datetime.utcnow().isoformat()),
                    })
                return inbox
                
        except Exception as e:
            logger.error(f"Error fetching Facebook inbox: {e}")
            return []
    
    def _mock_prepare(self, content: str, assets: List[Dict]) -> Dict:
        """Mock prepare for sandbox mode."""
        format_type = "text"
        if assets:
            format_type = "photo" if not "mp4" in assets[0].get("url", "").lower() else "video"
            
        return {
            "message": content,
            "assets": assets,
            "format": format_type,
        }
    
    def _mock_inbox(self) -> List[Dict]:
        """Mock inbox for testing."""
        return [
            {
                "type": "dm",
                "author": "fb_user_1",
                "content": "Is this product available?",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]
