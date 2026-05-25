from __future__ import annotations

from datetime import date, timedelta

from app.modules.workflow_runs.schemas import ContentPlanWorkflowInput, ContentPlanWorkflowOutput, PlannedPostArtifact
from app.workflows.base import Workflow


class GenerateContentPlanWorkflow(Workflow[ContentPlanWorkflowInput, ContentPlanWorkflowOutput]):
    async def run(self, workflow_input: ContentPlanWorkflowInput) -> ContentPlanWorkflowOutput:
        formats = ["Founder POV", "Carousel", "Short video", "Community prompt"]
        start_date = date.today() + timedelta(days=1)
        planned_posts: list[PlannedPostArtifact] = []

        for index in range(6):
            platform = workflow_input.platform_names[index % len(workflow_input.platform_names)]
            pillar = workflow_input.content_pillars[index % len(workflow_input.content_pillars)]
            post_date = start_date + timedelta(days=index * 2)
            content_format = formats[index % len(formats)]
            planned_posts.append(
                PlannedPostArtifact(
                    sequence_number=index + 1,
                    scheduled_for=post_date,
                    platform=platform,
                    format=content_format,
                    title=f"{platform} {pillar} activation",
                    hook=f"Show how {pillar.lower()} turns into visible momentum for the brand.",
                    angle=(
                        f"Use {workflow_input.strategy_title.lower()} to make {pillar.lower()} feel "
                        f"operational and founder-ready on {platform}."
                    ),
                    call_to_action="Invite the audience to reply, save, or request the next breakdown.",
                    notes=f"Keep the tone grounded in {pillar.lower()} and execution clarity.",
                    content_pillar_name=pillar,
                )
            )

        return ContentPlanWorkflowOutput(
            title=f"{workflow_input.strategy_title} plan",
            planning_horizon_label=workflow_input.planning_horizon_label,
            summary=(
                f"A paced {workflow_input.planning_horizon_label.lower()} plan designed to spread "
                f"{workflow_input.strategy_title.lower()} across the most useful channels."
            ),
            status=ContentPlanWorkflowOutput.model_fields["status"].default,
            planned_posts=planned_posts,
        )
