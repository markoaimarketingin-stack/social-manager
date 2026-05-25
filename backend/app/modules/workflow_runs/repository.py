from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.workflow_runs.models import WorkflowRun


class WorkflowRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, workflow_run: WorkflowRun) -> WorkflowRun:
        self.session.add(workflow_run)
        await self.session.flush()
        await self.session.refresh(workflow_run)
        return workflow_run

    async def list_by_workspace_id(self, workspace_id: str) -> list[WorkflowRun]:
        result = await self.session.execute(
            select(WorkflowRun)
            .where(WorkflowRun.workspace_id == workspace_id)
            .order_by(WorkflowRun.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, workflow_run_id: str) -> WorkflowRun | None:
        result = await self.session.execute(select(WorkflowRun).where(WorkflowRun.id == workflow_run_id))
        return result.scalar_one_or_none()
