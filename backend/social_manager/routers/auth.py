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
from jose import JWTError
from sqlalchemy.orm import Session

from social_manager.config import settings
from social_manager.db import SessionLocal, SocialConnectionRepository
from social_manager.routers.users import get_current_user
from social_manager.core.auth import create_state_token, verify_state_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Use `get_current_user` dependency (returns user object) for auth-protected routes.


def is_valid_config(val: Optional[str]) -> bool:
    if not val:
        return False
    val_lower = val.lower()
    placeholders = ["your_", "change_me", "placeholder", "access_token", "page_id", "account_id", "client_id", "client_secret"]
    return not any(p in val_lower for p in placeholders)


SUPPORTED_PROVIDERS = {
    "facebook": {
        "label": "Facebook Page",
        "required": ["FACEBOOK_APP_ID", "FACEBOOK_APP_SECRET"],
        "configured": lambda: is_valid_config(settings.facebook_app_id) and is_valid_config(settings.facebook_app_secret),
        "env_token_configured": lambda: is_valid_config(settings.facebook_access_token) and is_valid_config(settings.facebook_page_id),
    },
    "instagram": {
        "label": "Instagram",
        "required": ["FACEBOOK_APP_ID", "FACEBOOK_APP_SECRET"],
        "configured": lambda: is_valid_config(settings.facebook_app_id) and is_valid_config(settings.facebook_app_secret),
        "env_token_configured": lambda: is_valid_config(settings.instagram_access_token) and is_valid_config(settings.instagram_business_account_id),
    },
    "linkedin": {
        "label": "LinkedIn",
        "required": ["LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET"],
        "configured": lambda: is_valid_config(settings.linkedin_client_id) and is_valid_config(settings.linkedin_client_secret),
        "env_token_configured": lambda: is_valid_config(settings.linkedin_access_token),
    },
    "x": {
        "label": "X / Twitter",
        "required": ["TWITTER_API_KEY", "TWITTER_API_SECRET"],
        "configured": lambda: is_valid_config(settings.twitter_api_key) and is_valid_config(settings.twitter_api_secret),
        "env_token_configured": lambda: False,
    },
    "youtube": {
        "label": "YouTube",
        "required": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"],
        "configured": lambda: is_valid_config(settings.google_client_id) and is_valid_config(settings.google_client_secret),
        "env_token_configured": lambda: False,
    },
}


def frontend_redirect(params: dict[str, str], request: Optional[Request] = None) -> RedirectResponse:
    frontend_url = settings.frontend_url.rstrip("/")
    if request:
        origins = settings.cors_origins
        referer = request.headers.get("referer")
        if referer:
            parsed = urllib.parse.urlparse(referer)
            ref_origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
            if any(ref_origin == o.rstrip("/") for o in origins):
                frontend_url = ref_origin
        elif request.headers.get("origin"):
            origin = request.headers.get("origin").rstrip("/")
            if any(origin == o.rstrip("/") for o in origins):
                frontend_url = origin
    return RedirectResponse(f"{frontend_url}/connect?{urllib.parse.urlencode(params)}")


def get_base_backend_url(request: Optional[Request] = None) -> str:
    base_url = settings.backend_url
    if request:
        forwarded_proto = request.headers.get("x-forwarded-proto", request.url.scheme)
        forwarded_host = request.headers.get("x-forwarded-host", request.url.netloc)
        if forwarded_host:
            base_url = f"{forwarded_proto}://{forwarded_host}"
        else:
            base_url = f"{request.url.scheme}://{request.url.netloc}"
    return base_url.rstrip("/")


def provider_config_redirect(platform: str, request: Optional[Request] = None) -> RedirectResponse:
    provider = SUPPORTED_PROVIDERS[platform]
    return frontend_redirect(
        {
            "error": "provider_config",
            "platform": platform,
            "description": f"{provider['label']} is not configured. Add {', '.join(provider['required'])} to backend .env.",
        },
        request=request
    )


