"""
Base platform adapter interface.
All platform-specific implementations inherit from this.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class PlatformAdapter(ABC):
    """
    Abstract base class for platform adapters.
    Defines interface for prepare_post, publish, fetch_metrics, fetch_inbox.
    """
    
    def __init__(self, api_key: str, api_secret: Optional[str] = None):
        """Initialize platform adapter with credentials."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.platform_name: str = self.__class__.__name__
    
    @abstractmethod
    async def prepare_post(self, post_content: str, assets: List[Dict]) -> Dict[str, Any]:
        """
        Prepare post for platform (validate, format, attach media).
        
        Args:
            post_content: Text content or caption
            assets: List of asset dicts with url, alt_text, etc.
        
        Returns:
            Formatted post ready for publishing
        """
        pass
    
    @abstractmethod
    async def publish(self, prepared_post: Dict[str, Any], schedule_time: Optional[datetime] = None) -> Dict:
        """
        Publish post immediately or schedule.
        
        Args:
            prepared_post: Output from prepare_post()
            schedule_time: Optional scheduling time
        
        Returns:
            {platform_post_id, published_at, preview_url, ...}
        """
        pass
    
    @abstractmethod
    async def fetch_metrics(self, platform_post_id: str) -> Dict[str, Any]:
        """
        Fetch post metrics (likes, comments, shares, reach, impressions).
        
        Args:
            platform_post_id: ID from platform (e.g., Instagram post ID)
        
        Returns:
            {likes, comments, shares, reach, impressions, engagement_rate, ...}
        """
        pass
    
    @abstractmethod
    async def fetch_inbox(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent mentions, DMs, and comments.
        
        Args:
            limit: Max items to return
        
        Returns:
            List of conversation items {type, author, content, timestamp, ...}
        """
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Verify API credentials and access."""
        pass


class RateLimitStrategy:
    """Backoff and rate-limiting strategy for platform APIs."""
    
    def __init__(self, max_requests_per_minute: int = 60):
        self.max_requests = max_requests_per_minute
        self.requests = []  # Timestamps
    
    async def acquire(self):
        """Wait if rate limit approaching."""
        now = datetime.utcnow()
        # Remove requests older than 1 minute
        self.requests = [ts for ts in self.requests if (now - ts).total_seconds() < 60]
        
        if len(self.requests) >= self.max_requests:
            # Sleep until oldest request is 60s old
            await asyncio.sleep(61 - (now - self.requests[0]).total_seconds())
        
        self.requests.append(datetime.utcnow())


class SandboxMode:
    """Simulate post publishing for testing without hitting real platform APIs."""
    
    @staticmethod
    def mock_publish(platform: str, content: str) -> Dict:
        """Return mock post ID and metadata for testing."""
        import uuid
        return {
            "platform_post_id": f"mock_{platform}_{uuid.uuid4().hex[:8]}",
            "published_at": datetime.utcnow().isoformat(),
            "preview_url": f"https://sandbox-preview.local/{platform}/post",
            "sandbox": True,
        }
    
    @staticmethod
    def mock_metrics(platform_post_id: str) -> Dict:
        """Return mock metrics for testing."""
        import random
        return {
            "likes": random.randint(10, 500),
            "comments": random.randint(0, 50),
            "shares": random.randint(0, 30),
            "reach": random.randint(100, 5000),
            "impressions": random.randint(200, 8000),
            "engagement_rate": round(random.uniform(0.01, 0.15), 4),
        }


import asyncio
