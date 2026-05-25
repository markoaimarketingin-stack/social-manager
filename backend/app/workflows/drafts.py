from __future__ import annotations

from app.modules.post_drafts.models import DraftReviewStatus
from app.modules.workflow_runs.schemas import DraftArtifact, DraftWorkflowInput, DraftWorkflowOutput
from app.workflows.base import Workflow


class GenerateDraftWorkflow(Workflow[DraftWorkflowInput, DraftWorkflowOutput]):
    async def run(self, workflow_input: DraftWorkflowInput) -> DraftWorkflowOutput:
        drafts: list[DraftArtifact] = []
        for planned_post in workflow_input.planned_posts:
            hashtags = [
                "#MarkoAI",
                f"#{planned_post.platform.replace(' ', '')}",
                f"#{planned_post.format.replace(' ', '')}",
            ]
            drafts.append(
                DraftArtifact(
                    planned_post_sequence_number=planned_post.sequence_number,
                    title=planned_post.title,
                    caption=(
                        f"{planned_post.hook}\n\n"
                        f"{planned_post.angle}\n\n"
                        f"{planned_post.call_to_action}"
                    ),
                    creative_brief=(
                        f"Visualize {planned_post.title.lower()} with a premium, dark-shell product "
                        f"feel and a clear founder-demo narrative."
                    ),
                    call_to_action=planned_post.call_to_action,
                    hashtags=hashtags,
                    review_status=DraftReviewStatus.IN_REVIEW,
                )
            )

        return DraftWorkflowOutput(
            summary=(
                f"Generated {len(drafts)} drafts from {workflow_input.plan_title.lower()} for review "
                "and editing."
            ),
            generated_count=len(drafts),
            drafts=drafts,
        )
