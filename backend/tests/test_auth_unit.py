from fastapi.testclient import TestClient
from main import app
from social_manager.core.auth import create_state_token, verify_state_token, decode_token, create_access_token
from jose import jwt

def test_state_token_flow():
    # 1. Test encoding a state token with a string subject (sub)
    payload = {"sub": "123", "nonce": "abc"}
    token = create_state_token(payload, expires_minutes=5)
    
    # 2. Test verifying it. This should succeed now because sub is a string
    decoded = verify_state_token(token)
    assert decoded["sub"] == "123"
    assert decoded["nonce"] == "abc"

def test_decode_token_leeway_options():
    # 1. Test decode_token works with options instead of TypeError
    payload = {"sub": "456", "exp": 9999999999}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded["sub"] == "456"

def test_dynamic_redirect_uri():
    # We can import get_base_backend_url and test it directly with a mock Request.
    from social_manager.routers.auth import get_base_backend_url
    
    # Mock request object
    class MockRequest:
        def __init__(self, headers, scheme="http", netloc="localhost:8088"):
            self.headers = headers
            class MockUrl:
                def __init__(self, scheme, netloc):
                    self.scheme = scheme
                    self.netloc = netloc
            self.url = MockUrl(scheme, netloc)
            
    # Test case A: fallback to settings.backend_url when request is None
    from social_manager.config import settings
    assert get_base_backend_url(None) == settings.backend_url.rstrip("/")
    
    # Test case B: resolve base URL from request headers (x-forwarded-host)
    req = MockRequest(headers={"x-forwarded-host": "social-manager-1.onrender.com", "x-forwarded-proto": "https"})
    assert get_base_backend_url(req) == "https://social-manager-1.onrender.com"
    
    # Test case C: fallback to request URL scheme/netloc if headers are missing
    req2 = MockRequest(headers={}, scheme="http", netloc="localhost:8088")
    assert get_base_backend_url(req2) == "http://localhost:8088"
