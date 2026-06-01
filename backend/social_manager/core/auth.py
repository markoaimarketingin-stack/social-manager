from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from social_manager.config import settings


# JWT configuration
SECRET_KEY = getattr(settings, "jwt_secret_key", None) or os.environ.get("JWT_SECRET_KEY") or "dev_change_me"
ALGORITHM = getattr(settings, "jwt_algorithm", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getattr(settings, "jwt_exp_minutes", 60 * 24 * 7))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise


def create_state_token(data: Dict[str, Any], expires_minutes: int = 5) -> str:
    expires = timedelta(minutes=expires_minutes)
    return create_access_token(data, expires)


def verify_state_token(token: str) -> Dict[str, Any]:
    return decode_token(token)
