"""
Authentication and OAuth routers for multi-tenant social media management.
Implements OAuth 2.0 token exchange for Facebook, Instagram, LinkedIn, X, and YouTube.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import urllib.parse
import uuid
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from social_manager.config import settings
from social_manager.db import SessionLocal, SocialConnectionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(request: Request) -> int:
    """Extract user_id from a bearer JWT or from the OAuth-init query param."""
    token = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]

    if not token:
        token = request.query_params.get("user_id")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        from social_manager.routers.users import ALGORITHM, SECRET_KEY

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


SUPPORTED_PROVIDERS = {
    "facebook": {
        "label": "Facebook Page",
        "required": ["FACEBOOK_APP_ID", "FACEBOOK_APP_SECRET"],
        "configured": lambda: bool(settings.facebook_app_id and settings.facebook_app_secret),
        "env_token_configured": lambda: bool(settings.facebook_access_token and settings.facebook_page_id),
    },
    "instagram": {
        "label": "Instagram",
        "required": ["FACEBOOK_APP_ID", "FACEBOOK_APP_SECRET"],
        "configured": lambda: bool(settings.facebook_app_id and settings.facebook_app_secret),
        "env_token_configured": lambda: bool(settings.instagram_access_token and settings.instagram_business_account_id),
    },
    "linkedin": {
        "label": "LinkedIn",
        "required": ["LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET"],
        "configured": lambda: bool(settings.linkedin_client_id and settings.linkedin_client_secret),
        "env_token_configured": lambda: bool(settings.linkedin_access_token),
    },
    "x": {
        "label": "X / Twitter",
        "required": ["TWITTER_API_KEY", "TWITTER_API_SECRET"],
        "configured": lambda: bool(settings.twitter_api_key and settings.twitter_api_secret),
        "env_token_configured": lambda: False,
    },
    "youtube": {
        "label": "YouTube",
        "required": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"],
        "configured": lambda: bool(settings.google_client_id and settings.google_client_secret),
        "env_token_configured": lambda: False,
    },
}


def frontend_redirect(params: dict[str, str]) -> RedirectResponse:
    return RedirectResponse(f"{settings.frontend_url}/connect?{urllib.parse.urlencode(params)}")


def provider_config_redirect(platform: str) -> RedirectResponse:
    provider = SUPPORTED_PROVIDERS[platform]
    return frontend_redirect(
        {
            "error": "provider_config",
            "platform": platform,
            "description": f"{provider['label']} is not configured. Add {', '.join(provider['required'])} to backend .env.",
        }
    )


async def import_env_connection(platform: str, user_id: int, db: Session) -> RedirectResponse:
    """Create/update a user connection from legacy env tokens when OAuth app keys are not ready."""
    access_token = None
    refresh_token = None
    access_token_secret = None
    expires_at = None
    platform_account_id = None
    platform_account_name = None

    async with httpx.AsyncClient(timeout=20.0) as client:
        if platform == "facebook":
            access_token = settings.facebook_access_token
            platform_account_id = settings.facebook_page_id
            platform_account_name = "Facebook Page"
            page_resp = await client.get(
                f"https://graph.facebook.com/v18.0/{platform_account_id}",
                params={"fields": "name", "access_token": access_token},
            )
            if page_resp.status_code == 200:
                platform_account_name = page_resp.json().get("name") or platform_account_name
            else:
                return frontend_redirect(
                    {
                        "error": "env_token_invalid",
                        "platform": platform,
                        "description": "FACEBOOK_ACCESS_TOKEN or FACEBOOK_PAGE_ID could not be verified.",
                    }
                )

        elif platform == "instagram":
            access_token = settings.instagram_access_token
            platform_account_id = settings.instagram_business_account_id
            platform_account_name = "Instagram Business"
            ig_resp = await client.get(
                f"https://graph.facebook.com/v18.0/{platform_account_id}",
                params={"fields": "username,name", "access_token": access_token},
            )
            if ig_resp.status_code == 200:
                data = ig_resp.json()
                platform_account_name = data.get("username") or data.get("name") or platform_account_name
            else:
                return frontend_redirect(
                    {
                        "error": "env_token_invalid",
                        "platform": platform,
                        "description": "INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_BUSINESS_ACCOUNT_ID could not be verified.",
                    }
                )

        elif platform == "linkedin":
            access_token = settings.linkedin_access_token
            platform_account_name = "LinkedIn"
            me_resp = await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if me_resp.status_code == 200:
                data = me_resp.json()
                platform_account_id = data.get("sub")
                platform_account_name = data.get("name") or platform_account_name
            else:
                return frontend_redirect(
                    {
                        "error": "env_token_invalid",
                        "platform": platform,
                        "description": "LINKEDIN_ACCESS_TOKEN could not be verified.",
                    }
                )

    if not access_token:
        return provider_config_redirect(platform)

    social_repo = SocialConnectionRepository(db)
    existing = social_repo.get_user_connection(user_id, platform)
    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.access_token_secret = access_token_secret
        existing.platform_account_id = platform_account_id
        existing.platform_account_name = platform_account_name
        existing.expires_at = expires_at
        existing.updated_at = datetime.utcnow()
        db.commit()
    else:
        social_repo.create(
            user_id=user_id,
            platform=platform,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_secret=access_token_secret,
            platform_account_id=platform_account_id,
            platform_account_name=platform_account_name,
            expires_at=expires_at,
        )

    return frontend_redirect({"connected": platform, "success": "true", "source": "env"})


def pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


@router.get("/providers")
def get_auth_providers():
    """Return OAuth provider readiness for the connection UI."""
    return {
        "providers": [
            {
                "platform": platform,
                "label": meta["label"],
                "configured": meta["configured"]() or meta["env_token_configured"](),
                "oauth_configured": meta["configured"](),
                "env_token_configured": meta["env_token_configured"](),
                "required_env": meta["required"],
            }
            for platform, meta in SUPPORTED_PROVIDERS.items()
        ]
    }


@router.get("/{platform}/connect")
async def connect_platform(platform: str, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Start the OAuth flow for the requested platform."""
    platform = platform.lower()
    if platform not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    if not SUPPORTED_PROVIDERS[platform]["configured"]():
        if SUPPORTED_PROVIDERS[platform]["env_token_configured"]():
            return await import_env_connection(platform, user_id, db)
        return provider_config_redirect(platform)

    redirect_uri = f"{settings.backend_url}/api/auth/{platform}/callback"
    state = f"{user_id}_{uuid.uuid4().hex}"

    if platform in ("facebook", "instagram"):
        params = {
            "client_id": settings.facebook_app_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": (
                "pages_manage_posts,pages_read_engagement,pages_show_list,"
                "instagram_basic,instagram_content_publish,business_management"
            ),
        }
        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urllib.parse.urlencode(params)}"

    elif platform == "linkedin":
        params = {
            "response_type": "code",
            "client_id": settings.linkedin_client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": "w_member_social openid profile email",
        }
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"

    elif platform == "x":
        code_verifier = uuid.uuid4().hex + uuid.uuid4().hex
        state = f"{user_id}_{code_verifier}"
        params = {
            "response_type": "code",
            "client_id": settings.twitter_api_key,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": "tweet.read tweet.write users.read offline.access",
            "code_challenge": pkce_challenge(code_verifier),
            "code_challenge_method": "S256",
        }
        auth_url = f"https://twitter.com/i/oauth2/authorize?{urllib.parse.urlencode(params)}"

    elif platform == "youtube":
        params = {
            "response_type": "code",
            "client_id": settings.google_client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": "openid email profile https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.upload",
            "access_type": "offline",
            "prompt": "consent",
        }
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    return RedirectResponse(auth_url)


