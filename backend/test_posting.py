import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Setup paths
sys.path.insert(0, os.path.dirname(__file__))
from social_manager.platforms.linkedin import LinkedInAdapter
from social_manager.platforms.facebook import FacebookAdapter
from social_manager.platforms.instagram import InstagramAdapter

async def test_posting():
    print("==================================================")
    print("   Live Social Media Posting Test")
    print("==================================================")
    
    # Text content to post
    text_content = "Hello! This is a test post from Social Manager backend via API! 🚀 #Testing #API"
    
    # We need an image asset for Instagram/Facebook photo post
    # Using a placeholder image for testing
    assets = [
        {
            "url": "https://images.unsplash.com/photo-1516259762381-22954d7d3ad8?q=80&w=800&auto=format&fit=crop",
            "file_type": "image",
            "alt_text": "Code on a screen"
        }
    ]

    # --- 1. LinkedIn ---
    # Skipped to avoid duplicate posts
    print("\n[LinkedIn] Skipping - checking FB and IG only")

    # --- 2. Facebook ---
    fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    fb_page_id = os.getenv("FACEBOOK_PAGE_ID", "")
    if fb_token and fb_page_id:
        print("\n[Facebook] Found credentials, attempting to post...")
        try:
            fb = FacebookAdapter(
                api_key=fb_token,
                page_id=fb_page_id,
                sandbox=False
            )
            prepared = await fb.prepare_post(text_content, assets)
            res = await fb.publish(prepared)
            print(f"✅ Facebook Success: {res}")
        except Exception as e:
            print(f"❌ Facebook Error: {e}")
    else:
        print("\n[Facebook] Skipping - no credentials found in .env")

    # --- 3. Instagram ---
    ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    ig_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    if ig_token and ig_account_id:
        print("\n[Instagram] Found credentials, attempting to post...")
        try:
            ig = InstagramAdapter(
                api_key=ig_token,
                ig_user_id=ig_account_id,
                sandbox=False
            )
            # Instagram requires an image
            prepared = await ig.prepare_post(text_content, assets)
            res = await ig.publish(prepared)
            print(f"✅ Instagram Success: {res}")
        except Exception as e:
            print(f"❌ Instagram Error: {e}")
    else:
        print("\n[Instagram] Skipping - no credentials found in .env")

if __name__ == "__main__":
    asyncio.run(test_posting())
