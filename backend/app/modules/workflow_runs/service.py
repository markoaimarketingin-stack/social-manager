from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.activity_events.models import ActivityEntityType, ActivityEventType
from app.modules.activity_events.service import WorkspaceActivityEventService
from app.modules.audience_segments.repository import AudienceSegmentRepository
from app.modules.brand_profiles.repository import BrandProfileRepository
from app.modules.brand_strategies.models import BrandStrategy, ContentPillar, PlatformPlan
from app.modules.brand_strategies.repository import BrandStrategyRepository
from app.modules.content_plans.models import ContentPlan, PlannedPost, PlannedPostStatus
from app.modules.content_plans.repository import ContentPlanRepository
from app.modules.content_plans.schemas import ContentPlanGenerateRequest
from app.modules.post_drafts.models import DraftReviewStatus, PostDraft
from app.modules.post_drafts.repository import PostDraftRepository
from app.modules.post_drafts.schemas import DraftGenerateRequest
from app.modules.workflow_runs.models import WorkflowRun, WorkflowStatus, WorkflowType
from app.modules.workflow_runs.repository import WorkflowRunRepository
from app.modules.workflow_runs.schemas import (
    ContentPlanWorkflowInput,
    DraftWorkflowInput,
    PlannedPostArtifact,
    StrategyWorkflowInput,
    StrategyWorkflowRequest,
)
from app.modules.workspaces.repository import WorkspaceRepository
from app.workflows.drafts import GenerateDraftWorkflow
from app.workflows.planning import GenerateContentPlanWorkflow
from app.workflows.strategy import GenerateStrategyWorkflow


