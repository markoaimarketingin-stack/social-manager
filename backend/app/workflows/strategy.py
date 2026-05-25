from __future__ import annotations

from app.modules.workflow_runs.schemas import (
    StrategyContentPillarArtifact,
    StrategyPlatformPlanArtifact,
    StrategyWorkflowInput,
    StrategyWorkflowOutput,
)
from app.modules.brand_strategies.models import StrategyStatus
from app.workflows.base import Workflow


class GenerateStrategyWorkflow(Workflow[StrategyWorkflowInput, StrategyWorkflowOutput]):
    async def run(self, workflow_input: StrategyWorkflowInput) -> StrategyWorkflowOutput:
        audience_hint = (
            ", ".join(workflow_input.audience_segments[:2])
            if workflow_input.audience_segments
            else "the first high-intent audience segments"
        )
        brand_name = workflow_input.brand_profile_name
        industry = workflow_input.industry
        return StrategyWorkflowOutput(
            summary=(
                f"{brand_name} should show up as the operator-friendly voice in {industry.lower()}, "
                f"turning brand clarity into repeatable community momentum."
            ),
            title=f"{brand_name} growth strategy",
            positioning_statement=(
                f"{brand_name} helps {audience_hint} feel like they are getting a sharp, decisive "
                "guide instead of another noisy social account."
            ),
            audience_focus=(
                f"Primary attention goes to {audience_hint}, with messaging grounded in "
                f"{workflow_input.goal.lower()} and a voice that feels clear rather than performative."
            ),
            channel_focus=(
                "Lead with high-context formats for trust, then turn the strongest ideas into "
                "repeatable short-form and carousel moments."
            ),
            campaign_note=(
                f"Use the next planning cycle to prove {brand_name}'s operating point of view with "
                "consistent formats rather than one-off campaign theatrics."
            ),
            status=StrategyStatus.IN_REVIEW,
            recommended_next_steps=[
                "Review the strategy narrative and lock the strongest positioning language.",
                "Generate the first content plan and adjust cadence before drafting.",
                f"Keep the initial goal visible: {workflow_input.goal}",
            ],
            platform_plans=[
                StrategyPlatformPlanArtifact(
                    platform_name="Instagram",
                    objective="Make the brand feel culturally current and visually decisive.",
                    cadence_summary="3 weekly posts: one proof carousel, one founder angle, one social proof reel.",
                    content_mix="Behind-the-scenes process, POV storytelling, and proof-led summaries.",
                    success_signal="Saves and profile visits rise on narrative-led posts.",
                    sort_order=0,
                ),
                StrategyPlatformPlanArtifact(
                    platform_name="LinkedIn",
                    objective="Turn the brand into an operator-grade voice for partnerships and trust.",
                    cadence_summary="2 weekly posts: one operator memo and one outcome breakdown.",
                    content_mix="Strategic observations, customer lessons, and lightweight case stories.",
                    success_signal="Decision-maker comments and inbound conversations increase.",
                    sort_order=1,
                ),
                StrategyPlatformPlanArtifact(
                    platform_name="X",
                    objective="Test sharper messaging hooks and audience resonance in public.",
                    cadence_summary="3 short weekly threads or punchy standalone posts.",
                    content_mix="Hot takes, market signals, and fast iteration of the strongest hooks.",
                    success_signal="High-engagement hooks become inputs for the planning queue.",
                    sort_order=2,
                ),
            ],
            content_pillars=[
                StrategyContentPillarArtifact(
                    name="Operator clarity",
                    description="Explain decisions, tradeoffs, and frameworks in a way that builds trust.",
                    channel_angle="Founder POV and process-driven breakdowns.",
                    sort_order=0,
                ),
                StrategyContentPillarArtifact(
                    name="Audience proof",
                    description="Show that the product understands the audience's day-to-day reality.",
                    channel_angle="Narrative hooks backed by practical examples and reactions.",
                    sort_order=1,
                ),
                StrategyContentPillarArtifact(
                    name="Execution confidence",
                    description="Make the brand feel reliable by showing a visible operating cadence.",
                    channel_angle="Weekly planning snapshots, learnings, and draft-ready ideas.",
                    sort_order=2,
                ),
            ],
        )
