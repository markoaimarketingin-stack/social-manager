export type CreateWorkspaceRequest = {
  name: string;
  owner: {
    full_name: string;
    email: string;
  };
};

export type UpsertBrandProfileRequest = {
  brand_name: string;
  industry: string;
  description: string;
  website_url: string | null;
  voice_summary: string;
  mission: string;
};

export type CreateAudienceSegmentRequest = {
  name: string;
  description: string;
  age_range: string;
  interests: string[];
  primary_platform: string;
  messaging_angle: string;
};

export type UpdateAudienceSegmentRequest = CreateAudienceSegmentRequest;

export type StartStrategyRunRequest = {
  goal: string;
  initiated_by_member_id?: string | null;
};

export type ReviewStrategyRequest = {
  status: "draft" | "in_review" | "approved" | "needs_revision" | "rejected";
  review_notes: string | null;
  reviewer_member_id?: string | null;
};

export type StartContentPlanRunRequest = {
  brand_strategy_id?: string | null;
  planning_horizon_label: string;
  initiated_by_member_id?: string | null;
};

export type UpdatePlannedPostRequest = {
  scheduled_for: string;
  platform: string;
  format: string;
  title: string;
  hook: string;
  angle: string;
  call_to_action: string;
  status:
    | "planned"
    | "drafted"
    | "in_review"
    | "approved"
    | "publish_ready"
    | "published"
    | "rejected"
    | "ready_for_review";
  notes: string | null;
  reviewer_member_id?: string | null;
};

export type StartDraftRunRequest = {
  content_plan_id?: string | null;
  initiated_by_member_id?: string | null;
};

export type UpdateDraftRequest = {
  title: string;
  caption: string;
  creative_brief: string;
  call_to_action: string;
  hashtags: string[];
  review_status:
    | "draft"
    | "in_review"
    | "pending_review"
    | "approved"
    | "publish_ready"
    | "published"
    | "rejected"
    | "changes_requested";
  reviewer_notes: string | null;
  reviewer_member_id?: string | null;
  scheduled_publish_at?: string | null;
};

export type MarkDraftPublishReadyRequest = {
  reviewer_member_id?: string | null;
  scheduled_publish_at?: string | null;
};

export type PublishDraftRequest = {
  reviewer_member_id?: string | null;
};
