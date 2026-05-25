import { Link } from "react-router-dom";

import { Panel } from "../../../components/ui/Panel";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { StatusPill } from "../../../components/ui/StatusPill";
import { useWorkspaceContext } from "../hooks/useWorkspaceContext";

const formatTimestamp = (value: string | null | undefined) =>
  value
    ? new Date(value).toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      })
    : "No activity yet";

const workflowTone = (status: string) =>
  status === "completed" ? "success" : status === "failed" ? "warning" : "neutral";

export function WorkspaceOverviewPage() {
  const {
    workspaceId,
    workspaceQuery,
    brandProfileQuery,
    workflowRunsQuery,
    latestStrategyQuery,
    latestContentPlanQuery,
    reviewQueueQuery,
    publishingQueueQuery,
    activityQuery,
    activitySummaryQuery,
  } = useWorkspaceContext();

  const workflowRuns = workflowRunsQuery.data ?? [];
  const activityEvents = activityQuery.data ?? [];
  const publishReadyQueue = publishingQueueQuery.data ?? [];
  const pendingReviews = reviewQueueQuery.data ?? [];
  const latestStrategy = latestStrategyQuery.data ?? null;
  const latestPlan = latestContentPlanQuery.data ?? null;
  const latestRun = workflowRuns[0] ?? null;
  const strategyVersions = workflowRuns.filter((run) => run.workflow_type === "strategy").length;
  const planVersions = workflowRuns.filter((run) => run.workflow_type === "content_plan").length;
  const draftRuns = workflowRuns.filter((run) => run.workflow_type === "draft").length;

  const overviewCards = [
    {
      label: "Active strategy",
      value: latestStrategy ? `v${latestStrategy.version_number}` : "Missing",
      detail: latestStrategy?.title ?? "Generate and approve a strategy to anchor the operating cycle.",
    },
    {
      label: "Pending reviews",
      value: String(pendingReviews.length),
      detail: pendingReviews.length
        ? "Drafts are waiting for editorial decisions."
        : "The review queue is clear right now.",
    },
    {
      label: "Publish-ready",
      value: String(publishReadyQueue.length),
      detail: publishReadyQueue.length
        ? "Approved drafts are staged for scheduling and mock publishing."
        : "Nothing is staged for publishing yet.",
    },
    {
      label: "Timeline events",
      value: String(activitySummaryQuery.data?.total_events ?? 0),
      detail:
        activitySummaryQuery.data?.latest_summary ??
        "Operational events will appear here as the workflow progresses.",
    },
  ];

  const progression = [
    {
      title: "Strategy",
      value: latestStrategy ? latestStrategy.status.replace(/_/g, " ") : "not started",
      detail: latestStrategy
        ? `Version ${latestStrategy.version_number} is the active operating brief.`
        : "Brand inputs are ready once the profile is complete.",
      to: `/workspaces/${workspaceId}/strategy`,
    },
    {
      title: "Planning",
      value: latestPlan ? latestPlan.status.replace(/_/g, " ") : "not started",
      detail: latestPlan
        ? `${latestPlan.planned_posts.length} posts built from the active strategy.`
        : "Generate a plan to turn strategy into a concrete schedule.",
      to: `/workspaces/${workspaceId}/planning`,
    },
    {
      title: "Review",
      value: pendingReviews.length ? `${pendingReviews.length} pending` : "clear",
      detail: publishReadyQueue.length
        ? `${publishReadyQueue.length} items are ready to schedule or publish.`
        : "Approval and publishing prep live in one lightweight queue.",
      to: `/workspaces/${workspaceId}/review`,
    },
  ];

  return (
    <div className="mx-auto flex min-h-full w-full max-w-7xl flex-col px-5 py-10 lg:px-8">
      <SectionHeading
        eyebrow="Operational dashboard"
        title={workspaceQuery.data?.name ?? "Build the operating view"}
        description="The command center now behaves like a real operating surface: activity is traceable, workflow progression is visible, and approvals move toward publish-ready state without fake orchestration."
      />

      <div className="mt-8 animate-fade-up rounded-[2rem] border border-white/8 bg-white/[0.03] p-6 shadow-shell">
        <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
          <div>
            <div className="mx-auto mb-8 flex h-24 w-24 animate-float items-center justify-center rounded-full border border-white/8 bg-white/[0.03] shadow-[0_0_0_1px_rgba(255,255,255,0.03)]">
              <div className="flex gap-1.5">
                <span className="h-10 w-3 rounded-full bg-white" />
                <span className="mt-[-10px] h-12 w-3 rounded-full bg-white" />
                <span className="mt-[-18px] h-16 w-3 rounded-full bg-white" />
                <span className="mt-[-10px] h-12 w-3 rounded-full bg-white" />
              </div>
            </div>
            <h2 className="max-w-4xl text-4xl font-black leading-tight tracking-tight text-white md:text-6xl">
              Command center for operational continuity
            </h2>
            <p className="mt-5 max-w-3xl text-sm leading-7 text-white/60 md:text-lg">
              Strategy, planning, review, and publishing prep now feel connected. Each step leaves
              a persisted artifact, a visible trail, and a clear next action.
            </p>
            <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {overviewCards.map((card) => (
                <div
                  key={card.label}
                  className="rounded-3xl border border-white/8 bg-white/[0.04] p-5 backdrop-blur"
                >
                  <p className="text-[11px] font-bold uppercase tracking-[0.35em] text-white/35">
                    {card.label}
                  </p>
                  <p className="mt-3 text-lg font-semibold text-white">{card.value}</p>
                  <p className="mt-2 text-sm leading-6 text-white/60">{card.detail}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-4">
            <div className="rounded-3xl border border-white/8 bg-black/55 p-5 backdrop-blur">
              <p className="text-[10px] font-semibold uppercase tracking-[0.35em] text-white/35">
                System posture
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <StatusPill
                  label={`Workflow ${latestRun?.status ?? "idle"}`}
                  tone={workflowTone(latestRun?.status ?? "idle")}
                />
                <StatusPill
                  label={brandProfileQuery.data ? "Brand profile ready" : "Brand profile missing"}
                  tone={brandProfileQuery.data ? "success" : "warning"}
                />
                <StatusPill
                  label={`Last event ${formatTimestamp(activitySummaryQuery.data?.latest_event_at)}`}
                  tone="neutral"
                />
              </div>
              <div className="mt-5 space-y-3">
                {progression.map((item) => (
                  <Link
                    key={item.to}
                    to={item.to}
                    className="flex items-center justify-between rounded-3xl border border-white/8 bg-white/[0.04] px-5 py-4 transition hover:bg-white/8"
                  >
                    <div>
                      <p className="text-sm font-semibold text-white">{item.title}</p>
                      <p className="mt-1 text-xs leading-5 text-white/55">{item.detail}</p>
                    </div>
                    <StatusPill label={item.value} tone="neutral" />
                  </Link>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-white/8 bg-white/[0.04] p-5">
              <p className="text-[10px] font-semibold uppercase tracking-[0.35em] text-white/35">
                Run history
              </p>
              <div className="mt-4 grid gap-3 md:grid-cols-3 xl:grid-cols-1">
                <div className="rounded-3xl border border-white/10 bg-black/35 p-4">
                  <p className="text-xs uppercase tracking-[0.3em] text-white/35">Strategy runs</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{strategyVersions}</p>
                </div>
                <div className="rounded-3xl border border-white/10 bg-black/35 p-4">
                  <p className="text-xs uppercase tracking-[0.3em] text-white/35">Plan runs</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{planVersions}</p>
                </div>
                <div className="rounded-3xl border border-white/10 bg-black/35 p-4">
                  <p className="text-xs uppercase tracking-[0.3em] text-white/35">Draft runs</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{draftRuns}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel eyebrow="Recent activity" title="Operational timeline">
          <div className="mt-5 space-y-3">
            {activityEvents.slice(0, 6).map((event) => (
              <div key={event.id} className="rounded-3xl border border-line bg-white/5 p-5">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-white">{event.summary}</p>
                  <StatusPill label={event.event_type.replace(/_/g, " ")} tone="neutral" />
                </div>
                <p className="mt-2 text-xs uppercase tracking-[0.28em] text-white/35">
                  {event.actor_label ?? "System"} | {formatTimestamp(event.created_at)}
                </p>
              </div>
            ))}
            {activityEvents.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-line p-5 text-sm text-white/55">
                Activity will begin appearing here as soon as the first workflow runs.
              </div>
            ) : null}
          </div>
        </Panel>

        <Panel eyebrow="Operational queues" title="What needs attention">
          <div className="mt-5 space-y-4">
            <div className="rounded-3xl border border-line bg-white/5 p-5">
              <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Pending review</p>
              <p className="mt-3 text-3xl font-semibold text-white">{pendingReviews.length}</p>
              <p className="mt-2 text-sm text-white/55">
                Drafts waiting on approvals, edits, or review comments.
              </p>
            </div>
            <div className="rounded-3xl border border-line bg-white/5 p-5">
              <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Publish-ready queue</p>
              <p className="mt-3 text-3xl font-semibold text-white">{publishReadyQueue.length}</p>
              <p className="mt-2 text-sm text-white/55">
                Approved drafts with scheduling and mock publishing available.
              </p>
            </div>
            <div className="rounded-3xl border border-line bg-white/5 p-5">
              <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Active plan</p>
              <p className="mt-3 text-lg font-semibold text-white">
                {latestPlan?.title ?? "No active plan yet"}
              </p>
              <p className="mt-2 text-sm text-white/55">
                {latestPlan
                  ? `${latestPlan.planned_posts.length} planned posts are attached to the active cycle.`
                  : "Planning begins once a strategy is approved and a cycle is generated."}
              </p>
            </div>
          </div>
        </Panel>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Panel eyebrow="Analytics" title="Performance placeholders with founder context">
          <div className="mt-5 space-y-4">
            {[
              ["Audience growth", "+12.4%", "vs previous cycle"],
              ["Avg engagement", "4.8%", "proof-led posts are pulling harder"],
              ["Top platform", "Instagram", "creator-style reels lead the queue"],
            ].map(([label, value, detail]) => (
              <div key={label} className="rounded-3xl border border-line bg-white/5 p-5">
                <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">{label}</p>
                <p className="mt-3 text-2xl font-semibold text-white">{value}</p>
                <p className="mt-2 text-sm text-white/55">{detail}</p>
              </div>
            ))}
          </div>
        </Panel>

        <Panel eyebrow="Platform status" title="Readiness across publishing surfaces">
          <div className="mt-5 space-y-3">
            {[
              ["Instagram", "Connected", "success"],
              ["LinkedIn", "Mock queue", "neutral"],
              ["X", "Not linked", "warning"],
            ].map(([platform, state, tone]) => (
              <div key={platform} className="flex items-center justify-between rounded-3xl border border-line bg-white/5 p-4">
                <div>
                  <p className="text-sm font-semibold text-white">{platform}</p>
                  <p className="mt-1 text-xs text-white/45">Deployment-safe placeholder status</p>
                </div>
                <StatusPill label={state} tone={tone as "neutral" | "success" | "warning"} />
              </div>
            ))}
          </div>
        </Panel>

        <Panel eyebrow="Specialists" title="Agent surfaces preserved for parity">
          <div className="mt-5 space-y-3">
            {[
              "Trend intelligence",
              "Competitor tracking",
              "Audience segmentation",
              "Brand positioning",
              "Copy experimentation",
            ].map((label) => (
              <div key={label} className="rounded-3xl border border-line bg-white/5 px-4 py-4 text-sm text-white/75">
                {label}
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
