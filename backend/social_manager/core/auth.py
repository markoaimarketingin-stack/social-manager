from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from social_manager.config import settings


# JWT configuration
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_exp_minutes


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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"leeway": 600})
        return payload
    except JWTError as exc:
        raise


def create_state_token(data: Dict[str, Any], expires_minutes: int = 60) -> str:
    expires = timedelta(minutes=expires_minutes)
    return create_access_token(data, expires)


def verify_state_token(token: str) -> Dict[str, Any]:
    return decode_token(token)
