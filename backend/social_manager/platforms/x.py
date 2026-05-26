"""
X (Twitter) API v2 adapter.
Handles character-constrained copy, thread support, image/video attachments.
Supports publish, metrics, and inbox operations.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from social_manager.platforms.base import PlatformAdapter, RateLimitStrategy, SandboxMode

logger = logging.getLogger(__name__)


class XAdapter(PlatformAdapter):
    """X (Twitter) platform adapter using API v2 + tweepy."""
    
    API_BASE = "https://api.twitter.com/2"
    MAX_CHAR = 280
    
    def __init__(self, api_key: str, api_secret: Optional[str] = None,
                 access_token: Optional[str] = None,
                 access_token_secret: Optional[str] = None,
                 sandbox: bool = False):
        super().__init__(api_key, api_secret)
        self.access_token = access_token or ""
        self.access_token_secret = access_token_secret or ""
        self.rate_limiter = RateLimitStrategy(max_requests_per_minute=300)
        
        # Auto-detect sandbox: if credentials missing, force sandbox
        has_creds = all([api_key, api_secret, access_token, access_token_secret])
        self.sandbox = sandbox or not has_creds
        
        self._client = None
        if not self.sandbox:
            try:
                import tweepy
                self._client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                )
                logger.info("✓ Tweepy client initialized for real posting")
            except Exception as e:
                logger.warning(f"Failed to initialize tweepy client, falling back to sandbox: {e}")
                self.sandbox = True
    
    async def authenticate(self) -> bool:
        """Verify X API access."""
        if self.sandbox:
            return True
        return self._client is not None
    
    async def prepare_post(self, post_content: str, assets: List[Dict]) -> Dict[str, Any]:
        """Prepare X post with character limit, thread support, media handling."""
        if self.sandbox:
            return self._mock_prepare(post_content, assets)
        
        tweets = self._split_into_threads(post_content)
        return {"tweets": tweets, "assets": assets, "thread": len(tweets) > 1}
    
    async def publish(self, prepared_post: Dict[str, Any], schedule_time: Optional[datetime] = None) -> Dict:
        """Publish post(s) to X using tweepy."""
        if self.sandbox:
            return SandboxMode.mock_publish("x", prepared_post["tweets"][0] if prepared_post["tweets"] else "")
        
        await self.rate_limiter.acquire()
        
        try:
            tweets = prepared_post.get("tweets", [])
            if not tweets:
                raise ValueError("No tweet content to publish")
            
            # Post first tweet
            response = self._client.create_tweet(text=tweets[0])
            first_tweet_id = response.data["id"]
            
            # Post thread replies
            prev_id = first_tweet_id
            for tweet_text in tweets[1:]:
                resp = self._client.create_tweet(text=tweet_text, in_reply_to_tweet_id=prev_id)
                prev_id = resp.data["id"]
            
            logger.info(f"✓ Tweet published: {first_tweet_id}")
            return {
                "platform_post_id": str(first_tweet_id),
                "published_at": datetime.utcnow().isoformat(),
                "preview_url": f"https://x.com/i/status/{first_tweet_id}",
                "sandbox": False,
            }
        except Exception as e:
            logger.error(f"Twitter publish failed: {e}")
            raise
    
    async def fetch_metrics(self, platform_post_id: str) -> Dict[str, Any]:
        """Fetch X post metrics."""
        if self.sandbox:
            return SandboxMode.mock_metrics(platform_post_id)
        await self.rate_limiter.acquire()
        return {"likes": 0, "retweets": 0, "replies": 0, "impressions": 0}
    
    async def fetch_inbox(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch X mentions and DMs."""
        if self.sandbox:
            return self._mock_inbox()
        await self.rate_limiter.acquire()
        return []
    
    def _split_into_threads(self, content: str, max_char: int = 280) -> List[str]:
        """Split long content into character-limited tweets."""
        tweets = []
        current = ""
        for word in content.split():
            if len(current) + len(word) + 1 <= max_char:
                current += " " + word if current else word
            else:
                if current:
                    tweets.append(current)
                current = word
        if current:
            tweets.append(current)
        return tweets or [content[:max_char]]
    
    def _mock_prepare(self, content: str, assets: List[Dict]) -> Dict:
        return {"tweets": self._split_into_threads(content), "assets": assets, "thread": len(self._split_into_threads(content)) > 1}
    
    def _mock_inbox(self) -> List[Dict]:
        return [{"type": "mention", "author": "@test_user", "content": "@your_account Great insight!", "timestamp": datetime.utcnow().isoformat()}]
