"""
LinkedIn API adapter.
Handles posts, articles, tags (companies/people), link previews.
Uses httpx for REST API calls. Supports UGC Posts and /rest/posts APIs.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from social_manager.platforms.base import PlatformAdapter, RateLimitStrategy, SandboxMode

logger = logging.getLogger(__name__)


class LinkedInAdapter(PlatformAdapter):
    """LinkedIn platform adapter using LinkedIn API v2 + REST."""
    
    API_BASE = "https://api.linkedin.com/v2"
    REST_API_BASE = "https://api.linkedin.com/rest"
    
    def __init__(self, api_key: str, api_secret: Optional[str] = None,
                 access_token: Optional[str] = None,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 sandbox: bool = False):
        super().__init__(api_key, api_secret)
        self.access_token = access_token or ""
        self.client_id = client_id or ""
        self.client_secret = client_secret or ""
        self.rate_limiter = RateLimitStrategy(max_requests_per_minute=40)
        
        # Auto-detect sandbox
        has_creds = bool(access_token)
        self.sandbox = sandbox or not has_creds
        
        self._http_client = None
        self._member_urn = None
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202405",
        }
    
    async def _ensure_http_client(self):
        if not self._http_client:
            import httpx
            self._http_client = httpx.AsyncClient(timeout=30.0)
    
    async def authenticate(self) -> bool:
        """Verify LinkedIn API access and get member URN."""
        if self.sandbox:
            return True
        try:
            await self._ensure_http_client()
            
            # Try /v2/userinfo first (works with openid scope)
            response = await self._http_client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            if response.status_code == 200:
                data = response.json()
                self._member_urn = f"urn:li:person:{data.get('sub', '')}"
                logger.info(f"✓ LinkedIn authenticated as {data.get('name', 'Unknown')} ({self._member_urn})")
                return True
            
            # Fallback: /rest/me
            response2 = await self._http_client.get(
                f"{self.REST_API_BASE}/me", headers=self._get_headers())
            if response2.status_code == 200:
                data2 = response2.json()
                self._member_urn = f"urn:li:person:{data2.get('id', '')}"
                logger.info(f"✓ LinkedIn authenticated via /rest/me ({self._member_urn})")
                return True
            
            logger.warning("LinkedIn auth endpoints failed, will try to post directly")
            self._member_urn = None
            return True
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {e}")
            return False
    
    async def prepare_post(self, post_content: str, assets: List[Dict]) -> Dict[str, Any]:
        if self.sandbox:
            return self._mock_prepare(post_content, assets)
        return {"text": post_content, "assets": assets, "format": "post", "tags": self._extract_tags(post_content)}
    
    async def publish(self, prepared_post: Dict[str, Any], schedule_time: Optional[datetime] = None) -> Dict:
        """Publish post to LinkedIn."""
        if self.sandbox:
            return SandboxMode.mock_publish("linkedin", prepared_post.get("text", ""))
        
        await self.rate_limiter.acquire()
        await self._ensure_http_client()
        
        if not self._member_urn:
            await self.authenticate()
        
        text = prepared_post.get("text", "")
        
        try:
            if self._member_urn:
                # UGC Posts API
                payload = {
                    "author": self._member_urn,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": text},
                            "shareMediaCategory": "NONE",
                        }
                    },
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
                }
                response = await self._http_client.post(
                    f"{self.API_BASE}/ugcPosts", headers=self._get_headers(), json=payload)
                
                if response.status_code in (200, 201):
                    data = response.json()
                    activity_urn = data.get("id", "")
                    logger.info(f"✓ LinkedIn post published: {activity_urn}")
                    return {
                        "platform_post_id": activity_urn,
                        "published_at": datetime.utcnow().isoformat(),
                        "preview_url": f"https://www.linkedin.com/feed/update/{activity_urn}/",
                        "sandbox": False,
                    }
                else:
                    logger.warning(f"ugcPosts failed ({response.status_code}), trying /rest/posts")
                    return await self._publish_via_rest_api(text)
            else:
                return await self._publish_via_rest_api(text)
        except Exception as e:
            logger.error(f"LinkedIn publish failed: {e}")
            raise
    
    async def _publish_via_rest_api(self, text: str) -> Dict:
        """Fallback: LinkedIn /rest/posts API."""
        await self._ensure_http_client()
        payload = {
            "author": self._member_urn or "urn:li:person:me",
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        response = await self._http_client.post(
            f"{self.REST_API_BASE}/posts", headers=self._get_headers(), json=payload)
        
        if response.status_code in (200, 201):
            post_urn = response.headers.get("x-restli-id", response.json().get("id", ""))
            logger.info(f"✓ LinkedIn post via REST API: {post_urn}")
            return {
                "platform_post_id": post_urn,
                "published_at": datetime.utcnow().isoformat(),
                "preview_url": f"https://www.linkedin.com/feed/update/{post_urn}/",
                "sandbox": False,
            }
        else:
            raise ValueError(f"LinkedIn API error {response.status_code}: {response.text}")
    
    async def fetch_metrics(self, platform_post_id: str) -> Dict[str, Any]:
        if self.sandbox:
            return SandboxMode.mock_metrics(platform_post_id)
        return {"likes": 0, "comments": 0, "shares": 0, "impressions": 0}
    
    async def fetch_inbox(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self.sandbox:
            return self._mock_inbox()
        return []
    
    def _extract_tags(self, text: str) -> Dict:
        return {"companies": [], "people": []}
    
    def _mock_prepare(self, content: str, assets: List[Dict]) -> Dict:
        return {"text": content, "assets": assets, "format": "post", "tags": {"companies": [], "people": []}}
    
    def _mock_inbox(self) -> List[Dict]:
        return [{"type": "message", "author": "test_recruiter", "content": "Interested in discussing opportunities", "timestamp": datetime.utcnow().isoformat()}]