@router.get("/{platform}/callback")
async def platform_callback(
    platform: str,
    state: str,
    code: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Exchange an OAuth authorization code and save the resulting connection."""
    platform = platform.lower()
    if platform not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    if error or not code:
        logger.error("OAuth error from %s: %s - %s", platform, error, error_description)
        return frontend_redirect(
            {
                "error": error or "missing_code",
                "platform": platform,
                "description": error_description or "Authorization was cancelled.",
            }
        )

    try:
        user_id = int(state.split("_", 1)[0])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid OAuth state parameter")

    redirect_uri = f"{settings.backend_url}/api/auth/{platform}/callback"
    access_token = None
    refresh_token = None
    access_token_secret = None
    expires_at = None
    platform_account_id = None
    platform_account_name = None

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            if platform in ("facebook", "instagram"):
                token_resp = await client.get(
                    "https://graph.facebook.com/v18.0/oauth/access_token",
                    params={
                        "client_id": settings.facebook_app_id,
                        "client_secret": settings.facebook_app_secret,
                        "redirect_uri": redirect_uri,
                        "code": code,
                    },
                )
                token_resp.raise_for_status()
                short_lived_token = token_resp.json()["access_token"]

                long_lived_resp = await client.get(
                    "https://graph.facebook.com/v18.0/oauth/access_token",
                    params={
                        "grant_type": "fb_exchange_token",
                        "client_id": settings.facebook_app_id,
                        "client_secret": settings.facebook_app_secret,
                        "fb_exchange_token": short_lived_token,
                    },
                )
                long_lived_resp.raise_for_status()
                long_lived_user_token = long_lived_resp.json()["access_token"]

                pages_resp = await client.get(
                    "https://graph.facebook.com/v18.0/me/accounts",
                    params={"access_token": long_lived_user_token},
                )
                pages_resp.raise_for_status()
                pages = pages_resp.json().get("data", [])
                if not pages:
                    return frontend_redirect(
                        {
                            "error": "no_page",
                            "platform": platform,
                            "description": "No Facebook Page was found for this account.",
                        }
                    )

                if platform == "facebook":
                    page = pages[0]
                    access_token = page["access_token"]
                    platform_account_id = page["id"]
                    platform_account_name = page.get("name")
                else:
                    for page in pages:
                        ig_resp = await client.get(
                            f"https://graph.facebook.com/v18.0/{page['id']}",
                            params={
                                "fields": "name,instagram_business_account{id,username}",
                                "access_token": page["access_token"],
                            },
                        )
                        if ig_resp.status_code != 200:
                            continue
                        ig_account = ig_resp.json().get("instagram_business_account")
                        if ig_account:
                            access_token = page["access_token"]
                            platform_account_id = ig_account.get("id")
                            platform_account_name = ig_account.get("username") or ig_resp.json().get("name")
                            break

                    if not platform_account_id:
                        return frontend_redirect(
                            {
                                "error": "no_instagram_business",
                                "platform": platform,
                                "description": "No Instagram Business Account is linked to your Facebook Page.",
                            }
                        )

            elif platform == "linkedin":
                token_resp = await client.post(
                    "https://www.linkedin.com/oauth/v2/accessToken",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "client_id": settings.linkedin_client_id,
                        "client_secret": settings.linkedin_client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                token_resp.raise_for_status()
                token_data = token_resp.json()
                access_token = token_data["access_token"]
                refresh_token = token_data.get("refresh_token")
                if token_data.get("expires_in"):
                    expires_at = datetime.utcnow() + timedelta(seconds=int(token_data["expires_in"]))

                me_resp = await client.get(
                    "https://api.linkedin.com/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if me_resp.status_code == 200:
                    me_data = me_resp.json()
                    platform_account_id = me_data.get("sub")
                    platform_account_name = me_data.get("name")

            elif platform == "x":
                code_verifier = state.split("_", 1)[1] if "_" in state else ""
                data = {
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "code_verifier": code_verifier,
                }
                auth = (settings.twitter_api_key, settings.twitter_api_secret)
                token_resp = await client.post(
                    "https://api.twitter.com/2/oauth2/token",
                    data=data,
                    auth=auth,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                token_resp.raise_for_status()
                token_data = token_resp.json()
                access_token = token_data["access_token"]
                refresh_token = token_data.get("refresh_token")
                if token_data.get("expires_in"):
                    expires_at = datetime.utcnow() + timedelta(seconds=int(token_data["expires_in"]))

                user_resp = await client.get(
                    "https://api.twitter.com/2/users/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if user_resp.status_code == 200:
                    user_data = user_resp.json().get("data", {})
                    platform_account_id = user_data.get("id")
                    platform_account_name = user_data.get("username")

            elif platform == "youtube":
                token_resp = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "client_id": settings.google_client_id,
                        "client_secret": settings.google_client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                token_resp.raise_for_status()
                token_data = token_resp.json()
                access_token = token_data["access_token"]
                refresh_token = token_data.get("refresh_token")
                if token_data.get("expires_in"):
                    expires_at = datetime.utcnow() + timedelta(seconds=int(token_data["expires_in"]))

                channel_resp = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels",
                    params={"part": "snippet", "mine": "true"},
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                channel_resp.raise_for_status()
                channels = channel_resp.json().get("items", [])
                if channels:
                    channel = channels[0]
                    platform_account_id = channel.get("id")
                    platform_account_name = channel.get("snippet", {}).get("title")
                else:
                    platform_account_name = "YouTube channel"

    except httpx.HTTPStatusError as exc:
        logger.error("OAuth token exchange failed for %s: %s", platform, exc.response.text)
        return frontend_redirect(
            {
                "error": "oauth_exchange_failed",
                "platform": platform,
                "description": exc.response.text[:500],
            }
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected OAuth error for %s", platform)
        return frontend_redirect(
            {
                "error": "oauth_flow_failed",
                "platform": platform,
                "description": str(exc)[:500],
            }
        )

    if not access_token:
        return frontend_redirect(
            {
                "error": "missing_access_token",
                "platform": platform,
                "description": "Provider did not return an access token.",
            }
        )

    social_repo = SocialConnectionRepository(db)
    existing = social_repo.get_user_connection(user_id, platform)

    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.access_token_secret = access_token_secret
        existing.platform_account_id = platform_account_id
        existing.platform_account_name = platform_account_name
        existing.expires_at = expires_at
        existing.updated_at = datetime.utcnow()
        db.commit()
        logger.info("Updated %s connection for user %s", platform, user_id)
    else:
        social_repo.create(
            user_id=user_id,
            platform=platform,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_secret=access_token_secret,
            platform_account_id=platform_account_id,
            platform_account_name=platform_account_name,
            expires_at=expires_at,
        )
        logger.info("Saved new %s connection for user %s", platform, user_id)

    return frontend_redirect({"connected": platform, "success": "true"})


@router.get("/connections")
def get_user_connections(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Return all social accounts connected by the logged-in user."""
    social_repo = SocialConnectionRepository(db)
    connections = social_repo.get_user_connections(user_id)
    return [
        {
            "platform": connection.platform,
            "account_name": connection.platform_account_name,
            "account_id": connection.platform_account_id,
            "connected": True,
            "connected_at": connection.created_at.isoformat() if connection.created_at else None,
        }
        for connection in connections
    ]


@router.delete("/{platform}/disconnect")
def disconnect_platform(platform: str, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Remove a platform connection for the logged-in user."""
    social_repo = SocialConnectionRepository(db)
    conn = social_repo.get_user_connection(user_id, platform.lower())
    if not conn:
        raise HTTPException(status_code=404, detail=f"No {platform} connection found")
    db.delete(conn)
    db.commit()
    logger.info("Disconnected %s for user %s", platform, user_id)
    return {"disconnected": platform, "user_id": user_id}
