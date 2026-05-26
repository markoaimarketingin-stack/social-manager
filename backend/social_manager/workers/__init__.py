"""
Worker initialization and lifecycle management.
"""

import logging
from social_manager.workers.queue import publishing_queue, publishing_service
from social_manager.platforms import platform_hub

logger = logging.getLogger(__name__)


async def init_workers(platform_credentials: dict, sandbox_mode: bool = False):
    """
    Initialize platform adapters and start background workers.
    
    Args:
        platform_credentials: Dict with API keys for platforms
        sandbox_mode: Whether to use mock/sandbox platform adapters
    """
    logger.info("Initializing publishing workers...")
    
    # Initialize platform adapters
    platform_hub.init_adapters(platform_credentials, sandbox=sandbox_mode)
    
    # Define publish handler
    async def publish_handler(job):
        """Adapt publishing job to user's platform-specific flow."""
        from social_manager.db import SessionLocal
        from social_manager.platforms.hub import get_user_platform_hub
        
        # Instantiate adapters for this specific user
        db = SessionLocal()
        try:
            hub = get_user_platform_hub(job.user_id, db)
            adapter = hub.get_adapter(job.platform)
            if not adapter:
                raise ValueError(f"No adapter configured for platform: {job.platform}")
            
            # Prepare post
            prepared = await adapter.prepare_post(job.content, job.assets)
            
            # Publish
            result = await adapter.publish(prepared, job.scheduled_at)
            
            return result
        finally:
            db.close()
    
    # Start workers
    await publishing_queue.start_workers(publish_handler)
    logger.info("✓ Publishing workers initialized and running")


async def shutdown_workers():
    """Gracefully shutdown workers."""
    logger.info("Shutting down publishing workers...")
    await publishing_queue.stop_workers()
    logger.info("✓ Workers shut down")


__all__ = [
    "init_workers",
    "shutdown_workers",
    "publishing_service",
    "publishing_queue",
]
