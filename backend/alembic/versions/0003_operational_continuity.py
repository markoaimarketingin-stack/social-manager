"""operational continuity

Revision ID: 0003_operational_continuity
Revises: 0002_strategy_planning_drafts
Create Date: 2026-05-25 18:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_operational_continuity"
down_revision = "0002_strategy_planning_drafts"
branch_labels = None
depends_on = None


activity_entity_type = sa.Enum(
    "WORKSPACE",
    "STRATEGY",
    "CONTENT_PLAN",
    "PLANNED_POST",
    "POST_DRAFT",
    "WORKFLOW_RUN",
    name="activityentitytype",
)
activity_event_type = sa.Enum(
    "WORKSPACE_CREATED",
    "STRATEGY_GENERATED",
    "STRATEGY_REVIEWED",
    "CONTENT_PLAN_GENERATED",
    "PLANNED_POST_EDITED",
    "DRAFT_GENERATED",
    "DRAFT_UPDATED",
    "REVIEW_STATUS_CHANGED",
    "APPROVAL_GRANTED",
    "PUBLISH_READY",
    "PUBLISHED",
    "WORKFLOW_COMPLETED",
    "WORKFLOW_FAILED",
    name="activityeventtype",
)


def _add_enum_value_if_needed(enum_name: str, value: str) -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(f"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS '{value}'")


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name != "postgresql":
        activity_entity_type.create(bind, checkfirst=True)
        activity_event_type.create(bind, checkfirst=True)
    else:
        activity_entity_type.create(bind, checkfirst=True)
        activity_event_type.create(bind, checkfirst=True)

    for value in ("REJECTED",):
        _add_enum_value_if_needed("strategystatus", value)
    for value in ("IN_REVIEW", "APPROVED"):
        _add_enum_value_if_needed("contentplanstatus", value)
    for value in ("IN_REVIEW", "APPROVED", "PUBLISH_READY", "PUBLISHED", "REJECTED"):
        _add_enum_value_if_needed("plannedpoststatus", value)
    for value in ("IN_REVIEW", "PUBLISH_READY", "PUBLISHED", "REJECTED"):
        _add_enum_value_if_needed("draftreviewstatus", value)

    op.create_table(
        "workspace_activity_events",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("actor_member_id", sa.String(length=36), nullable=True),
        sa.Column("actor_label", sa.String(length=120), nullable=True),
        sa.Column("entity_type", activity_entity_type, nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", activity_event_type, nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("metadata_payload", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_workspace_activity_events_workspace_id"),
        "workspace_activity_events",
        ["workspace_id"],
        unique=False,
    )

    op.add_column("brand_strategies", sa.Column("parent_strategy_id", sa.String(length=36), nullable=True))
    op.add_column(
        "brand_strategies",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("brand_strategies", sa.Column("reviewed_by_member_id", sa.String(length=36), nullable=True))
    op.add_column("brand_strategies", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("brand_strategies", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("brand_strategies", sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True))
    if bind.dialect.name != "sqlite":
        op.create_foreign_key(
            "fk_brand_strategies_parent_strategy_id",
            "brand_strategies",
            "brand_strategies",
            ["parent_strategy_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.add_column("content_plans", sa.Column("parent_plan_id", sa.String(length=36), nullable=True))
    op.add_column(
        "content_plans",
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "content_plans",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("content_plans", sa.Column("reviewed_by_member_id", sa.String(length=36), nullable=True))
    op.add_column("content_plans", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("content_plans", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("content_plans", sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True))
    if bind.dialect.name != "sqlite":
        op.create_foreign_key(
            "fk_content_plans_parent_plan_id",
            "content_plans",
            "content_plans",
            ["parent_plan_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.add_column("planned_posts", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("planned_posts", sa.Column("publish_ready_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("planned_posts", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column("post_drafts", sa.Column("parent_draft_id", sa.String(length=36), nullable=True))
    op.add_column(
        "post_drafts",
        sa.Column("is_current_version", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("post_drafts", sa.Column("reviewer_member_id", sa.String(length=36), nullable=True))
    op.add_column("post_drafts", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("post_drafts", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("post_drafts", sa.Column("publish_ready_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("post_drafts", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("post_drafts", sa.Column("scheduled_publish_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("post_drafts", sa.Column("mock_publishing_receipt", sa.JSON(), nullable=True))
    if bind.dialect.name != "sqlite":
        op.create_foreign_key(
            "fk_post_drafts_parent_draft_id",
            "post_drafts",
            "post_drafts",
            ["parent_draft_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    bind = op.get_bind()

    bind = op.get_bind()

    if bind.dialect.name != "sqlite":
        op.drop_constraint("fk_post_drafts_parent_draft_id", "post_drafts", type_="foreignkey")
    op.drop_column("post_drafts", "mock_publishing_receipt")
    op.drop_column("post_drafts", "scheduled_publish_at")
    op.drop_column("post_drafts", "published_at")
    op.drop_column("post_drafts", "publish_ready_at")
    op.drop_column("post_drafts", "approved_at")
    op.drop_column("post_drafts", "reviewed_at")
    op.drop_column("post_drafts", "reviewer_member_id")
    op.drop_column("post_drafts", "is_current_version")
    op.drop_column("post_drafts", "parent_draft_id")

    op.drop_column("planned_posts", "published_at")
    op.drop_column("planned_posts", "publish_ready_at")
    op.drop_column("planned_posts", "approved_at")

    if bind.dialect.name != "sqlite":
        op.drop_constraint("fk_content_plans_parent_plan_id", "content_plans", type_="foreignkey")
    op.drop_column("content_plans", "superseded_at")
    op.drop_column("content_plans", "approved_at")
    op.drop_column("content_plans", "reviewed_at")
    op.drop_column("content_plans", "reviewed_by_member_id")
    op.drop_column("content_plans", "is_active")
    op.drop_column("content_plans", "version_number")
    op.drop_column("content_plans", "parent_plan_id")

    if bind.dialect.name != "sqlite":
        op.drop_constraint("fk_brand_strategies_parent_strategy_id", "brand_strategies", type_="foreignkey")
    op.drop_column("brand_strategies", "superseded_at")
    op.drop_column("brand_strategies", "approved_at")
    op.drop_column("brand_strategies", "reviewed_at")
    op.drop_column("brand_strategies", "reviewed_by_member_id")
    op.drop_column("brand_strategies", "is_active")
    op.drop_column("brand_strategies", "parent_strategy_id")

    op.drop_index(op.f("ix_workspace_activity_events_workspace_id"), table_name="workspace_activity_events")
    op.drop_table("workspace_activity_events")

    activity_event_type.drop(bind, checkfirst=True)
    activity_entity_type.drop(bind, checkfirst=True)
