from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.core.config import settings
from app.db.base import Base, import_models
from app.db.session import close_engine
from app.main import app


def test_strategy_planning_and_review_flow() -> None:
    database_path = Path(".test-data/product-flow.db")
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()
    settings.database_url = f"sqlite:///{database_path}"

    import_models()
    sync_engine = create_engine(settings.database_url, future=True)
    Base.metadata.create_all(sync_engine)

    try:
        client = TestClient(app)

        workspace_response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Acme Social",
                "owner": {
                    "full_name": "Jordan Rivera",
                    "email": "jordan@acme.co",
                },
            },
        )
        assert workspace_response.status_code == 201
        workspace_id = workspace_response.json()["id"]

        brand_profile_response = client.put(
            f"/api/v1/workspaces/{workspace_id}/brand-profile",
            json={
                "brand_name": "Acme Social",
                "industry": "Consumer SaaS",
                "description": "Helps community teams operate with clarity.",
                "website_url": "https://acme.example.com",
                "voice_summary": "Clear, practical, and founder-direct.",
                "mission": "Make community work feel repeatable and visible.",
            },
        )
        assert brand_profile_response.status_code == 200

        segment_response = client.post(
            f"/api/v1/workspaces/{workspace_id}/audience-segments",
            json={
                "name": "Community operators",
                "description": "Own social and community reporting.",
                "age_range": "28-40",
                "interests": ["community", "growth", "reporting"],
                "primary_platform": "LinkedIn",
                "messaging_angle": "Practical operating leverage.",
            },
        )
        assert segment_response.status_code == 201

        strategy_run_response = client.post(
            f"/api/v1/workspaces/{workspace_id}/strategy-runs",
            json={"goal": "Create a believable first strategy"},
        )
        assert strategy_run_response.status_code == 201
        assert strategy_run_response.json()["workflow_type"] == "strategy"

        latest_strategy_response = client.get(f"/api/v1/workspaces/{workspace_id}/strategies/latest")
        assert latest_strategy_response.status_code == 200
        latest_strategy = latest_strategy_response.json()
        assert latest_strategy["platform_plans"]
        assert latest_strategy["content_pillars"]
        assert latest_strategy["is_active"] is True

        content_plan_run_response = client.post(
            f"/api/v1/workspaces/{workspace_id}/content-plan-runs",
            json={
                "brand_strategy_id": latest_strategy["id"],
                "planning_horizon_label": "Next 2 weeks",
            },
        )
        assert content_plan_run_response.status_code == 201

        latest_content_plan_response = client.get(
            f"/api/v1/workspaces/{workspace_id}/content-plans/latest"
        )
        assert latest_content_plan_response.status_code == 200
        latest_content_plan = latest_content_plan_response.json()
        assert len(latest_content_plan["planned_posts"]) >= 1
        assert latest_content_plan["is_active"] is True

        first_post = latest_content_plan["planned_posts"][0]
        update_post_response = client.put(
            f"/api/v1/planned-posts/{first_post['id']}",
            json={
                "scheduled_for": first_post["scheduled_for"],
                "platform": first_post["platform"],
                "format": first_post["format"],
                "title": "Updated founder-ready post",
                "hook": first_post["hook"],
                "angle": first_post["angle"],
                "call_to_action": first_post["call_to_action"],
                "status": "planned",
                "notes": "Tighten the opener before drafting.",
            },
        )
        assert update_post_response.status_code == 200
        assert update_post_response.json()["title"] == "Updated founder-ready post"

        draft_run_response = client.post(
            f"/api/v1/workspaces/{workspace_id}/draft-runs",
            json={"content_plan_id": latest_content_plan["id"]},
        )
        assert draft_run_response.status_code == 201
        assert draft_run_response.json()["workflow_type"] == "draft"

        review_queue_response = client.get(f"/api/v1/workspaces/{workspace_id}/drafts/review-queue")
        assert review_queue_response.status_code == 200
        review_queue = review_queue_response.json()
        assert len(review_queue) >= 1

        first_draft = review_queue[0]
        update_draft_response = client.put(
            f"/api/v1/drafts/{first_draft['id']}",
            json={
                "title": first_draft["title"],
                "caption": first_draft["caption"],
                "creative_brief": first_draft["creative_brief"],
                "call_to_action": first_draft["call_to_action"],
                "hashtags": first_draft["hashtags"],
                "review_status": "approved",
                "reviewer_notes": "Looks ready for demo.",
            },
        )
        assert update_draft_response.status_code == 200
        assert update_draft_response.json()["review_status"] == "approved"

        publish_ready_response = client.post(
            f"/api/v1/drafts/{first_draft['id']}/publish-ready",
            json={"scheduled_publish_at": "2026-06-01T10:00:00Z"},
        )
        assert publish_ready_response.status_code == 200
        assert publish_ready_response.json()["review_status"] == "publish_ready"

        publish_queue_response = client.get(f"/api/v1/workspaces/{workspace_id}/drafts/publishing-queue")
        assert publish_queue_response.status_code == 200
        publish_queue = publish_queue_response.json()
        assert len(publish_queue) >= 1

        publish_response = client.post(f"/api/v1/drafts/{first_draft['id']}/publish", json={})
        assert publish_response.status_code == 200
        assert publish_response.json()["review_status"] == "published"
        assert publish_response.json()["mock_publishing_receipt"] is not None

        activity_response = client.get(f"/api/v1/workspaces/{workspace_id}/activity")
        assert activity_response.status_code == 200
        activity_events = activity_response.json()
        assert len(activity_events) >= 6

        activity_summary_response = client.get(f"/api/v1/workspaces/{workspace_id}/activity/summary")
        assert activity_summary_response.status_code == 200
        assert activity_summary_response.json()["total_events"] >= 6

        updated_review_queue_response = client.get(
            f"/api/v1/workspaces/{workspace_id}/drafts/review-queue"
        )
        assert updated_review_queue_response.status_code == 200
        assert len(updated_review_queue_response.json()) == len(review_queue) - 1
    finally:
        sync_engine.dispose()
        asyncio.run(close_engine())
        if database_path.exists():
            database_path.unlink()
