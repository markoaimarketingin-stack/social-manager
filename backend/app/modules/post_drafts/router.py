from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.modules.post_drafts.schemas import (
    DraftPublishReadyRequest,
    DraftPublishRequest,
    PostDraftResponse,
    PostDraftUpdate,
)
from app.modules.post_drafts.service import PostDraftService

router = APIRouter(tags=["post_drafts"])


@router.get("/workspaces/{workspace_id}/drafts", response_model=list[PostDraftResponse])
async def list_post_drafts(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> list[PostDraftResponse]:
    service = PostDraftService(session)
    drafts = await service.list_drafts(workspace_id)
    return [PostDraftResponse.model_validate(draft) for draft in drafts]


@router.get("/workspaces/{workspace_id}/drafts/review-queue", response_model=list[PostDraftResponse])
async def list_review_queue(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> list[PostDraftResponse]:
    service = PostDraftService(session)
    drafts = await service.list_review_queue(workspace_id)
    return [PostDraftResponse.model_validate(draft) for draft in drafts]


@router.get("/workspaces/{workspace_id}/drafts/publishing-queue", response_model=list[PostDraftResponse])
async def list_publishing_queue(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> list[PostDraftResponse]:
    service = PostDraftService(session)
    drafts = await service.list_publish_ready_queue(workspace_id)
    return [PostDraftResponse.model_validate(draft) for draft in drafts]


@router.get("/drafts/{draft_id}", response_model=PostDraftResponse)
async def get_post_draft(
    draft_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> PostDraftResponse:
    service = PostDraftService(session)
    draft = await service.get_draft(draft_id)
    return PostDraftResponse.model_validate(draft)


@router.put("/drafts/{draft_id}", response_model=PostDraftResponse)
async def update_post_draft(
    draft_id: str,
    payload: PostDraftUpdate,
    session: AsyncSession = Depends(db_session_dependency),
) -> PostDraftResponse:
    service = PostDraftService(session)
    draft = await service.update_draft(draft_id, payload)
    return PostDraftResponse.model_validate(draft)


@router.post("/drafts/{draft_id}/publish-ready", response_model=PostDraftResponse)
async def mark_post_draft_publish_ready(
    draft_id: str,
    payload: DraftPublishReadyRequest,
    session: AsyncSession = Depends(db_session_dependency),
) -> PostDraftResponse:
    service = PostDraftService(session)
    draft = await service.mark_publish_ready(draft_id, payload)
    return PostDraftResponse.model_validate(draft)


@router.post("/drafts/{draft_id}/publish", response_model=PostDraftResponse)
async def publish_post_draft(
    draft_id: str,
    payload: DraftPublishRequest,
    session: AsyncSession = Depends(db_session_dependency),
) -> PostDraftResponse:
    service = PostDraftService(session)
    draft = await service.publish_draft(draft_id, payload)
    return PostDraftResponse.model_validate(draft)
