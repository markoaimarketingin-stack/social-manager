"""
Platform factory and hub for managing multiple platform adapters.
Now supports multi-tenant per-user dynamic initialization.
"""

import logging
from typing import Dict, Optional
from social_manager.platforms.base import PlatformAdapter
from social_manager.platforms.instagram import InstagramAdapter
from social_manager.platforms.linkedin import LinkedInAdapter
from social_manager.platforms.x import XAdapter
from social_manager.platforms.youtube import YouTubeAdapter
from social_manager.platforms.facebook import FacebookAdapter
from social_manager.db import SocialConnectionRepository

logger = logging.getLogger(__name__)


class PlatformAdapterHub:
    """
    Central hub for managing platform adapters for a specific user session.
    """
    
    SUPPORTED_PLATFORMS = ["instagram", "linkedin", "x", "youtube", "facebook"]
    
    def __init__(self):
        self.adapters: Dict[str, PlatformAdapter] = {}
        self.sandbox_mode = False
    
    def register_adapter(self, platform: str, adapter: PlatformAdapter):
        """Register a platform adapter."""
        if platform.lower() not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        self.adapters[platform.lower()] = adapter
    
    def get_adapter(self, platform: str) -> Optional[PlatformAdapter]:
        """Get adapter for platform."""
        return self.adapters.get(platform.lower())
    
    def init_adapters(self, credentials: Dict[str, str], sandbox: bool = False):
        """
        Initialize all adapters with provided credentials (legacy/fallback mode).
        """
        self.sandbox_mode = sandbox
        
        # Twitter/X
        self.register_adapter("x", XAdapter(
            api_key=credentials.get("twitter_api_key", ""),
            api_secret=credentials.get("twitter_api_secret", ""),
            access_token=credentials.get("twitter_access_token", ""),
            access_token_secret=credentials.get("twitter_access_token_secret", ""),
            sandbox=sandbox,
        ))
        
        # LinkedIn
        self.register_adapter("linkedin", LinkedInAdapter(
            api_key=credentials.get("linkedin_client_id", ""),
            api_secret=credentials.get("linkedin_client_secret", ""),
            access_token=credentials.get("linkedin_access_token", ""),
            client_id=credentials.get("linkedin_client_id", ""),
            client_secret=credentials.get("linkedin_client_secret", ""),
            sandbox=sandbox,
        ))
        
        # Instagram
        self.register_adapter("instagram", InstagramAdapter(
            api_key=credentials.get("instagram_access_token", ""),
            ig_user_id=credentials.get("instagram_business_account_id", ""),
            sandbox=sandbox or not credentials.get("instagram_access_token"),
        ))
        
        # Facebook
        self.register_adapter("facebook", FacebookAdapter(
            api_key=credentials.get("facebook_access_token", ""),
            page_id=credentials.get("facebook_page_id", ""),
            sandbox=sandbox or not credentials.get("facebook_access_token"),
        ))
        
        # YouTube
        self.register_adapter("youtube", YouTubeAdapter(
            api_key=credentials.get("youtube_api_key", ""),
            sandbox=True,  # Always sandbox until implemented
        ))
    
    def get_platform_status(self) -> Dict:
        """Get connection status for all platforms in this hub."""
        status = {}
        for platform_name in self.SUPPORTED_PLATFORMS:
            adapter = self.adapters.get(platform_name)
            if adapter:
                is_sandbox = getattr(adapter, "sandbox", True)
                status[platform_name] = {
                    "platform": platform_name,
                    "connected": not is_sandbox,
                    "mode": "sandbox" if is_sandbox else "live",
                }
            else:
                status[platform_name] = {"platform": platform_name, "connected": False, "mode": "sandbox"}
        return status
    
    async def prepare_post_for_platform(self, platform: str, content: str, assets: list) -> Dict:
        adapter = self.get_adapter(platform)
        if not adapter:
            raise ValueError(f"No adapter for platform: {platform}")
        return await adapter.prepare_post(content, assets)
    
    async def publish_to_platform(self, platform: str, prepared_post: Dict, schedule_time=None) -> Dict:
        adapter = self.get_adapter(platform)
        if not adapter:
            raise ValueError(f"No adapter for platform: {platform}")
        return await adapter.publish(prepared_post, schedule_time)
    
    async def fetch_platform_metrics(self, platform: str, platform_post_id: str) -> Dict:
        adapter = self.get_adapter(platform)
        if not adapter:
            raise ValueError(f"No adapter for platform: {platform}")
        return await adapter.fetch_metrics(platform_post_id)
    
    async def fetch_platform_inbox(self, platform: str, limit: int = 50) -> list:
        adapter = self.get_adapter(platform)
        if not adapter:
            raise ValueError(f"No adapter for platform: {platform}")
        return await adapter.fetch_inbox(limit)


def get_user_platform_hub(user_id: int, db_session) -> PlatformAdapterHub:
    """
    Factory function to instantiate a PlatformAdapterHub for a specific user
    using their stored OAuth credentials.
    """
    hub = PlatformAdapterHub()
    repo = SocialConnectionRepository(db_session)
    connections = repo.get_user_connections(user_id)
    
    # Pre-fill with sandbox/empty adapters
    hub.init_adapters({}, sandbox=True)
    
    from social_manager.config import settings
    
    for conn in connections:
        if conn.platform == "facebook":
            hub.register_adapter("facebook", FacebookAdapter(
                api_key=conn.access_token,
                page_id=conn.platform_account_id or "",
                sandbox=False
            ))
        elif conn.platform == "instagram":
            hub.register_adapter("instagram", InstagramAdapter(
                api_key=conn.access_token,
                ig_user_id=conn.platform_account_id or "",
                sandbox=False
            ))
        elif conn.platform == "x":
            hub.register_adapter("x", XAdapter(
                api_key=settings.twitter_api_key or "",
                api_secret=settings.twitter_api_secret or "",
                access_token=conn.access_token,
                access_token_secret=conn.access_token_secret or "",
                sandbox=False
            ))
        elif conn.platform == "linkedin":
            hub.register_adapter("linkedin", LinkedInAdapter(
                api_key=settings.linkedin_client_id or "",
                api_secret=settings.linkedin_client_secret or "",
                access_token=conn.access_token,
                client_id=settings.linkedin_client_id or "",
                client_secret=settings.linkedin_client_secret or "",
                sandbox=False
            ))
            
    return hub

# Legacy global singleton (only used for non-user-specific tasks or startup validation)
platform_hub = PlatformAdapterHub()
