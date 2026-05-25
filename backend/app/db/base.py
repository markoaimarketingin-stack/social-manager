from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative model for the application."""


def import_models() -> None:
    from app.modules.activity_events import models as activity_event_models  # noqa: F401
    from app.modules.audience_segments import models as audience_segment_models  # noqa: F401
    from app.modules.brand_strategies import models as brand_strategy_models  # noqa: F401
    from app.modules.brand_profiles import models as brand_profile_models  # noqa: F401
    from app.modules.content_plans import models as content_plan_models  # noqa: F401
    from app.modules.members import models as member_models  # noqa: F401
    from app.modules.post_drafts import models as post_draft_models  # noqa: F401
    from app.modules.workflow_runs import models as workflow_run_models  # noqa: F401
    from app.modules.workspaces import models as workspace_models  # noqa: F401
