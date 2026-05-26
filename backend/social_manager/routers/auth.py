"""
Authentication and OAuth routers for multi-tenant social media management.
Implements real OAuth 2.0 token exchange for Facebook, Instagram, LinkedIn, and X.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import urllib.parse
import uuid
import httpx
import logging

from social_manager.db import SessionLocal, UserRepository, SocialConnectionRepository
from social_manager.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# User Identity Helper
# ---------------------------------------------------------------------------

from jose import jwt, JWTError

def get_current_user_id(request: Request) -> int:
    """
    Extract user_id from Authorization header or query param.
    Decodes the real JWT.
    """
    token = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
    
    if not token:
        token = request.query_params.get("user_id")
        
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    try:
        from social_manager.routers.users import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Dummy Login removed - use /api/users/login and /api/users/register


# ---------------------------------------------------------------------------
# OAuth – Initiate (redirect to platform)
# ---------------------------------------------------------------------------

@router.get("/{platform}/connect")
def connect_platform(platform: str, request: Request, user_id: int = Depends(get_current_user_id)):
    """
    Start the OAuth flow for the requested platform.
    Redirects the user to the platform's consent screen.
    """
    redirect_uri = f"http://localhost:{settings.port}/api/auth/{platform}/callback"
    state = f"{user_id}_{uuid.uuid4().hex}"

    if platform in ("facebook", "instagram"):
        if not settings.facebook_app_id:
            raise HTTPException(status_code=500, detail="FACEBOOK_APP_ID not configured in .env")

        params = {
            "client_id": settings.facebook_app_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": (
                "pages_manage_posts,pages_read_engagement,pages_show_list,"
                "instagram_basic,instagram_content_publish,instagram_manage_insights"
            ),
        }
        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urllib.parse.urlencode(params)}"

    elif platform == "linkedin":
        if not settings.linkedin_client_id:
            raise HTTPException(status_code=500, detail="LINKEDIN_CLIENT_ID not configured in .env")

        params = {
            "response_type": "code",
            "client_id": settings.linkedin_client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": "w_member_social r_liteprofile r_emailaddress",
        }
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"

    elif platform == "x":
        # X uses OAuth 2.0 PKCE – twitter_api_key here is the OAuth 2.0 Client ID
        if not settings.twitter_api_key:
            raise HTTPException(status_code=500, detail="TWITTER_API_KEY not configured in .env")

        code_verifier = uuid.uuid4().hex + uuid.uuid4().hex  # 64-char random string
        # Store verifier in state so callback can use it (state = user_id_verifier)
        state_with_verifier = f"{user_id}_{code_verifier}"
        params = {
            "response_type": "code",
            "client_id": settings.twitter_api_key,
            "redirect_uri": redirect_uri,
            "state": state_with_verifier,
            "scope": "tweet.read tweet.write users.read offline.access",
            "code_challenge": code_verifier,
            "code_challenge_method": "plain",
        }
        auth_url = f"https://twitter.com/i/oauth2/authorize?{urllib.parse.urlencode(params)}"

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    return RedirectResponse(auth_url)


# ---------------------------------------------------------------------------
# OAuth – Callback (exchange code for token, save to DB)
# ---------------------------------------------------------------------------

@router.get("/{platform}/callback")
async def platform_callback(
    platform: str,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth redirect, exchange auth code for access token, save to DB.
    """
    try:
        user_id = int(state.split("_")[0])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid OAuth state parameter")

    redirect_uri = f"http://localhost:{settings.port}/api/auth/{platform}/callback"
    access_token = None
    refresh_token = None
    platform_account_id = None
    platform_account_name = None
    access_token_secret = None

    try:
        async with httpx.AsyncClient() as client:

            # ----------------------------------------------------------------
            # Facebook / Instagram
            # ----------------------------------------------------------------
            if platform in ("facebook", "instagram"):
                # Step 1: Exchange code for short-lived user token
                resp = await client.get(
                    "https://graph.facebook.com/v18.0/oauth/access_token",
                    params={
                        "client_id": settings.facebook_app_id,
                        "client_secret": settings.facebook_app_secret,
                        "redirect_uri": redirect_uri,
                        "code": code,
                    }
                )
                resp.raise_for_status()
                token_data = resp.json()
                short_lived_token = token_data["access_token"]

                # Step 2: Exchange for long-lived user token
                ll_resp = await client.get(
                    "https://graph.facebook.com/v18.0/oauth/access_token",
                    params={
                        "grant_type": "fb_exchange_token",
                        "client_id": settings.facebook_app_id,
                        "client_secret": settings.facebook_app_secret,
                        "fb_exchange_token": short_lived_token,
                    }
                )
                ll_resp.raise_for_status()
                ll_data = ll_resp.json()
                long_lived_user_token = ll_data["access_token"]

                if platform == "facebook":
                    # Step 3: Get the Page access token (permanent)
                    pages_resp = await client.get(
                        "https://graph.facebook.com/v18.0/me/accounts",
                        params={"access_token": long_lived_user_token}
                    )
                    pages_resp.raise_for_status()
                    pages = pages_resp.json().get("data", [])
                    if not pages:
                        raise HTTPException(status_code=400, detail="No Facebook Pages found for this account")
                    # Use the first page; in production show a page-selection UI
                    page = pages[0]
                    access_token = page["access_token"]   # permanent page token
                    platform_account_id = page["id"]
                    platform_account_name = page.get("name")

                else:  # instagram
                    # Step 3: Get IG Business Account linked to first Page
                    pages_resp = await client.get(
                        "https://graph.facebook.com/v18.0/me/accounts",
                        params={"access_token": long_lived_user_token}
                    )
                    pages_resp.raise_for_status()
                    pages = pages_resp.json().get("data", [])
                    ig_user_id = None
                    for page in pages:
                        ig_resp = await client.get(
                            f"https://graph.facebook.com/v18.0/{page['id']}",
                            params={
                                "fields": "instagram_business_account",
                                "access_token": page["access_token"]
                            }
                        )
                        if ig_resp.status_code == 200:
                            ig_data = ig_resp.json()
                            if "instagram_business_account" in ig_data:
                                ig_user_id = ig_data["instagram_business_account"]["id"]
                                access_token = page["access_token"]
                                platform_account_id = ig_user_id
                                platform_account_name = ig_data.get("name")
                                break

                    if not ig_user_id:
                        raise HTTPException(
                            status_code=400,
                            detail="No Instagram Business Account linked to this Facebook Page"
                        )

            # ----------------------------------------------------------------
            # LinkedIn
            # ----------------------------------------------------------------
            elif platform == "linkedin":
                resp = await client.post(
                    "https://www.linkedin.com/oauth/v2/accessToken",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "client_id": settings.linkedin_client_id,
                        "client_secret": settings.linkedin_client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                resp.raise_for_status()
                token_data = resp.json()
                access_token = token_data["access_token"]
                refresh_token = token_data.get("refresh_token")

                # Get member profile
                me_resp = await client.get(
                    "https://api.linkedin.com/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if me_resp.status_code == 200:
                    me_data = me_resp.json()
                    platform_account_id = me_data.get("sub")
                    platform_account_name = me_data.get("name")

            # ----------------------------------------------------------------
            # X (Twitter) – OAuth 2.0 PKCE
            # ----------------------------------------------------------------
            elif platform == "x":
                code_verifier = state.split("_", 1)[1] if "_" in state else ""
                resp = await client.post(
                    "https://api.twitter.com/2/oauth2/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "code_verifier": code_verifier,
                    },
                    auth=(settings.twitter_api_key, settings.twitter_api_secret),
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                resp.raise_for_status()
                token_data = resp.json()
                access_token = token_data["access_token"]
                refresh_token = token_data.get("refresh_token")

                # Get user info
                user_resp = await client.get(
                    "https://api.twitter.com/2/users/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if user_resp.status_code == 200:
                    user_data = user_resp.json().get("data", {})
                    platform_account_id = user_data.get("id")
                    platform_account_name = user_data.get("username")

    except httpx.HTTPStatusError as e:
        logger.error(f"OAuth token exchange failed for {platform}: {e.response.text}")
        raise HTTPException(status_code=502, detail=f"OAuth error from {platform}: {e.response.text}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected OAuth error for {platform}: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth flow failed: {str(e)}")

    if not access_token:
        raise HTTPException(status_code=500, detail="Failed to obtain access token")

    # Save to DB
    social_repo = SocialConnectionRepository(db)
    existing = social_repo.get_user_connection(user_id, platform)

    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.access_token_secret = access_token_secret
        existing.platform_account_id = platform_account_id
        existing.platform_account_name = platform_account_name
        existing.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"✓ Updated {platform} connection for user {user_id}")
    else:
        social_repo.create(
            user_id=user_id,
            platform=platform,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_secret=access_token_secret,
            platform_account_id=platform_account_id,
            platform_account_name=platform_account_name,
        )
        logger.info(f"✓ Saved new {platform} connection for user {user_id}")

    # Redirect back to frontend settings page
    frontend_url = f"http://localhost:5173/settings?connected={platform}&success=true"
    return RedirectResponse(frontend_url)


# ---------------------------------------------------------------------------
# Get all connected accounts for the logged-in user
# ---------------------------------------------------------------------------

@router.get("/connections")
def get_user_connections(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Return all social accounts connected by the logged-in user."""
    social_repo = SocialConnectionRepository(db)
    connections = social_repo.get_user_connections(user_id)
    return [
        {
            "platform": c.platform,
            "account_name": c.platform_account_name,
            "account_id": c.platform_account_id,
            "connected": True,
            "connected_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in connections
    ]


# ---------------------------------------------------------------------------
# Disconnect a platform
# ---------------------------------------------------------------------------

@router.delete("/{platform}/disconnect")
def disconnect_platform(
    platform: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Remove a platform connection for the logged-in user."""
    social_repo = SocialConnectionRepository(db)
    conn = social_repo.get_user_connection(user_id, platform)
    if not conn:
        raise HTTPException(status_code=404, detail=f"No {platform} connection found")
    db.delete(conn)
    db.commit()
    logger.info(f"Disconnected {platform} for user {user_id}")
    return {"disconnected": platform, "user_id": user_id}
