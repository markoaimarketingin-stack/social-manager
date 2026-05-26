"""Platform integrations for social media publishing."""

from social_manager.platforms.base import PlatformAdapter, RateLimitStrategy, SandboxMode
from social_manager.platforms.instagram import InstagramAdapter
from social_manager.platforms.linkedin import LinkedInAdapter
from social_manager.platforms.x import XAdapter
from social_manager.platforms.youtube import YouTubeAdapter
from social_manager.platforms.hub import PlatformAdapterHub, platform_hub

__all__ = [
    "PlatformAdapter",
    "InstagramAdapter",
    "LinkedInAdapter",
    "XAdapter",
    "YouTubeAdapter",
    "PlatformAdapterHub",
    "platform_hub",
    "RateLimitStrategy",
    "SandboxMode",
]
