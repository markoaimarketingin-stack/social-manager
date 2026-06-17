import io
import pytest
from fastapi.testclient import TestClient
from main import app
from social_manager.routers.users import get_current_user
from social_manager.db import User, SessionLocal, Asset, Post, PublishingJob
from sqlalchemy.orm import Session

# Create a mock user
class MockUser:
    id = 1
    email = "test@demo.com"
    name = "Test User"

@pytest.fixture(autouse=True)
def override_auth():
    # Override get_current_user to return our MockUser
    app.dependency_overrides[get_current_user] = lambda: MockUser()
    yield
    app.dependency_overrides.clear()

def test_generate_hashtags():
    client = TestClient(app)
    
    # 1. Test empty description
    resp = client.post("/api/publishing/generate-hashtags", json={"description": "  ", "platform": "instagram"})
    assert resp.status_code == 400
    
    # 2. Test valid description
    resp = client.post("/api/publishing/generate-hashtags", json={"description": "fitness tips daily workout", "platform": "instagram"})
    assert resp.status_code == 200
    data = resp.json()
    assert "hashtags" in data
    assert isinstance(data["hashtags"], list)

def test_media_upload_and_publishing():
    client = TestClient(app)
    
    # 1. Upload mock files
    files = [
        ("files", ("test1.png", io.BytesIO(b"pngcontent"), "image/png")),
        ("files", ("test2.mp4", io.BytesIO(b"mp4content"), "video/mp4")),
    ]
    resp = client.post("/api/publishing/upload", files=files)
    assert resp.status_code == 200
    uploaded_assets = resp.json()
    assert len(uploaded_assets) == 2
    assert uploaded_assets[0]["file_type"] == "image"
    assert uploaded_assets[1]["file_type"] == "video"
    
    asset_ids = [asset["id"] for asset in uploaded_assets]
    
    # 2. Schedule a post with these asset IDs
    payload = {
        "platforms": ["linkedin"],
        "content": "Check out my new workout video!",
        "asset_ids": asset_ids,
        "scheduled_at": None
    }
    
    # We call schedule
    resp = client.post("/api/publishing/schedule", json=payload)
    assert resp.status_code == 200
    schedule_data = resp.json()
    assert schedule_data["status"] == "success"
    
    post_id = schedule_data["post_id"]
    job_ids = schedule_data["job_ids"]
    assert len(job_ids) == 1
    
    # 3. Verify database state
    db = SessionLocal()
    try:
        db_post = db.query(Post).filter(Post.id == post_id).first()
        assert db_post is not None
        assert db_post.asset_ids == asset_ids
        
        # Verify the background execute job logic retrieves these assets
        from social_manager.routers.publishing import execute_publishing_job
        # We can test executing it (it will fail to publish since we don't have real tokens, but we check if it runs)
        # To avoid actual HTTP calls during testing, we can verify the db asset fetching logic directly or mock user_hub.
    finally:
        db.close()