class WorkflowRunService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.workflow_run_repository = WorkflowRunRepository(session)
        self.workspace_repository = WorkspaceRepository(session)
        self.brand_profile_repository = BrandProfileRepository(session)
        self.audience_segment_repository = AudienceSegmentRepository(session)
        self.brand_strategy_repository = BrandStrategyRepository(session)
        self.content_plan_repository = ContentPlanRepository(session)
        self.post_draft_repository = PostDraftRepository(session)
        self.activity_service = WorkspaceActivityEventService(session)
        self.strategy_workflow = GenerateStrategyWorkflow()
        self.content_plan_workflow = GenerateContentPlanWorkflow()
        self.draft_workflow = GenerateDraftWorkflow()

    async def list_runs(self, workspace_id: str) -> list[WorkflowRun]:
        await self._ensure_workspace_exists(workspace_id)
        return await self.workflow_run_repository.list_by_workspace_id(workspace_id)

    async def get_run(self, workflow_run_id: str) -> WorkflowRun:
        workflow_run = await self.workflow_run_repository.get_by_id(workflow_run_id)
        if workflow_run is None:
            raise NotFoundError("Workflow run not found", code="workflow_run_not_found")
        return workflow_run

    async def start_strategy_run(
        self,
        workspace_id: str,
        payload: StrategyWorkflowRequest,
    ) -> WorkflowRun:
        await self._ensure_workspace_exists(workspace_id)

        brand_profile = await self.brand_profile_repository.get_by_workspace_id(workspace_id)
        if brand_profile is None:
            raise NotFoundError(
                "Brand profile required before strategy generation",
                code="brand_profile_required",
            )
        audience_segments = await self.audience_segment_repository.list_by_workspace_id(workspace_id)

        workflow_input = StrategyWorkflowInput(
            workspace_id=workspace_id,
            brand_profile_name=brand_profile.brand_name,
            industry=brand_profile.industry,
            voice_summary=brand_profile.voice_summary,
            mission=brand_profile.mission,
            audience_segments=[segment.name for segment in audience_segments],
            goal=payload.goal,
        )
        workflow_run = WorkflowRun(
            workspace_id=workspace_id,
            workflow_type=WorkflowType.STRATEGY,
            status=WorkflowStatus.RUNNING,
            input_payload=workflow_input.model_dump(),
            started_at=datetime.now(timezone.utc),
            initiated_by_member_id=payload.initiated_by_member_id,
        )
        await self.workflow_run_repository.save(workflow_run)
        try:
            output = await self.strategy_workflow.run(workflow_input)
            version_number = await self.brand_strategy_repository.get_next_version_number(workspace_id)
            previous_strategy = await self.brand_strategy_repository.get_active_by_workspace_id(workspace_id)
            if previous_strategy is not None:
                previous_strategy.is_active = False
                previous_strategy.superseded_at = datetime.now(timezone.utc)

            strategy = BrandStrategy(
                workspace_id=workspace_id,
                source_workflow_run_id=workflow_run.id,
                parent_strategy_id=previous_strategy.id if previous_strategy is not None else None,
                version_number=version_number,
                is_active=True,
                status=output.status,
                title=output.title,
                summary=output.summary,
                positioning_statement=output.positioning_statement,
                audience_focus=output.audience_focus,
                channel_focus=output.channel_focus,
                campaign_note=output.campaign_note,
                platform_plans=[
                    PlatformPlan(
                        platform_name=platform_plan.platform_name,
                        objective=platform_plan.objective,
                        cadence_summary=platform_plan.cadence_summary,
                        content_mix=platform_plan.content_mix,
                        success_signal=platform_plan.success_signal,
                        sort_order=platform_plan.sort_order,
                    )
                    for platform_plan in output.platform_plans
                ],
                content_pillars=[
                    ContentPillar(
                        name=pillar.name,
                        description=pillar.description,
                        channel_angle=pillar.channel_angle,
                        sort_order=pillar.sort_order,
                    )
                    for pillar in output.content_pillars
                ],
            )
            await self.brand_strategy_repository.save(strategy)

            workflow_run.status = WorkflowStatus.COMPLETED
            workflow_run.output_payload = {
                **output.model_dump(),
                "brand_strategy_id": strategy.id,
                "version_number": strategy.version_number,
                "parent_strategy_id": strategy.parent_strategy_id,
            }
            workflow_run.completed_at = datetime.now(timezone.utc)

            await self.activity_service.record_event(
                workspace_id=workspace_id,
                entity_type=ActivityEntityType.STRATEGY,
                entity_id=strategy.id,
                event_type=ActivityEventType.STRATEGY_GENERATED,
                summary=f"Generated strategy v{strategy.version_number}: {strategy.title}.",
                actor_member_id=payload.initiated_by_member_id,
                actor_label="Workflow",
                metadata_payload={
                    "workflow_run_id": workflow_run.id,
                    "parent_strategy_id": strategy.parent_strategy_id,
                },
            )
            await self.activity_service.record_event(
                workspace_id=workspace_id,
                entity_type=ActivityEntityType.WORKFLOW_RUN,
                entity_id=workflow_run.id,
                event_type=ActivityEventType.WORKFLOW_COMPLETED,
                summary="Completed strategy workflow.",
                actor_member_id=payload.initiated_by_member_id,
                actor_label="Workflow",
                metadata_payload={"workflow_type": workflow_run.workflow_type.value},
            )
            await self.session.commit()
        except Exception as exc:
            workflow_run.status = WorkflowStatus.FAILED
            workflow_run.error_message = str(exc)
            workflow_run.completed_at = datetime.now(timezone.utc)
            await self.activity_service.record_event(
                workspace_id=workspace_id,
                entity_type=ActivityEntityType.WORKFLOW_RUN,
                entity_id=workflow_run.id,
                event_type=ActivityEventType.WORKFLOW_FAILED,
                summary="Strategy workflow failed.",
                actor_member_id=payload.initiated_by_member_id,
                actor_label="Workflow",
                metadata_payload={"error_message": str(exc)},
            )
            await self.session.commit()
            raise

        await self.session.refresh(workflow_run)
        return workflow_run

    async def start_content_plan_run(
        self,
        workspace_id: str,
        payload: ContentPlanGenerateRequest,
    ) -> WorkflowRun:
        await self._ensure_workspace_exists(workspace_id)
        strategy = await self._resolve_strategy(workspace_id, payload.brand_strategy_id)

        workflow_input = ContentPlanWorkflowInput(
            workspace_id=workspace_id,
            brand_strategy_id=strategy.id,
            strategy_title=strategy.title,
            planning_horizon_label=payload.planning_horizon_label,
            platform_names=[plan.platform_name for plan in strategy.platform_plans] or ["Instagram"],
            content_pillars=[pillar.name for pillar in strategy.content_pillars] or ["Operator clarity"],
        )
        workflow_run = WorkflowRun(
            workspace_id=workspace_id,
            workflow_type=WorkflowType.CONTENT_PLAN,
            status=WorkflowStatus.RUNNING,
            input_payload=workflow_input.model_dump(),
            started_at=datetime.now(timezone.utc),
            initiated_by_member_id=payload.initiated_by_member_id,
        )
        await self.workflow_run_repository.save(workflow_run)
        try:
            output = await self.content_plan_workflow.run(workflow_input)
            pillar_map = {pillar.name: pillar.id for pillar in strategy.content_pillars}
            version_number = await self.content_plan_repository.get_next_version_number(workspace_id)
            previous_plan = await self.content_plan_repository.get_active_by_workspace_id(workspace_id)
            if previous_plan is not None:
                previous_plan.is_active = False
                previous_plan.superseded_at = datetime.now(timezone.utc)

            content_plan = ContentPlan(
                workspace_id=workspace_id,
                brand_strategy_id=strategy.id,
                source_workflow_run_id=workflow_run.id,
                parent_plan_id=previous_plan.id if previous_plan is not None else None,
                version_number=version_number,
                is_active=True,
                title=output.title,
                planning_horizon_label=output.planning_horizon_label,
                summary=output.summary,
                status=output.status,
                planned_posts=[
                    PlannedPost(
                        workspace_id=workspace_id,
                        brand_strategy_id=strategy.id,
                        content_pillar_id=pillar_map.get(post.content_pillar_name or ""),
                        sequence_number=post.sequence_number,
                        scheduled_for=post.scheduled_for,
                        platform=post.platform,
                        format=post.format,
                        title=post.title,
                        hook=post.hook,
                        angle=post.angle,
                        call_to_action=post.call_to_action,
                        status=post.status,
                        notes=post.notes,
                    )
                    for post in output.planned_posts
                ],
            )
            await self.content_plan_repository.save(content_plan)

            workflow_run.status = WorkflowStatus.COMPLETED
            workflow_run.output_payload = {
                **output.model_dump(mode="json"),
                "content_plan_id": content_plan.id,
                "planned_post_count": len(output.planned_posts),
                "brand_strategy_id": strategy.id,
                "parent_plan_id": content_plan.parent_plan_id,
            }
            workflow_run.completed_at = datetime.now(timezone.utc)

            await self.activity_service.record_event(
                workspace_id=workspace_id,
                entity_type=ActivityEntityType.CONTENT_PLAN,
                entity_id=content_plan.id,
                event_type=ActivityEventType.CONTENT_PLAN_GENERATED,
                summary=f"Generated content plan v{content_plan.version_number}: {content_plan.title}.",
                actor_member_id=payload.initiated_by_member_id,
                actor_label="Workflow",
                metadata_payload={
                    "workflow_run_id": workflow_run.id,
                    "brand_strategy_id": strategy.id,
                    "parent_plan_id": content_plan.parent_plan_id,
                },
            )
            await self.activity_service.record_event(
                workspace_id=workspace_id,
                entity_type=ActivityEntityType.WORKFLOW_RUN,
                entity_id=workflow_run.id,
                event_type=ActivityEventType.WORKFLOW_COMPLETED,
                summary="Completed content plan workflow.",
                actor_member_id=payload.initiated_by_member_id,
                actor_label="Workflow",
                metadata_payload={"workflow_type": workflow_run.workflow_type.value},
            )
            await self.session.commit()
        except Exception as exc:
            workflow_run.status = WorkflowStatus.FAILED
            workflow_run.error_message = str(exc)
            workflow_run.completed_at = datetime.now(timezone.utc)
            await self.activity_service.record_event(
                workspace_id=workspace_id,
                entity_type=ActivityEntityType.WORKFLOW_RUN,
                entity_id=workflow_run.id,
                event_type=ActivityEventType.WORKFLOW_FAILED,
                summary="Content plan workflow failed.",
                actor_member_id=payload.initiated_by_member_id,
                actor_label="Workflow",
                metadata_payload={"error_message": str(exc)},
            )
            await self.session.commit()
            raise

        await self.session.refresh(workflow_run)
        return workflow_run

    async def start_draft_run(
        self,
        workspace_id: str,
        payload: DraftGenerateRequest,
    ) -> WorkflowRun:
        await self._ensure_workspace_exists(workspace_id)
        content_plan = await self._resolve_content_plan(workspace_id, payload.content_plan_id)

        workflow_input = DraftWorkflowInput(
            workspace_id=workspace_id,
            content_plan_id=content_plan.id,
            plan_title=content_plan.title,
            planned_posts=[
                PlannedPostArtifact(
                    sequence_number=post.sequence_number,
                    scheduled_for=post.scheduled_for,
                    platform=post.platform,
                    format=post.format,
                    title=post.title,
                    hook=post.hook,
                    angle=post.angle,
                    call_to_action=post.call_to_action,
                    status=post.status,
                    notes=post.notes,
                    content_pillar_name=None,
                )
                for post in content_plan.planned_posts
            ],
        )
        workflow_run = WorkflowRun(
            workspace_id=workspace_id,
            workflow_type=WorkflowType.DRAFT,
            status=WorkflowStatus.RUNNING,
            input_payload=workflow_input.model_dump(mode="json"),
            started_at=datetime.now(timezone.utc),
            initiated_by_member_id=payload.initiated_by_member_id,
        )
        await self.workflow_run_repository.save(workflow_run)
        try:
            output = await self.draft_workflow.run(workflow_input)
            posts_by_sequence = {post.sequence_number: post for post in content_plan.planned_posts}

            generated_count = 0
            generated_draft_ids: list[str] = []
            for draft_artifact in output.drafts:
                planned_post = posts_by_sequence.get(draft_artifact.planned_post_sequence_number)
                if planned_post is None:
                    continue

                previous_draft = await self.post_draft_repository.get_current_by_planned_post_id(planned_post.id)
                if previous_draft is not None:
                    previous_draft.is_current_version = False

                draft = PostDraft(
                    workspace_id=workspace_id,
                    planned_post_id=planned_post.id,
                    source_workflow_run_id=workflow_run.id,
                    parent_draft_id=previous_draft.id if previous_draft is not None else None,
                    version_number=await self.post_draft_repository.get_next_version_number(planned_post.id),
                    is_current_version=True,
                    title=draft_artifact.title,
                    caption=draft_artifact.caption,
                    creative_brief=draft_artifact.creative_brief,
                    call_to_action=draft_artifact.call_to_action,
                    hashtags=draft_artifact.hashtags,
                    review_status=draft_artifact.review_status,
                )
                await self.post_draft_repository.save(draft)
                planned_post.status = PlannedPostStatus.DRAFTED
                generated_count += 1
                generated_draft_ids.append(draft.id)

                await self.activity_service.record_event(
                    workspace_id=workspace_id,
                    entity_type=ActivityEntityType.POST_DRAFT,
                    entity_id=draft.id,
                    event_type=ActivityEventType.DRAFT_GENERATED,
                    summary=f"Generated draft v{draft.version_number} for '{draft.title}'.",
                    actor_member_id=payload.initiated_by_member_id,
                    actor_label="Workflow",
                    metadata_payload={
                        "workflow_run_id": workflow_run.id,
                        "planned_post_id": planned_post.id,
                        "parent_draft_id": draft.parent_draft_id,
                    },
                )

            workflow_run.status = WorkflowStatus.COMPLETED
            workflow_run.output_payload = {
                **output.model_dump(),
                "content_plan_id": content_plan.id,
                "generated_count": generated_count,
                "generated_draft_ids": generated_draft_ids,
                "brand_strategy_id": content_plan.brand_strategy_id,
            }
            workflow_run.completed_at = datetime.now(timezone.utc)

            await self.activity_service.record_event(
                workspace_id=workspace_id,
                entity_type=ActivityEntityType.WORKFLOW_RUN,
                entity_id=workflow_run.id,
                event_type=ActivityEventType.WORKFLOW_COMPLETED,
                summary="Completed draft generation workflow.",
                actor_member_id=payload.initiated_by_member_id,
                actor_label="Workflow",
                metadata_payload={"workflow_type": workflow_run.workflow_type.value},
            )
            await self.session.commit()
        except Exception as exc:
            workflow_run.status = WorkflowStatus.FAILED
            workflow_run.error_message = str(exc)
            workflow_run.completed_at = datetime.now(timezone.utc)
            await self.activity_service.record_event(
                workspace_id=workspace_id,
                entity_type=ActivityEntityType.WORKFLOW_RUN,
                entity_id=workflow_run.id,
                event_type=ActivityEventType.WORKFLOW_FAILED,
                summary="Draft workflow failed.",
                actor_member_id=payload.initiated_by_member_id,
                actor_label="Workflow",
                metadata_payload={"error_message": str(exc)},
            )
            await self.session.commit()
            raise

        await self.session.refresh(workflow_run)
        return workflow_run

    async def _resolve_strategy(self, workspace_id: str, strategy_id: str | None) -> BrandStrategy:
        if strategy_id is not None:
            strategy = await self.brand_strategy_repository.get_by_id(strategy_id)
        else:
            strategy = await self.brand_strategy_repository.get_active_by_workspace_id(workspace_id)
            if strategy is None:
                strategy = await self.brand_strategy_repository.get_latest_by_workspace_id(workspace_id)
        if strategy is None or strategy.workspace_id != workspace_id:
            raise NotFoundError("Strategy not found", code="strategy_not_found")
        return strategy

    async def _resolve_content_plan(self, workspace_id: str, content_plan_id: str | None) -> ContentPlan:
        if content_plan_id is not None:
            content_plan = await self.content_plan_repository.get_by_id(content_plan_id)
        else:
            content_plan = await self.content_plan_repository.get_active_by_workspace_id(workspace_id)
            if content_plan is None:
                content_plan = await self.content_plan_repository.get_latest_by_workspace_id(workspace_id)
        if content_plan is None or content_plan.workspace_id != workspace_id:
            raise NotFoundError("Content plan not found", code="content_plan_not_found")
        return content_plan

    async def _ensure_workspace_exists(self, workspace_id: str) -> None:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundError("Workspace not found", code="workspace_not_found")
