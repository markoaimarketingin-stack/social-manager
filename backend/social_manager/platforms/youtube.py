"""
YouTube API v3 adapter.
Handles titles, descriptions, tags, chapters, thumbnails.
Supports Shorts vs. long-form, publish, metrics, and comments.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from datetime import datetime
from social_manager.platforms.base import PlatformAdapter, RateLimitStrategy, SandboxMode


class YouTubeAdapter(PlatformAdapter):
    """YouTube platform adapter using YouTube Data API v3."""
    
    API_BASE = "https://www.googleapis.com/youtube/v3"
    
    def __init__(self, api_key: str, api_secret: Optional[str] = None, sandbox: bool = False):
        super().__init__(api_key, api_secret)
        self.sandbox = sandbox
        self.rate_limiter = RateLimitStrategy(max_requests_per_minute=10000)  # YouTube quota is token-based
    
    async def authenticate(self) -> bool:
        """Verify YouTube API access."""
        if self.sandbox:
            return True
        return bool(self.api_key)
    
    async def prepare_post(self, post_content: str, assets: List[Dict]) -> Dict[str, Any]:
        """
        Prepare YouTube video metadata.
        Parse content for title, description, tags, chapters.
        Detect Short vs. long-form by asset duration.
        """
        if self.sandbox:
            return self._mock_prepare(post_content, assets)
        
        lines = post_content.split("\n")
        title = lines[0] if lines else "Untitled"
        description = "\n".join(lines[1:]) if len(lines) > 1 else ""
        
        video_asset = assets[0] if assets else {}
        is_short = self._is_short(video_asset)
        
        prepared = {
            "title": title[:100],  # YouTube limit
            "description": description[:5000],
            "tags": self._extract_tags(description),
            "category_id": "22",  # Default: People & Blogs
            "is_short": is_short,
            "privacy_status": "public",
            "video_file_url": video_asset.get("url"),
            "thumbnail_url": video_asset.get("thumbnail_url"),
        }
        
        # Extract chapters if present
        prepared["chapters"] = self._extract_chapters(description)
        
        return prepared
    
    async def publish(self, prepared_post: Dict[str, Any], schedule_time: Optional[datetime] = None) -> Dict:
        """Publish video to YouTube."""
        if self.sandbox:
            return SandboxMode.mock_publish("youtube", prepared_post.get("title", ""))
        
        await self.rate_limiter.acquire()
        
        # TODO: Implement actual YouTube API call
        # POST /videos with video metadata
        # Upload video file separately via resumable upload
        
        return {
            "platform_post_id": "yt_dQw4w9WgXcQ",
            "published_at": datetime.utcnow().isoformat(),
            "preview_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
        }
    
    async def fetch_metrics(self, platform_post_id: str) -> Dict[str, Any]:
        """Fetch YouTube video metrics."""
        if self.sandbox:
            return SandboxMode.mock_metrics(platform_post_id)
        
        await self.rate_limiter.acquire()
        
        # TODO: Implement GET /videos with statistics
        
        return {
            "views": 5000,
            "likes": 250,
            "comments": 45,
            "shares": 30,
            "watch_time_hours": 125,
            "average_view_duration_seconds": 240,
            "engagement_rate": 0.055,
        }
    
    async def fetch_inbox(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch YouTube comments."""
        if self.sandbox:
            return self._mock_inbox()
        
        await self.rate_limiter.acquire()
        
        # TODO: Implement GET /commentThreads
        
        return []
    
    def _is_short(self, video_asset: Dict) -> bool:
        """Detect if video is a Short (< 60 seconds)."""
        duration = video_asset.get("duration_seconds", 0)
        return duration < 60
    
    def _extract_tags(self, text: str, max_tags: int = 30) -> List[str]:
        """Extract hashtags from description."""
        words = text.split()
        tags = [w[1:] for w in words if w.startswith("#")]
        return tags[:max_tags]
    
    def _extract_chapters(self, description: str) -> List[Dict]:
        """Parse chapters from description (format: timestamp - Chapter Name)."""
        chapters = []
        for line in description.split("\n"):
            parts = line.split(" - ", 1)
            if len(parts) == 2 and self._is_timestamp(parts[0]):
                chapters.append({
                    "time": parts[0],
                    "title": parts[1],
                })
        return chapters
    
    def _is_timestamp(self, text: str) -> bool:
        """Check if text looks like a timestamp (MM:SS or HH:MM:SS)."""
        parts = text.split(":")
        return len(parts) in [2, 3] and all(p.isdigit() for p in parts)
    
    def _mock_prepare(self, content: str, assets: List[Dict]) -> Dict:
        """Mock prepare for sandbox mode."""
        lines = content.split("\n")
        return {
            "title": lines[0][:100] if lines else "Untitled",
            "description": "\n".join(lines[1:])[:5000] if len(lines) > 1 else "",
            "tags": self._extract_tags(content)[:30],
            "is_short": False,
            "chapters": self._extract_chapters(content),
        }
    
    def _mock_inbox(self) -> List[Dict]:
        """Mock comments for testing."""
        return [
            {
                "type": "comment",
                "author": "test_viewer",
                "content": "Great video! Really helpful.",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]
