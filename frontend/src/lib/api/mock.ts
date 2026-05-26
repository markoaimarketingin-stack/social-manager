import type {
  AudienceSegment,
  BrandProfile,
  BrandStrategy,
  AssistantCommandResult,
  ContentPlan,
  KnowledgeBaseDocument,
  PlannedPostStatus,
  PostDraft,
  TrainingJob,
  WorkflowRun,
  WorkspaceActivityEvent,
  WorkspaceActivitySummary,
  WorkspaceDetail,
} from "./types/domain";

type DemoStore = {
  workspace: WorkspaceDetail;
  brandProfile: BrandProfile | null;
  audienceSegments: AudienceSegment[];
  workflowRuns: WorkflowRun[];
  strategies: BrandStrategy[];
  contentPlans: ContentPlan[];
  drafts: PostDraft[];
  knowledgeBaseDocuments: KnowledgeBaseDocument[];
  trainingJobs: TrainingJob[];
  activity: WorkspaceActivityEvent[];
};

const STORAGE_KEY = "social_manager_demo_store_v1";
const wait = (ms = 180) => new Promise((resolve) => setTimeout(resolve, ms));

function rid(prefix: string): string {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`;
}

function nowIso(): string {
  return new Date().toISOString();
}

function addDays(days: number): string {
  const value = new Date();
  value.setDate(value.getDate() + days);
  return value.toISOString();
}

function addActivity(
  store: DemoStore,
  event: Omit<WorkspaceActivityEvent, "id" | "created_at" | "updated_at">,
): void {
  const timestamp = nowIso();
  store.activity.unshift({
    id: rid("activity"),
    created_at: timestamp,
    updated_at: timestamp,
    ...event,
  });
}

function activeStrategy(store: DemoStore): BrandStrategy | null {
  return store.strategies.find((item) => item.is_active) ?? store.strategies[0] ?? null;
}

function activePlan(store: DemoStore): ContentPlan | null {
  return store.contentPlans.find((item) => item.is_active) ?? store.contentPlans[0] ?? null;
}

function seedStore(): DemoStore {
  const workspaceId = "demo-workspace";
  const createdAt = nowIso();
  const strategyOneId = rid("strategy");
  const strategyTwoId = rid("strategy");
  const planOneId = rid("plan");
  const planTwoId = rid("plan");
  const pillarA = rid("pillar");
  const pillarB = rid("pillar");
  const plannedPostA = rid("post");
  const plannedPostB = rid("post");
  const plannedPostC = rid("post");
  const draftA = rid("draft");
  const draftB = rid("draft");
  const draftC = rid("draft");

  const store: DemoStore = {
    workspace: {
      id: workspaceId,
      name: "Myntra Social Command",
      slug: "myntra-social-command",
      brand_profile_id: rid("brand"),
      member_count: 4,
      audience_segment_count: 3,
      created_at: createdAt,
      updated_at: createdAt,
    },
    brandProfile: {
      id: rid("brand"),
      workspace_id: workspaceId,
      brand_name: "Myntra",
      industry: "Fashion commerce",
      description: "Style-led ecommerce brand with fast-moving campaign and creator cadence.",
      website_url: "https://www.myntra.com",
      voice_summary: "Bold, trend-aware, premium, playful, and fashion-confident.",
      mission: "Make fashion discovery feel current, expressive, and action-ready every day.",
      created_at: createdAt,
      updated_at: createdAt,
    },
    audienceSegments: [
      {
        id: rid("segment"),
        workspace_id: workspaceId,
        name: "Trend-first college shoppers",
        description: "High-frequency mobile audience looking for expressive style cues.",
        age_range: "18-24",
        interests: ["streetwear", "creator culture", "fashion reels"],
        primary_platform: "Instagram",
        messaging_angle: "Fresh drops, social proof, and style confidence.",
        created_at: createdAt,
        updated_at: createdAt,
      },
      {
        id: rid("segment"),
        workspace_id: workspaceId,
        name: "Urban young professionals",
        description: "Need practical yet elevated looks for hybrid work and weekends.",
        age_range: "24-32",
        interests: ["workwear", "lifestyle", "brand trust"],
        primary_platform: "LinkedIn",
        messaging_angle: "Easy styling, premium value, and decision confidence.",
        created_at: createdAt,
        updated_at: createdAt,
      },
      {
        id: rid("segment"),
        workspace_id: workspaceId,
        name: "Occasion-led festive shoppers",
        description: "Arrive for eventwear, gifting, and cultural styling inspiration.",
        age_range: "22-35",
        interests: ["festive wear", "wedding edits", "shopping events"],
        primary_platform: "Instagram",
        messaging_angle: "Shopable moments, curated edits, and event urgency.",
        created_at: createdAt,
        updated_at: createdAt,
      },
    ],
    workflowRuns: [],
    strategies: [
      {
        id: strategyTwoId,
        workspace_id: workspaceId,
        source_workflow_run_id: rid("run"),
        parent_strategy_id: strategyOneId,
        version_number: 2,
        is_active: true,
        status: "approved",
        title: "Myntra culture-forward social strategy",
        summary:
          "Shift the brand from generic fashion commerce to a visible culture engine with repeatable drop narratives and premium social proof.",
        positioning_statement:
          "Myntra helps style-aware shoppers feel plugged into what is next, not just what is on sale.",
        audience_focus:
          "Lead with young fashion-forward shoppers while translating trend momentum into trust-building formats for broader conversion cohorts.",
        channel_focus:
          "Instagram drives aspiration and cultural relevance, LinkedIn sharpens brand authority, and fast-turn social hooks get tested in short-form formats.",
        campaign_note:
          "Anchor the next two weeks around launch edits, creator styling, and proof-led outfit confidence.",
        review_notes: "Approved for founder demo and planning handoff.",
        reviewed_by_member_id: null,
        reviewed_at: addDays(-1),
        approved_at: addDays(-1),
        superseded_at: null,
        platform_plans: [
          {
            id: rid("platform"),
            brand_strategy_id: strategyTwoId,
            platform_name: "Instagram",
            objective: "Make Myntra feel like the source of what is current and wearable now.",
            cadence_summary: "4 posts weekly: one creator edit, one trend breakdown, one product proof reel, one social proof carousel.",
            content_mix: "Trend edits, style explainers, creator social proof, and conversion cues.",
            success_signal: "Higher saves, product detail taps, and branded content shares.",
            sort_order: 0,
            created_at: createdAt,
            updated_at: createdAt,
          },
          {
            id: rid("platform"),
            brand_strategy_id: strategyTwoId,
            platform_name: "LinkedIn",
            objective: "Show fashion-commerce operating sharpness and brand curation confidence.",
            cadence_summary: "2 weekly operator posts: one trend memo and one campaign breakdown.",
            content_mix: "Retail insight, creator strategy, and fashion consumer behavior.",
            success_signal: "Higher engagement from brand and growth operators.",
            sort_order: 1,
            created_at: createdAt,
            updated_at: createdAt,
          },
        ],
        content_pillars: [
          {
            id: pillarA,
            brand_strategy_id: strategyTwoId,
            name: "Trend translation",
            description: "Turn cultural signals into immediately wearable outfit ideas.",
            channel_angle: "Fast-moving trend explainers with strong fashion POV.",
            sort_order: 0,
            created_at: createdAt,
            updated_at: createdAt,
          },
          {
            id: pillarB,
            brand_strategy_id: strategyTwoId,
            name: "Confidence to purchase",
            description: "Reduce hesitation with styling proof, fit confidence, and creator validation.",
            channel_angle: "Proof-led reels, outfit stacks, and easy cart-building cues.",
            sort_order: 1,
            created_at: createdAt,
            updated_at: createdAt,
          },
        ],
        created_at: createdAt,
        updated_at: createdAt,
      },
      {
        id: strategyOneId,
        workspace_id: workspaceId,
        source_workflow_run_id: rid("run"),
        parent_strategy_id: null,
        version_number: 1,
        is_active: false,
        status: "approved",
        title: "Myntra demand-generation strategy",
        summary: "An earlier version centered on broad awareness and commerce-led calls to action.",
        positioning_statement: "Myntra brings discoverable fashion into one easy shopping surface.",
        audience_focus: "General urban online shoppers.",
        channel_focus: "Commerce messaging with lighter narrative depth.",
        campaign_note: "Original baseline prior to the culture-forward refinement.",
        review_notes: "Superseded by a stronger cultural POV.",
        reviewed_by_member_id: null,
        reviewed_at: addDays(-5),
        approved_at: addDays(-5),
        superseded_at: addDays(-2),
        platform_plans: [],
        content_pillars: [],
        created_at: createdAt,
        updated_at: createdAt,
      },
    ],
    contentPlans: [
      {
        id: planTwoId,
        workspace_id: workspaceId,
        brand_strategy_id: strategyTwoId,
        source_workflow_run_id: rid("run"),
        parent_plan_id: planOneId,
        version_number: 2,
        is_active: true,
        title: "Launch Edit planning cycle",
        planning_horizon_label: "Next 2 weeks",
        summary: "A founder-ready content cycle built around style edits, creator proof, and conversion confidence.",
        status: "approved",
        review_notes: "Locked for demo.",
        reviewed_by_member_id: null,
        reviewed_at: addDays(-1),
        approved_at: addDays(-1),
        superseded_at: null,
        planned_posts: [
          {
            id: plannedPostA,
            content_plan_id: planTwoId,
            workspace_id: workspaceId,
            brand_strategy_id: strategyTwoId,
            content_pillar_id: pillarA,
            sequence_number: 1,
            scheduled_for: addDays(1).slice(0, 10),
            platform: "Instagram",
            format: "Reel",
            title: "3 looks from the new drop",
            hook: "Show how one launch edit becomes three wearable identities.",
            angle: "Fast outfit transitions with creator energy and clear shopable cues.",
            call_to_action: "Save the looks and tap through to shop the edit.",
            status: "publish_ready",
            notes: "Lead with the strongest color story in the first two seconds.",
            approved_at: addDays(-1),
            publish_ready_at: addDays(-1),
            published_at: null,
            created_at: createdAt,
            updated_at: createdAt,
          },
          {
            id: plannedPostB,
            content_plan_id: planTwoId,
            workspace_id: workspaceId,
            brand_strategy_id: strategyTwoId,
            content_pillar_id: pillarB,
            sequence_number: 2,
            scheduled_for: addDays(3).slice(0, 10),
            platform: "Instagram",
            format: "Carousel",
            title: "Why this festive edit converts",
            hook: "Break down the proof points that make the edit easy to buy into.",
            angle: "Fit confidence, product proof, and occasion styling in one swipe narrative.",
            call_to_action: "Swipe, shortlist, and send the edit to your group chat.",
            status: "in_review",
            notes: "Need final pricing overlay review.",
            approved_at: null,
            publish_ready_at: null,
            published_at: null,
            created_at: createdAt,
            updated_at: createdAt,
          },
          {
            id: plannedPostC,
            content_plan_id: planTwoId,
            workspace_id: workspaceId,
            brand_strategy_id: strategyTwoId,
            content_pillar_id: pillarA,
            sequence_number: 3,
            scheduled_for: addDays(5).slice(0, 10),
            platform: "LinkedIn",
            format: "Operator memo",
            title: "What social signals say about fashion intent",
            hook: "Translate social interest spikes into practical commerce planning.",
            angle: "A crisp operator read on how trend-led creative feeds purchase confidence.",
            call_to_action: "Comment with the strongest demand signal you are seeing.",
            status: "approved",
            notes: "Ready to stage after legal copy review.",
            approved_at: addDays(-1),
            publish_ready_at: null,
            published_at: null,
            created_at: createdAt,
            updated_at: createdAt,
          },
        ],
        created_at: createdAt,
        updated_at: createdAt,
      },
      {
        id: planOneId,
        workspace_id: workspaceId,
        brand_strategy_id: strategyOneId,
        source_workflow_run_id: rid("run"),
        parent_plan_id: null,
        version_number: 1,
        is_active: false,
        title: "Baseline promo cycle",
        planning_horizon_label: "Previous cycle",
        summary: "The first plan version focused more on offer messaging and generic promo rhythm.",
        status: "approved",
        review_notes: "Superseded.",
        reviewed_by_member_id: null,
        reviewed_at: addDays(-4),
        approved_at: addDays(-4),
        superseded_at: addDays(-2),
        planned_posts: [],
        created_at: createdAt,
        updated_at: createdAt,
      },
    ],
    knowledgeBaseDocuments: [
      {
        id: rid("doc"),
        workspace_id: workspaceId,
        file_name: "brand_voice_guidelines.txt",
        category: "brand_voice",
        mime_type: "text/plain",
        size_bytes: 18420,
        ingestion_status: "ready",
        source: "demo_seed",
        uploaded_by_member_id: null,
        created_at: addDays(-2),
        updated_at: addDays(-2),
      },
      {
        id: rid("doc"),
        workspace_id: workspaceId,
        file_name: "campaign_brief_festival_launch.pdf",
        category: "campaign_brief",
        mime_type: "application/pdf",
        size_bytes: 342000,
        ingestion_status: "ready",
        source: "demo_seed",
        uploaded_by_member_id: null,
        created_at: addDays(-1),
        updated_at: addDays(-1),
      },
      {
        id: rid("doc"),
        workspace_id: workspaceId,
        file_name: "audience_segments.csv",
        category: "audience",
        mime_type: "text/csv",
        size_bytes: 12840,
        ingestion_status: "ready",
        source: "demo_seed",
        uploaded_by_member_id: null,
        created_at: createdAt,
        updated_at: createdAt,
      },
    ],
    trainingJobs: [],
    drafts: [
      {
        id: draftA,
        workspace_id: workspaceId,
        planned_post_id: plannedPostA,
        source_workflow_run_id: rid("run"),
        parent_draft_id: null,
        version_number: 1,
        is_current_version: true,
        title: "3 looks from the new drop",
        caption:
          "One launch. Three moods. One wardrobe update that actually feels current.\n\nFrom polished brunch energy to late-night statement fits, this edit moves with the plan.\n\nSave your favorite look and shop the full drop on Myntra.",
        creative_brief:
          "Dark-shell preview card with creator-led styling sequence, strong contrast, and premium fashion motion.",
        call_to_action: "Save and shop the full edit.",
        hashtags: ["#Myntra", "#StyleEdit", "#NewDrop"],
        review_status: "publish_ready",
        reviewer_notes: "Approved and queued for scheduling.",
        reviewer_member_id: null,
        reviewed_at: addDays(-1),
        approved_at: addDays(-1),
        publish_ready_at: addDays(-1),
        published_at: null,
        scheduled_publish_at: addDays(1),
        mock_publishing_receipt: null,
        created_at: createdAt,
        updated_at: createdAt,
      },
      {
        id: draftB,
        workspace_id: workspaceId,
        planned_post_id: plannedPostB,
        source_workflow_run_id: rid("run"),
        parent_draft_id: null,
        version_number: 1,
        is_current_version: true,
        title: "Why this festive edit converts",
        caption:
          "When the outfit already solves the occasion question, the purchase decision gets easier.\n\nThis carousel shows the fit, the feel, and the confidence cue in one swipe sequence.",
        creative_brief: "Proof-led carousel with fashion detail zooms and pricing callouts.",
        call_to_action: "Swipe and shortlist your favorite look.",
        hashtags: ["#FestiveStyle", "#MyntraFinds", "#FashionProof"],
        review_status: "in_review",
        reviewer_notes: "Tighten slide three CTA.",
        reviewer_member_id: null,
        reviewed_at: addDays(-1),
        approved_at: null,
        publish_ready_at: null,
        published_at: null,
        scheduled_publish_at: null,
        mock_publishing_receipt: null,
        created_at: createdAt,
        updated_at: createdAt,
      },
      {
        id: draftC,
        workspace_id: workspaceId,
        planned_post_id: plannedPostC,
        source_workflow_run_id: rid("run"),
        parent_draft_id: null,
        version_number: 1,
        is_current_version: true,
        title: "What social signals say about fashion intent",
        caption:
          "Social behavior is now one of the strongest early indicators of what converts next.\n\nHere is how we translate trend response into planning confidence without chasing noise.",
        creative_brief: "Clean memo-style graphic with operator framing and retail insight pull quotes.",
        call_to_action: "Comment with the signal your team trusts most.",
        hashtags: ["#RetailStrategy", "#SocialSignals", "#Myntra"],
        review_status: "approved",
        reviewer_notes: "Approved, can stage after scheduling slot opens.",
        reviewer_member_id: null,
        reviewed_at: addDays(-1),
        approved_at: addDays(-1),
        publish_ready_at: null,
        published_at: null,
        scheduled_publish_at: null,
        mock_publishing_receipt: null,
        created_at: createdAt,
        updated_at: createdAt,
      },
    ],
    activity: [],
  };

  store.workflowRuns = [
    {
      id: rid("run"),
      workspace_id: workspaceId,
      workflow_type: "draft",
      status: "completed",
      input_payload: { content_plan_id: planTwoId },
      output_payload: { generated_count: 3, content_plan_id: planTwoId },
      error_message: null,
      started_at: addDays(-1),
      completed_at: addDays(-1),
      initiated_by_member_id: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: rid("run"),
      workspace_id: workspaceId,
      workflow_type: "content_plan",
      status: "completed",
      input_payload: { brand_strategy_id: strategyTwoId },
      output_payload: { content_plan_id: planTwoId, planned_post_count: 3 },
      error_message: null,
      started_at: addDays(-2),
      completed_at: addDays(-2),
      initiated_by_member_id: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: rid("run"),
      workspace_id: workspaceId,
      workflow_type: "strategy",
      status: "completed",
      input_payload: { goal: "Refine brand positioning" },
      output_payload: { brand_strategy_id: strategyTwoId, version_number: 2 },
      error_message: null,
      started_at: addDays(-3),
      completed_at: addDays(-3),
      initiated_by_member_id: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
  ];

  addActivity(store, {
    workspace_id: workspaceId,
    actor_member_id: null,
    actor_label: "System",
    entity_type: "workspace",
    entity_id: workspaceId,
    event_type: "workspace_created",
    summary: "Created workspace 'Myntra Social Command'.",
    metadata_payload: {},
  });
  addActivity(store, {
    workspace_id: workspaceId,
    actor_member_id: null,
    actor_label: "Workflow",
    entity_type: "strategy",
    entity_id: strategyTwoId,
    event_type: "strategy_generated",
    summary: "Generated strategy v2: Myntra culture-forward social strategy.",
    metadata_payload: {},
  });
  addActivity(store, {
    workspace_id: workspaceId,
    actor_member_id: null,
    actor_label: "Reviewer",
    entity_type: "strategy",
    entity_id: strategyTwoId,
    event_type: "approval_granted",
    summary: "Approved strategy v2 for planning.",
    metadata_payload: {},
  });
  addActivity(store, {
    workspace_id: workspaceId,
    actor_member_id: null,
    actor_label: "Workflow",
    entity_type: "content_plan",
    entity_id: planTwoId,
    event_type: "content_plan_generated",
    summary: "Generated content plan v2: Launch Edit planning cycle.",
    metadata_payload: {},
  });
  addActivity(store, {
    workspace_id: workspaceId,
    actor_member_id: null,
    actor_label: "Reviewer",
    entity_type: "post_draft",
    entity_id: draftA,
    event_type: "publish_ready",
    summary: "Moved draft '3 looks from the new drop' into the publish-ready queue.",
    metadata_payload: {},
  });

  return store;
}

function readStore(): DemoStore {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    const seeded = seedStore();
    writeStore(seeded);
    return seeded;
  }

  try {
    const parsed = JSON.parse(raw) as DemoStore;
    const seeded = seedStore();
    return {
      ...seeded,
      ...parsed,
      knowledgeBaseDocuments: parsed.knowledgeBaseDocuments ?? seeded.knowledgeBaseDocuments,
      trainingJobs: parsed.trainingJobs ?? [],
    };
  } catch {
    const seeded = seedStore();
    writeStore(seeded);
    return seeded;
  }
}

function writeStore(store: DemoStore): void {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

function summarizeActivity(store: DemoStore): WorkspaceActivitySummary {
  return {
    total_events: store.activity.length,
    workflow_completions: store.activity.filter((item) => item.event_type === "workflow_completed").length,
    approvals: store.activity.filter((item) => item.event_type === "approval_granted").length,
    publish_ready_items: store.drafts.filter((item) => item.review_status === "publish_ready").length,
    latest_event_at: store.activity[0]?.created_at ?? null,
    latest_summary: store.activity[0]?.summary ?? null,
  };
}

export async function mockRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const method = (init?.method ?? "GET").toUpperCase();
  const delay = method === "GET" ? 200 : Math.floor(Math.random() * 800) + 800; // longer delay for mutations to feel real
  await wait(delay);
  const body = init?.body ? (JSON.parse(init.body.toString()) as Record<string, unknown>) : null;
  const store = readStore();

  const workspaceId = store.workspace.id;

  if (path === "/api/v1/system/status") {
    return {
      status: "ok",
      service: "social-manager-api",
      environment: "demo",
      database: "connected",
    } as T;
  }

  if (path === "/api/v1/workspaces" && method === "POST" && body) {
    const timestamp = nowIso();
    store.workspace = {
      ...store.workspace,
      id: rid("workspace"),
      slug: String(body.name ?? "demo-workspace").toLowerCase().replace(/\s+/g, "-"),
      name: String(body.name ?? "Demo Workspace"),
      created_at: timestamp,
      updated_at: timestamp,
    };
    addActivity(store, {
      workspace_id: store.workspace.id,
      actor_member_id: null,
      actor_label: String((body.owner as { full_name?: string } | undefined)?.full_name ?? "Demo User"),
      entity_type: "workspace",
      entity_id: store.workspace.id,
      event_type: "workspace_created",
      summary: `Created workspace '${store.workspace.name}'.`,
      metadata_payload: {},
    });
    writeStore(store);
    return store.workspace as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}`) {
    store.workspace.brand_profile_id = store.brandProfile?.id ?? null;
    store.workspace.audience_segment_count = store.audienceSegments.length;
    writeStore(store);
    return store.workspace as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/knowledge-base/documents` && method === "GET") {
    return store.knowledgeBaseDocuments as T;
  }
  if (path === `/api/v1/workspaces/${workspaceId}/knowledge-base/documents` && method === "POST" && body) {
    const timestamp = nowIso();
    const document: KnowledgeBaseDocument = {
      id: rid("doc"),
      workspace_id: workspaceId,
      file_name: String(body.file_name ?? "untitled"),
      category: body.category as KnowledgeBaseDocument["category"],
      mime_type: String(body.mime_type ?? "application/octet-stream"),
      size_bytes: Number(body.size_bytes ?? 0),
      ingestion_status: "ready",
      source: "upload",
      uploaded_by_member_id: (body.uploaded_by_member_id as string | null | undefined) ?? null,
      created_at: timestamp,
      updated_at: timestamp,
    };
    store.knowledgeBaseDocuments.unshift(document);
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Operator",
      entity_type: "knowledge_document",
      entity_id: document.id,
      event_type: "document_uploaded",
      summary: `Uploaded knowledge document '${document.file_name}'.`,
      metadata_payload: { category: document.category, size_bytes: document.size_bytes },
    });
    writeStore(store);
    return document as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/training-jobs` && method === "GET") {
    return store.trainingJobs as T;
  }
  if (path === `/api/v1/workspaces/${workspaceId}/training-jobs` && method === "POST" && body) {
    const timestamp = nowIso();
    const job: TrainingJob = {
      id: rid("training"),
      workspace_id: workspaceId,
      document_ids: (body.document_ids as string[]) ?? store.knowledgeBaseDocuments.map((doc) => doc.id),
      category: (body.category as TrainingJob["category"]) ?? "brand_voice",
      status: "completed",
      created_at: timestamp,
      updated_at: timestamp,
    };
    store.trainingJobs.unshift(job);
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Trainer",
      entity_type: "training_job",
      entity_id: job.id,
      event_type: "training_queued",
      summary: `Queued model training with ${job.document_ids.length} document${job.document_ids.length === 1 ? "" : "s"}.`,
      metadata_payload: { category: job.category, document_ids: job.document_ids },
    });
    writeStore(store);
    return job as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/assistant/commands` && method === "POST" && body) {
    const timestamp = nowIso();
    const prompt = String(body.prompt ?? "");
    const result: AssistantCommandResult = {
      id: rid("assistant"),
      workspace_id: workspaceId,
      route_context: String(body.route_context ?? "workspace"),
      mode: (body.mode as AssistantCommandResult["mode"]) ?? "ask",
      prompt,
      response: `Logged '${prompt}' against ${String(body.route_context ?? "workspace")} in demo mode.`,
      created_at: timestamp,
    };
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Assistant",
      entity_type: "assistant_command",
      entity_id: result.id,
      event_type: "assistant_command_logged",
      summary: `Assistant command logged: ${prompt.slice(0, 80)}${prompt.length > 80 ? "..." : ""}`,
      metadata_payload: { route_context: result.route_context, mode: result.mode },
    });
    writeStore(store);
    return result as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/brand-profile`) {
    if (method === "GET") {
      if (!store.brandProfile) {
        throw new Error("Not found");
      }
      return store.brandProfile as T;
    }
    if (method === "PUT" && body) {
      const timestamp = nowIso();
      store.brandProfile = {
        id: store.brandProfile?.id ?? rid("brand"),
        workspace_id: workspaceId,
        brand_name: String(body.brand_name ?? ""),
        industry: String(body.industry ?? ""),
        description: String(body.description ?? ""),
        website_url: (body.website_url as string | null) ?? null,
        voice_summary: String(body.voice_summary ?? ""),
        mission: String(body.mission ?? ""),
        created_at: store.brandProfile?.created_at ?? timestamp,
        updated_at: timestamp,
      };
      store.workspace.brand_profile_id = store.brandProfile.id;
      writeStore(store);
      return store.brandProfile as T;
    }
  }

  if (path === `/api/v1/workspaces/${workspaceId}/audience-segments` && method === "GET") {
    return store.audienceSegments as T;
  }
  if (path === `/api/v1/workspaces/${workspaceId}/audience-segments` && method === "POST" && body) {
    const timestamp = nowIso();
    const segment: AudienceSegment = {
      id: rid("segment"),
      workspace_id: workspaceId,
      name: String(body.name ?? ""),
      description: String(body.description ?? ""),
      age_range: String(body.age_range ?? ""),
      interests: (body.interests as string[]) ?? [],
      primary_platform: String(body.primary_platform ?? ""),
      messaging_angle: String(body.messaging_angle ?? ""),
      created_at: timestamp,
      updated_at: timestamp,
    };
    store.audienceSegments.unshift(segment);
    store.workspace.audience_segment_count = store.audienceSegments.length;
    writeStore(store);
    return segment as T;
  }

  const updateSegmentMatch = path.match(new RegExp(`/api/v1/workspaces/${workspaceId}/audience-segments/([^/]+)$`));
  if (updateSegmentMatch && body && method === "PUT") {
    const segmentId = updateSegmentMatch[1];
    store.audienceSegments = store.audienceSegments.map((item) =>
      item.id === segmentId
        ? {
            ...item,
            name: String(body.name ?? item.name),
            description: String(body.description ?? item.description ?? ""),
            age_range: String(body.age_range ?? item.age_range ?? ""),
            interests: (body.interests as string[]) ?? item.interests,
            primary_platform: String(body.primary_platform ?? item.primary_platform ?? ""),
            messaging_angle: String(body.messaging_angle ?? item.messaging_angle ?? ""),
            updated_at: nowIso(),
          }
        : item,
    );
    writeStore(store);
    return store.audienceSegments.find((item) => item.id === segmentId) as T;
  }
  if (updateSegmentMatch && method === "DELETE") {
    store.audienceSegments = store.audienceSegments.filter((item) => item.id !== updateSegmentMatch[1]);
    store.workspace.audience_segment_count = store.audienceSegments.length;
    writeStore(store);
    return undefined as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/workflow-runs`) {
    return store.workflowRuns as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/strategies`) {
    return store.strategies as T;
  }
  if (path === `/api/v1/workspaces/${workspaceId}/strategies/latest`) {
    return activeStrategy(store) as T;
  }
  const strategyReviewMatch = path.match(/\/api\/v1\/strategies\/([^/]+)\/review$/);
  if (strategyReviewMatch && method === "PATCH" && body) {
    const strategyId = strategyReviewMatch[1];
    store.strategies = store.strategies.map((item) =>
      item.id === strategyId
        ? {
            ...item,
            status: body.status as BrandStrategy["status"],
            review_notes: (body.review_notes as string | null) ?? null,
            reviewed_at: nowIso(),
            approved_at: body.status === "approved" ? nowIso() : item.approved_at,
            updated_at: nowIso(),
          }
        : item,
    );
    const strategy = store.strategies.find((item) => item.id === strategyId)!;
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Reviewer",
      entity_type: "strategy",
      entity_id: strategyId,
      event_type: "strategy_reviewed",
      summary: `Reviewed strategy v${strategy.version_number} as ${strategy.status}.`,
      metadata_payload: {},
    });
    if (strategy.status === "approved") {
      addActivity(store, {
        workspace_id: workspaceId,
        actor_member_id: null,
        actor_label: "Reviewer",
        entity_type: "strategy",
        entity_id: strategyId,
        event_type: "approval_granted",
        summary: `Approved strategy v${strategy.version_number} for planning.`,
        metadata_payload: {},
      });
    }
    writeStore(store);
    return strategy as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/content-plans`) {
    return store.contentPlans as T;
  }
  if (path === `/api/v1/workspaces/${workspaceId}/content-plans/latest`) {
    return activePlan(store) as T;
  }
  const postMatch = path.match(/\/api\/v1\/planned-posts\/([^/]+)$/);
  if (postMatch && method === "PUT" && body) {
    const postId = postMatch[1];
    store.contentPlans = store.contentPlans.map((plan) => ({
      ...plan,
      planned_posts: plan.planned_posts.map((post) =>
        post.id === postId
          ? {
              ...post,
              scheduled_for: String(body.scheduled_for ?? post.scheduled_for),
              platform: String(body.platform ?? post.platform),
              format: String(body.format ?? post.format),
              title: String(body.title ?? post.title),
              hook: String(body.hook ?? post.hook),
              angle: String(body.angle ?? post.angle),
              call_to_action: String(body.call_to_action ?? post.call_to_action),
              status: body.status as PlannedPostStatus,
              notes: (body.notes as string | null) ?? null,
              updated_at: nowIso(),
            }
          : post,
      ),
    }));
    const updated = store.contentPlans.flatMap((plan) => plan.planned_posts).find((post) => post.id === postId)!;
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Operator",
      entity_type: "planned_post",
      entity_id: updated.id,
      event_type: "planned_post_edited",
      summary: `Updated planned post '${updated.title}' to ${updated.status}.`,
      metadata_payload: {},
    });
    writeStore(store);
    return updated as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/drafts`) {
    return store.drafts as T;
  }
  if (path === `/api/v1/workspaces/${workspaceId}/drafts/review-queue`) {
    return store.drafts.filter((item) => ["in_review", "draft", "changes_requested"].includes(item.review_status)) as T;
  }
  if (path === `/api/v1/workspaces/${workspaceId}/drafts/publishing-queue`) {
    return store.drafts.filter((item) => item.review_status === "publish_ready") as T;
  }
  const draftMatch = path.match(/\/api\/v1\/drafts\/([^/]+)$/);
  if (draftMatch && method === "PUT" && body) {
    const draftId = draftMatch[1];
    store.drafts = store.drafts.map((item) =>
      item.id === draftId
        ? {
            ...item,
            title: String(body.title ?? item.title),
            caption: String(body.caption ?? item.caption),
            creative_brief: String(body.creative_brief ?? item.creative_brief),
            call_to_action: String(body.call_to_action ?? item.call_to_action),
            hashtags: (body.hashtags as string[]) ?? item.hashtags,
            review_status: body.review_status as PostDraft["review_status"],
            reviewer_notes: (body.reviewer_notes as string | null) ?? null,
            scheduled_publish_at: (body.scheduled_publish_at as string | null) ?? item.scheduled_publish_at,
            reviewed_at: nowIso(),
            approved_at: body.review_status === "approved" ? nowIso() : item.approved_at,
            updated_at: nowIso(),
          }
        : item,
    );
    const draft = store.drafts.find((item) => item.id === draftId)!;
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Reviewer",
      entity_type: "post_draft",
      entity_id: draftId,
      event_type: "review_status_changed",
      summary: `Updated draft '${draft.title}' to ${draft.review_status}.`,
      metadata_payload: {},
    });
    writeStore(store);
    return draft as T;
  }
  const publishReadyMatch = path.match(/\/api\/v1\/drafts\/([^/]+)\/publish-ready$/);
  if (publishReadyMatch && method === "POST") {
    const draftId = publishReadyMatch[1];
    store.drafts = store.drafts.map((item) =>
      item.id === draftId
        ? {
            ...item,
            review_status: "publish_ready",
            publish_ready_at: nowIso(),
            scheduled_publish_at: (body?.scheduled_publish_at as string | null) ?? item.scheduled_publish_at,
            updated_at: nowIso(),
          }
        : item,
    );
    const draft = store.drafts.find((item) => item.id === draftId)!;
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Reviewer",
      entity_type: "post_draft",
      entity_id: draftId,
      event_type: "publish_ready",
      summary: `Moved draft '${draft.title}' into the publish-ready queue.`,
      metadata_payload: {},
    });
    writeStore(store);
    return draft as T;
  }
  const publishMatch = path.match(/\/api\/v1\/drafts\/([^/]+)\/publish$/);
  if (publishMatch && method === "POST") {
    const draftId = publishMatch[1];
    store.drafts = store.drafts.map((item) =>
      item.id === draftId
        ? {
            ...item,
            review_status: "published",
            published_at: nowIso(),
            mock_publishing_receipt: {
              receipt_id: rid("receipt"),
              provider: "demo_mode",
              published_at: nowIso(),
            },
            updated_at: nowIso(),
          }
        : item,
    );
    const draft = store.drafts.find((item) => item.id === draftId)!;
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Publisher",
      entity_type: "post_draft",
      entity_id: draftId,
      event_type: "published",
      summary: `Published draft '${draft.title}' with a demo receipt.`,
      metadata_payload: draft.mock_publishing_receipt ?? {},
    });
    writeStore(store);
    return draft as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/activity`) {
    return store.activity as T;
  }
  if (path === `/api/v1/workspaces/${workspaceId}/activity/summary`) {
    return summarizeActivity(store) as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/strategy-runs` && method === "POST") {
    const current = activeStrategy(store);
    const timestamp = nowIso();
    const run: WorkflowRun = {
      id: rid("run"),
      workspace_id: workspaceId,
      workflow_type: "strategy",
      status: "completed",
      input_payload: body ?? {},
      output_payload: {},
      error_message: null,
      started_at: timestamp,
      completed_at: timestamp,
      initiated_by_member_id: null,
      created_at: timestamp,
      updated_at: timestamp,
    };
    const strategyId = rid("strategy");
    if (current) {
      current.is_active = false;
      current.superseded_at = timestamp;
    }
    const next: BrandStrategy = {
      ...(current ?? seedStore().strategies[0]),
      id: strategyId,
      source_workflow_run_id: run.id,
      parent_strategy_id: current?.id ?? null,
      version_number: (current?.version_number ?? 0) + 1,
      is_active: true,
      status: "in_review",
      title: `${store.brandProfile?.brand_name ?? "Brand"} signal-led strategy v${(current?.version_number ?? 0) + 1}`,
      summary:
        "A refreshed strategy run that sharpens the social narrative around product confidence, creator proof, and launch-cycle urgency.",
      review_notes: "Freshly generated in demo mode.",
      reviewed_at: null,
      approved_at: null,
      superseded_at: null,
      created_at: timestamp,
      updated_at: timestamp,
    };
    store.strategies.unshift(next);
    run.output_payload = { brand_strategy_id: strategyId, version_number: next.version_number };
    store.workflowRuns.unshift(run);
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Workflow",
      entity_type: "strategy",
      entity_id: strategyId,
      event_type: "strategy_generated",
      summary: `Generated strategy v${next.version_number}: ${next.title}.`,
      metadata_payload: {},
    });
    writeStore(store);
    return run as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/content-plan-runs` && method === "POST") {
    const current = activePlan(store);
    const strategy = activeStrategy(store)!;
    const timestamp = nowIso();
    const run: WorkflowRun = {
      id: rid("run"),
      workspace_id: workspaceId,
      workflow_type: "content_plan",
      status: "completed",
      input_payload: body ?? {},
      output_payload: {},
      error_message: null,
      started_at: timestamp,
      completed_at: timestamp,
      initiated_by_member_id: null,
      created_at: timestamp,
      updated_at: timestamp,
    };
    if (current) {
      current.is_active = false;
      current.superseded_at = timestamp;
    }
    const newPlanId = rid("plan");
    const plan: ContentPlan = {
      ...(current ?? store.contentPlans[0]),
      id: newPlanId,
      source_workflow_run_id: run.id,
      parent_plan_id: current?.id ?? null,
      version_number: (current?.version_number ?? 0) + 1,
      is_active: true,
      brand_strategy_id: strategy.id,
      title: `${strategy.title} planning cycle`,
      summary: "A regenerated planning cycle with updated scheduling, tighter hooks, and clearer publish staging.",
      status: "in_review",
      review_notes: "Regenerated in demo mode.",
      reviewed_at: null,
      approved_at: null,
      superseded_at: null,
      planned_posts: (current?.planned_posts ?? store.contentPlans[0].planned_posts).map((post, index) => ({
        ...post,
        id: rid("post"),
        content_plan_id: newPlanId,
        sequence_number: index + 1,
        scheduled_for: addDays(index + 1).slice(0, 10),
        status: index === 0 ? "planned" : "in_review",
        approved_at: null,
        publish_ready_at: null,
        published_at: null,
        created_at: timestamp,
        updated_at: timestamp,
      })),
      created_at: timestamp,
      updated_at: timestamp,
    };
    store.contentPlans.unshift(plan);
    run.output_payload = { content_plan_id: newPlanId, planned_post_count: plan.planned_posts.length };
    store.workflowRuns.unshift(run);
    addActivity(store, {
      workspace_id: workspaceId,
      actor_member_id: null,
      actor_label: "Workflow",
      entity_type: "content_plan",
      entity_id: newPlanId,
      event_type: "content_plan_generated",
      summary: `Generated content plan v${plan.version_number}: ${plan.title}.`,
      metadata_payload: {},
    });
    writeStore(store);
    return run as T;
  }

  if (path === `/api/v1/workspaces/${workspaceId}/draft-runs` && method === "POST") {
    const plan = activePlan(store)!;
    const timestamp = nowIso();
    const run: WorkflowRun = {
      id: rid("run"),
      workspace_id: workspaceId,
      workflow_type: "draft",
      status: "completed",
      input_payload: body ?? {},
      output_payload: {},
      error_message: null,
      started_at: timestamp,
      completed_at: timestamp,
      initiated_by_member_id: null,
      created_at: timestamp,
      updated_at: timestamp,
    };
    const generated: PostDraft[] = plan.planned_posts.map((post) => ({
      id: rid("draft"),
      workspace_id: workspaceId,
      planned_post_id: post.id,
      source_workflow_run_id: run.id,
      parent_draft_id: store.drafts.find((item) => item.planned_post_id === post.id && item.is_current_version)?.id ?? null,
      version_number: 1,
      is_current_version: true,
      title: post.title,
      caption: `${post.hook}\n\n${post.angle}\n\n${post.call_to_action}`,
      creative_brief: `Demo-generated creative brief for ${post.title}.`,
      call_to_action: post.call_to_action,
      hashtags: ["#MarkoAI", "#DemoMode", `#${post.platform.replace(/\s+/g, "")}`],
      review_status: "in_review",
      reviewer_notes: null,
      reviewer_member_id: null,
      reviewed_at: null,
      approved_at: null,
      publish_ready_at: null,
      published_at: null,
      scheduled_publish_at: null,
      mock_publishing_receipt: null,
      created_at: timestamp,
      updated_at: timestamp,
    }));
    store.drafts = [...generated, ...store.drafts];
    run.output_payload = { content_plan_id: plan.id, generated_count: generated.length };
    store.workflowRuns.unshift(run);
    generated.forEach((draft) => {
      addActivity(store, {
        workspace_id: workspaceId,
        actor_member_id: null,
        actor_label: "Workflow",
        entity_type: "post_draft",
        entity_id: draft.id,
        event_type: "draft_generated",
        summary: `Generated draft v${draft.version_number} for '${draft.title}'.`,
        metadata_payload: {},
      });
    });
    writeStore(store);
    return run as T;
  }

  throw new Error(`Mock route not implemented: ${method} ${path}`);
}

export function isDemoModeEnabled(): boolean {
  return import.meta.env.VITE_DEMO_MODE === "true";
}
