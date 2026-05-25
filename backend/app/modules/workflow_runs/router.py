from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.modules.content_plans.schemas import ContentPlanGenerateRequest
from app.modules.post_drafts.schemas import DraftGenerateRequest
from app.modules.workflow_runs.schemas import StrategyWorkflowRequest, WorkflowRunResponse
from app.modules.workflow_runs.service import WorkflowRunService

router = APIRouter(tags=["workflow_runs"])


@router.get("/workspaces/{workspace_id}/workflow-runs", response_model=list[WorkflowRunResponse])
async def list_workflow_runs(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> list[WorkflowRunResponse]:
    service = WorkflowRunService(session)
    workflow_runs = await service.list_runs(workspace_id)
    return [WorkflowRunResponse.model_validate(workflow_run) for workflow_run in workflow_runs]


@router.get("/workflow-runs/{workflow_run_id}", response_model=WorkflowRunResponse)
async def get_workflow_run(
    workflow_run_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> WorkflowRunResponse:
    service = WorkflowRunService(session)
    workflow_run = await service.get_run(workflow_run_id)
    return WorkflowRunResponse.model_validate(workflow_run)


@router.post("/workspaces/{workspace_id}/strategy-runs", response_model=WorkflowRunResponse, status_code=201)
async def start_strategy_run(
    workspace_id: str,
    payload: StrategyWorkflowRequest,
    session: AsyncSession = Depends(db_session_dependency),
) -> WorkflowRunResponse:
    service = WorkflowRunService(session)
    workflow_run = await service.start_strategy_run(workspace_id, payload)
    return WorkflowRunResponse.model_validate(workflow_run)


@router.post(
    "/workspaces/{workspace_id}/content-plan-runs",
    response_model=WorkflowRunResponse,
    status_code=201,
)
async def start_content_plan_run(
    workspace_id: str,
    payload: ContentPlanGenerateRequest,
    session: AsyncSession = Depends(db_session_dependency),
) -> WorkflowRunResponse:
    service = WorkflowRunService(session)
    workflow_run = await service.start_content_plan_run(workspace_id, payload)
    return WorkflowRunResponse.model_validate(workflow_run)


@router.post("/workspaces/{workspace_id}/draft-runs", response_model=WorkflowRunResponse, status_code=201)
async def start_draft_run(
    workspace_id: str,
    payload: DraftGenerateRequest,
    session: AsyncSession = Depends(db_session_dependency),
) -> WorkflowRunResponse:
    service = WorkflowRunService(session)
    workflow_run = await service.start_draft_run(workspace_id, payload)
    return WorkflowRunResponse.model_validate(workflow_run)
