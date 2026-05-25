"""strategy planning drafts

Revision ID: 0002_strategy_planning_drafts
Revises: 0001_phase0_foundation
Create Date: 2026-05-25 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_strategy_planning_drafts"
down_revision = "0001_phase0_foundation"
branch_labels = None
depends_on = None


workflow_type = sa.Enum("STRATEGY", "CONTENT_PLAN", "DRAFT", name="workflowtype")
workflow_status = sa.Enum("PENDING", "RUNNING", "COMPLETED", "FAILED", name="workflowstatus")
strategy_status = sa.Enum("DRAFT", "IN_REVIEW", "APPROVED", "NEEDS_REVISION", name="strategystatus")
content_plan_status = sa.Enum("DRAFT", "READY", name="contentplanstatus")
planned_post_status = sa.Enum("PLANNED", "DRAFTED", "READY_FOR_REVIEW", name="plannedpoststatus")
draft_review_status = sa.Enum(
    "DRAFT",
    "PENDING_REVIEW",
    "APPROVED",
    "CHANGES_REQUESTED",
    name="draftreviewstatus",
)


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE workflowtype ADD VALUE IF NOT EXISTS 'CONTENT_PLAN'")
        op.execute("ALTER TYPE workflowtype ADD VALUE IF NOT EXISTS 'DRAFT'")
        op.execute("ALTER TYPE workflowstatus ADD VALUE IF NOT EXISTS 'RUNNING'")
    else:
        workflow_type.create(bind, checkfirst=True)
        workflow_status.create(bind, checkfirst=True)

    strategy_status.create(bind, checkfirst=True)
    content_plan_status.create(bind, checkfirst=True)
    planned_post_status.create(bind, checkfirst=True)
    draft_review_status.create(bind, checkfirst=True)

    op.create_table(
        "brand_strategies",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("source_workflow_run_id", sa.String(length=36), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", strategy_status, nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("positioning_statement", sa.Text(), nullable=False),
        sa.Column("audience_focus", sa.Text(), nullable=False),
        sa.Column("channel_focus", sa.Text(), nullable=False),
        sa.Column("campaign_note", sa.Text(), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_workflow_run_id"], ["workflow_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_brand_strategies_workspace_id"), "brand_strategies", ["workspace_id"], unique=False)

    op.create_table(
        "platform_plans",
        sa.Column("brand_strategy_id", sa.String(length=36), nullable=False),
        sa.Column("platform_name", sa.String(length=80), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("cadence_summary", sa.Text(), nullable=False),
        sa.Column("content_mix", sa.Text(), nullable=False),
        sa.Column("success_signal", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["brand_strategy_id"], ["brand_strategies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_platform_plans_brand_strategy_id"), "platform_plans", ["brand_strategy_id"], unique=False)

    op.create_table(
        "content_pillars",
        sa.Column("brand_strategy_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("channel_angle", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["brand_strategy_id"], ["brand_strategies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_pillars_brand_strategy_id"), "content_pillars", ["brand_strategy_id"], unique=False)

    op.create_table(
        "content_plans",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("brand_strategy_id", sa.String(length=36), nullable=False),
        sa.Column("source_workflow_run_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("planning_horizon_label", sa.String(length=80), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("status", content_plan_status, nullable=False),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["brand_strategy_id"], ["brand_strategies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_workflow_run_id"], ["workflow_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_plans_brand_strategy_id"), "content_plans", ["brand_strategy_id"], unique=False)
    op.create_index(op.f("ix_content_plans_workspace_id"), "content_plans", ["workspace_id"], unique=False)

    op.create_table(
        "planned_posts",
        sa.Column("content_plan_id", sa.String(length=36), nullable=False),
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("brand_strategy_id", sa.String(length=36), nullable=False),
        sa.Column("content_pillar_id", sa.String(length=36), nullable=True),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("scheduled_for", sa.Date(), nullable=False),
        sa.Column("platform", sa.String(length=80), nullable=False),
        sa.Column("format", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("hook", sa.Text(), nullable=False),
        sa.Column("angle", sa.Text(), nullable=False),
        sa.Column("call_to_action", sa.Text(), nullable=False),
        sa.Column("status", planned_post_status, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["brand_strategy_id"], ["brand_strategies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["content_pillar_id"], ["content_pillars.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["content_plan_id"], ["content_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_planned_posts_brand_strategy_id"), "planned_posts", ["brand_strategy_id"], unique=False)
    op.create_index(op.f("ix_planned_posts_content_plan_id"), "planned_posts", ["content_plan_id"], unique=False)
    op.create_index(op.f("ix_planned_posts_workspace_id"), "planned_posts", ["workspace_id"], unique=False)

    op.create_table(
        "post_drafts",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("planned_post_id", sa.String(length=36), nullable=False),
        sa.Column("source_workflow_run_id", sa.String(length=36), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column("creative_brief", sa.Text(), nullable=False),
        sa.Column("call_to_action", sa.Text(), nullable=False),
        sa.Column("hashtags", sa.JSON(), nullable=False),
        sa.Column("review_status", draft_review_status, nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["planned_post_id"], ["planned_posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_workflow_run_id"], ["workflow_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_drafts_planned_post_id"), "post_drafts", ["planned_post_id"], unique=False)
    op.create_index(op.f("ix_post_drafts_workspace_id"), "post_drafts", ["workspace_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_index(op.f("ix_post_drafts_workspace_id"), table_name="post_drafts")
    op.drop_index(op.f("ix_post_drafts_planned_post_id"), table_name="post_drafts")
    op.drop_table("post_drafts")
    op.drop_index(op.f("ix_planned_posts_workspace_id"), table_name="planned_posts")
    op.drop_index(op.f("ix_planned_posts_content_plan_id"), table_name="planned_posts")
    op.drop_index(op.f("ix_planned_posts_brand_strategy_id"), table_name="planned_posts")
    op.drop_table("planned_posts")
    op.drop_index(op.f("ix_content_plans_workspace_id"), table_name="content_plans")
    op.drop_index(op.f("ix_content_plans_brand_strategy_id"), table_name="content_plans")
    op.drop_table("content_plans")
    op.drop_index(op.f("ix_content_pillars_brand_strategy_id"), table_name="content_pillars")
    op.drop_table("content_pillars")
    op.drop_index(op.f("ix_platform_plans_brand_strategy_id"), table_name="platform_plans")
    op.drop_table("platform_plans")
    op.drop_index(op.f("ix_brand_strategies_workspace_id"), table_name="brand_strategies")
    op.drop_table("brand_strategies")

    draft_review_status.drop(bind, checkfirst=True)
    planned_post_status.drop(bind, checkfirst=True)
    content_plan_status.drop(bind, checkfirst=True)
    strategy_status.drop(bind, checkfirst=True)