async def import_env_connection(platform: str, user_id: int, db: Session, request: Optional[Request] = None) -> RedirectResponse:
    """Create/update a user connection from env tokens or fall back to Sandbox Mode."""
    access_token = None
    refresh_token = None
    access_token_secret = None
    expires_at = None
    platform_account_id = None
    platform_account_name = None

    # Retrieve configured tokens
    if platform == "facebook":
        access_token = settings.facebook_access_token
        platform_account_id = settings.facebook_page_id
        platform_account_name = "Facebook Page"
    elif platform == "instagram":
        access_token = settings.instagram_access_token
        platform_account_id = settings.instagram_business_account_id
        platform_account_name = "Instagram Business"
    elif platform == "linkedin":
        access_token = settings.linkedin_access_token
        platform_account_name = "LinkedIn Profile"
    elif platform == "x":
        access_token = settings.twitter_bearer_token
        platform_account_name = "X Profile"
    elif platform == "youtube":
        access_token = settings.google_api_key
        platform_account_name = "YouTube Channel"

    has_valid_token = is_valid_config(access_token)

    if has_valid_token:
        # Perform real external verification
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                if platform == "facebook" and platform_account_id:
                    page_resp = await client.get(
                        f"https://graph.facebook.com/v18.0/{platform_account_id}",
                        params={"fields": "name", "access_token": access_token},
                    )
                    if page_resp.status_code == 200:
                        platform_account_name = page_resp.json().get("name") or platform_account_name
                    else:
                        has_valid_token = False
                elif platform == "instagram" and platform_account_id:
                    ig_resp = await client.get(
                        f"https://graph.facebook.com/v18.0/{platform_account_id}",
                        params={"fields": "username,name", "access_token": access_token},
                    )
                    if ig_resp.status_code == 200:
                        data = ig_resp.json()
                        platform_account_name = data.get("username") or data.get("name") or platform_account_name
                    else:
                        has_valid_token = False
                elif platform == "linkedin":
                    me_resp = await client.get(
                        "https://api.linkedin.com/v2/userinfo",
                        headers={"Authorization": f"Bearer {access_token}"},
                    )
                    if me_resp.status_code == 200:
                        data = me_resp.json()
                        platform_account_id = data.get("sub")
                        platform_account_name = data.get("name") or platform_account_name
                    else:
                        has_valid_token = False
            except Exception:
                has_valid_token = False

    # Fall back to Sandbox Mode if token is placeholder, invalid, or API checks failed
    if not has_valid_token or not access_token:
        access_token = f"sandbox_token_{platform}"
        if platform == "facebook":
            platform_account_name = "Vivan Naik"
            platform_account_id = "vivan_naik_fb_id"
        elif platform == "instagram":
            platform_account_name = "markoaisocialmanager"
            platform_account_id = "markoaisocialmanager_ig_id"
        elif platform == "linkedin":
            platform_account_name = "Marko Ai"
            platform_account_id = "marko_ai_linkedin_id"
        else:
            platform_account_id = f"sandbox_{platform}_id"
            platform_account_name = f"{platform.capitalize()} Sandbox"

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
        # DB schema fallback uses social_repo.create() or direct inserts
        # Use DB direct model creation for safety
        from social_manager.db import SocialConnection
        db_conn = SocialConnection(
            user_id=user_id,
            platform=platform,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_secret=access_token_secret,
            platform_account_id=platform_account_id,
            platform_account_name=platform_account_name,
            expires_at=expires_at,
        )
        db.add(db_conn)
        db.commit()

    return frontend_redirect({"connected": platform, "success": "true", "source": "env" if has_valid_token else "sandbox"}, request=request)


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
async def connect_platform(
    platform: str, 
    request: Request, 
    sandbox: Optional[str] = None, 
    current_user=Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Start the OAuth flow for the requested platform."""
    platform = platform.lower()
    if platform not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    # Check if the app-level OAuth credentials (client ID and secret) are configured
    is_configured = SUPPORTED_PROVIDERS[platform]["configured"]()
    logger.info(
        "connect_platform: Checking configured status for platform '%s'. Configured: %s. "
        "App ID/Client ID present: %s, Secret present: %s.",
        platform,
        is_configured,
        bool(settings.facebook_app_id) if platform in ("facebook", "instagram") else bool(settings.linkedin_client_id) if platform == "linkedin" else False,
        bool(settings.facebook_app_secret) if platform in ("facebook", "instagram") else bool(settings.linkedin_client_secret) if platform == "linkedin" else False
    )

    if sandbox == "true" or not is_configured:
        # Always redirect to import/sandbox flow if credentials are not configured or sandbox is requested
        return await import_env_connection(platform, current_user.id, db, request=request)

    redirect_uri = f"{get_base_backend_url(request)}/api/auth/{platform}/callback"
    # create a short-lived signed state token containing the user id and a nonce
    state_payload = {"sub": str(current_user.id), "nonce": uuid.uuid4().hex}
    state = create_state_token(state_payload, expires_minutes=5)

    if platform in ("facebook", "instagram"):
        scopes = ["pages_manage_posts", "pages_read_engagement", "pages_show_list"]
        if platform == "instagram":
            scopes.extend(["instagram_basic", "instagram_content_publish"])
        params = {
            "client_id": settings.facebook_app_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": ",".join(scopes),
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
        # include PKCE verifier in the signed state token
        state_payload["cv"] = code_verifier
        state = create_state_token(state_payload, expires_minutes=5)
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
    request: Request,
    state: Optional[str] = None,
    code: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    error_message: Optional[str] = None,
    error_code: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Exchange an OAuth authorization code and save the resulting connection."""
    platform = platform.lower()
    if platform not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    if error or error_message or not code:
        err_msg = error or error_message or "missing_code"
        err_desc = error_description or error_message or (f"Authorization failed (code: {error_code})." if error_code else "Authorization was cancelled.")
        logger.error("OAuth error from %s: %s - %s", platform, err_msg, err_desc)
        return frontend_redirect(
            {
                "error": err_msg,
                "platform": platform,
                "description": err_desc,
            },
            request=request
        )

    if not state:
        logger.error("OAuth error from %s: Missing state parameter", platform)
        return frontend_redirect(
            {
                "error": "missing_state",
                "platform": platform,
                "description": "Missing OAuth state parameter.",
            },
            request=request
        )

    try:
        payload = verify_state_token(state)
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state parameter")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid OAuth state parameter")

    redirect_uri = f"{get_base_backend_url(request)}/api/auth/{platform}/callback"
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
                        },
                        request=request
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
                            },
                            request=request
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
                # retrieve PKCE code_verifier from signed state payload
                try:
                    payload = verify_state_token(state)
                    code_verifier = payload.get("cv", "")
                except Exception:
                    code_verifier = ""
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
            },
            request=request
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
            },
            request=request
        )

    if not access_token:
        return frontend_redirect(
            {
                "error": "missing_access_token",
                "platform": platform,
                "description": "Provider did not return an access token.",
            },
            request=request
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

    return frontend_redirect({"connected": platform, "success": "true"}, request=request)


@router.get("/connections")
def get_user_connections(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Return all social accounts connected by the logged-in user."""
    social_repo = SocialConnectionRepository(db)
    connections = social_repo.get_user_connections(current_user.id)
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
def disconnect_platform(platform: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Remove a platform connection for the logged-in user."""
    social_repo = SocialConnectionRepository(db)
    conn = social_repo.get_user_connection(current_user.id, platform.lower())
    if not conn:
        raise HTTPException(status_code=404, detail=f"No {platform} connection found")
    db.delete(conn)
    db.commit()
    logger.info("Disconnected %s for user %s", platform, current_user.id)
    return {"disconnected": platform, "user_id": current_user.id}
