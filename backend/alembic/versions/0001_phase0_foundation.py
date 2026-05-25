"""phase0 foundation

Revision ID: 0001_phase0_foundation
Revises: 
Create Date: 2026-05-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_phase0_foundation"
down_revision = None
branch_labels = None
depends_on = None


member_role = sa.Enum("OWNER", "MANAGER", name="memberrole")
workflow_type = sa.Enum("STRATEGY", name="workflowtype")
workflow_status = sa.Enum("PENDING", "COMPLETED", "FAILED", name="workflowstatus")


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workspaces_slug"), "workspaces", ["slug"], unique=True)

    op.create_table(
        "members",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", member_role, nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_members_workspace_id"), "members", ["workspace_id"], unique=False)

    op.create_table(
        "brand_profiles",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("brand_name", sa.String(length=120), nullable=False),
        sa.Column("industry", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website_url", sa.String(length=255), nullable=True),
        sa.Column("voice_summary", sa.Text(), nullable=True),
        sa.Column("mission", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id"),
    )
    op.create_index(op.f("ix_brand_profiles_workspace_id"), "brand_profiles", ["workspace_id"], unique=True)

    op.create_table(
        "audience_segments",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("age_range", sa.String(length=80), nullable=True),
        sa.Column("interests", sa.JSON(), nullable=False),
        sa.Column("primary_platform", sa.String(length=80), nullable=True),
        sa.Column("messaging_angle", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audience_segments_workspace_id"),
        "audience_segments",
        ["workspace_id"],
        unique=False,
    )

    op.create_table(
        "workflow_runs",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("workflow_type", workflow_type, nullable=False),
        sa.Column("status", workflow_status, nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("initiated_by_member_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workflow_runs_workspace_id"), "workflow_runs", ["workspace_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_workflow_runs_workspace_id"), table_name="workflow_runs")
    op.drop_table("workflow_runs")
    op.drop_index(op.f("ix_audience_segments_workspace_id"), table_name="audience_segments")
    op.drop_table("audience_segments")
    op.drop_index(op.f("ix_brand_profiles_workspace_id"), table_name="brand_profiles")
    op.drop_table("brand_profiles")
    op.drop_index(op.f("ix_members_workspace_id"), table_name="members")
    op.drop_table("members")
    op.drop_index(op.f("ix_workspaces_slug"), table_name="workspaces")
    op.drop_table("workspaces")

    workflow_status.drop(op.get_bind(), checkfirst=False)
    workflow_type.drop(op.get_bind(), checkfirst=False)
    member_role.drop(op.get_bind(), checkfirst=False)
