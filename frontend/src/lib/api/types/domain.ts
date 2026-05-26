export type Workspace = {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
};

export type WorkspaceDetail = Workspace & {
  brand_profile_id: string | null;
  member_count: number;
  audience_segment_count: number;
};

export type BrandProfile = {
  id: string;
  workspace_id: string;
  brand_name: string;
  industry: string;
  description: string | null;
  website_url: string | null;
  voice_summary: string | null;
  mission: string | null;
  created_at: string;
  updated_at: string;
};

export type AudienceSegment = {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  age_range: string | null;
  interests: string[];
  primary_platform: string | null;
  messaging_angle: string | null;
  created_at: string;
  updated_at: string;
};

export type WorkflowRun = {
  id: string;
  workspace_id: string;
  workflow_type: "strategy" | "content_plan" | "draft";
  status: "pending" | "running" | "completed" | "failed";
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown> | null;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
  initiated_by_member_id: string | null;
  created_at: string;
  updated_at: string;
};

export type StrategyStatus = "draft" | "in_review" | "approved" | "needs_revision";
export type StrategyStatusExtended = StrategyStatus | "rejected";

export type PlatformPlan = {
  id: string;
  brand_strategy_id: string;
  platform_name: string;
  objective: string;
  cadence_summary: string;
  content_mix: string;
  success_signal: string;
  sort_order: number;
  created_at: string;
  updated_at: string;
};

export type ContentPillar = {
  id: string;
  brand_strategy_id: string;
  name: string;
  description: string;
  channel_angle: string;
  sort_order: number;
  created_at: string;
  updated_at: string;
};

export type BrandStrategy = {
  id: string;
  workspace_id: string;
  source_workflow_run_id: string | null;
  parent_strategy_id: string | null;
  version_number: number;
  is_active: boolean;
  status: StrategyStatusExtended;
  title: string;
  summary: string;
  positioning_statement: string;
  audience_focus: string;
  channel_focus: string;
  campaign_note: string | null;
  review_notes: string | null;
  reviewed_by_member_id: string | null;
  reviewed_at: string | null;
  approved_at: string | null;
  superseded_at: string | null;
  platform_plans: PlatformPlan[];
  content_pillars: ContentPillar[];
  created_at: string;
  updated_at: string;
};

export type PlannedPostStatus =
  | "planned"
  | "drafted"
  | "in_review"
  | "approved"
  | "publish_ready"
  | "published"
  | "rejected"
  | "ready_for_review";

export type PlannedPost = {
  id: string;
  content_plan_id: string;
  workspace_id: string;
  brand_strategy_id: string;
  content_pillar_id: string | null;
  sequence_number: number;
  scheduled_for: string;
  platform: string;
  format: string;
  title: string;
  hook: string;
  angle: string;
  call_to_action: string;
  status: PlannedPostStatus;
  notes: string | null;
  approved_at: string | null;
  publish_ready_at: string | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ContentPlanStatus = "draft" | "in_review" | "approved" | "ready";

export type ContentPlan = {
  id: string;
  workspace_id: string;
  brand_strategy_id: string;
  source_workflow_run_id: string | null;
  parent_plan_id: string | null;
  version_number: number;
  is_active: boolean;
  title: string;
  planning_horizon_label: string;
  summary: string;
  status: ContentPlanStatus;
  review_notes: string | null;
  reviewed_by_member_id: string | null;
  reviewed_at: string | null;
  approved_at: string | null;
  superseded_at: string | null;
  planned_posts: PlannedPost[];
  created_at: string;
  updated_at: string;
};

export type DraftReviewStatus =
  | "draft"
  | "in_review"
  | "pending_review"
  | "approved"
  | "publish_ready"
  | "published"
  | "rejected"
  | "changes_requested";

export type PostDraft = {
  id: string;
  workspace_id: string;
  planned_post_id: string;
  source_workflow_run_id: string | null;
  parent_draft_id: string | null;
  version_number: number;
  is_current_version: boolean;
  title: string;
  caption: string;
  creative_brief: string;
  call_to_action: string;
  hashtags: string[];
  review_status: DraftReviewStatus;
  reviewer_notes: string | null;
  reviewer_member_id: string | null;
  reviewed_at: string | null;
  approved_at: string | null;
  publish_ready_at: string | null;
  published_at: string | null;
  scheduled_publish_at: string | null;
  mock_publishing_receipt: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type KnowledgeBaseDocument = {
  id: string;
  workspace_id: string;
  file_name: string;
  category: "brand_voice" | "campaign_brief" | "audience" | "competitors" | "social_strategy" | "asset";
  mime_type: string;
  size_bytes: number;
  ingestion_status: "queued" | "processing" | "ready" | "failed";
  source: "upload" | "demo_seed";
  uploaded_by_member_id: string | null;
  created_at: string;
  updated_at: string;
};

export type TrainingJob = {
  id: string;
  workspace_id: string;
  document_ids: string[];
  category: KnowledgeBaseDocument["category"];
  status: "queued" | "processing" | "completed" | "failed";
  created_at: string;
  updated_at: string;
};

export type AssistantCommandResult = {
  id: string;
  workspace_id: string;
  route_context: string;
  mode: "ask" | "agent";
  prompt: string;
  response: string;
  created_at: string;
};

export type ActivityEntityType =
  | "workspace"
  | "strategy"
  | "content_plan"
  | "planned_post"
  | "post_draft"
  | "knowledge_document"
  | "training_job"
  | "assistant_command"
  | "workflow_run";

export type ActivityEventType =
  | "workspace_created"
  | "strategy_generated"
  | "strategy_reviewed"
  | "content_plan_generated"
  | "planned_post_edited"
  | "draft_generated"
  | "draft_updated"
  | "review_status_changed"
  | "approval_granted"
  | "publish_ready"
  | "published"
  | "document_uploaded"
  | "training_queued"
  | "assistant_command_logged"
  | "workflow_completed"
  | "workflow_failed";

export type WorkspaceActivityEvent = {
  id: string;
  workspace_id: string;
  actor_member_id: string | null;
  actor_label: string | null;
  entity_type: ActivityEntityType;
  entity_id: string | null;
  event_type: ActivityEventType;
  summary: string;
  metadata_payload: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type WorkspaceActivitySummary = {
  total_events: number;
  workflow_completions: number;
  approvals: number;
  publish_ready_items: number;
  latest_event_at: string | null;
  latest_summary: string | null;
};

export type HealthStatus = {
  status: string;
  service: string;
  environment: string;
};

export type SystemStatus = HealthStatus & {
  database: string;
};
