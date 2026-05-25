import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { useWorkspaceChrome } from "../../features/workspace/components/WorkspaceChromeContext";
import { ApiError, apiGet } from "../../lib/api/client";
import type {
  BrandStrategy,
  ContentPlan,
  PostDraft,
  SystemStatus,
  WorkflowRun,
  WorkspaceActivityEvent,
  WorkspaceActivitySummary,
} from "../../lib/api/types/domain";
import { queryKeys } from "../../lib/query/keys";
import { StatusPill } from "../ui/StatusPill";

type AssistantPanelProps = {
  workspaceId: string;
};

const suggestions = [
  "Approve the active strategy before regenerating planning.",
  "Stage at least one publish-ready draft for the founder walkthrough.",
  "Use the intelligence hub to anchor trend and competitor context.",
];

const draftPreview = {
  title: "Myntra Instagram Draft",
  brand: "Myntra",
  caption:
    "Myntra mode: on.\n\nFresh fits, bold energy, and everyday style made to move with you.\nFrom standout pieces to effortless basics, keep your wardrobe ready for every plan.\n\n#Myntra #FashionForward #StyleUpgrade",
};

export function AssistantPanel({ workspaceId }: AssistantPanelProps) {
  const [tab, setTab] = useState<"chat" | "suggestions">("chat");
  const [chatInput, setChatInput] = useState("");
  const { pushToast } = useWorkspaceChrome();

  const statusQuery = useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiGet<SystemStatus>("/api/v1/system/status"),
  });
  const workflowRunsQuery = useQuery({
    queryKey: queryKeys.workflowRuns(workspaceId),
    queryFn: () => apiGet<WorkflowRun[]>(`/api/v1/workspaces/${workspaceId}/workflow-runs`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });
  const latestStrategyQuery = useQuery({
    queryKey: queryKeys.latestStrategy(workspaceId),
    queryFn: () => apiGet<BrandStrategy>(`/api/v1/workspaces/${workspaceId}/strategies/latest`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });
  const latestContentPlanQuery = useQuery({
    queryKey: queryKeys.latestContentPlan(workspaceId),
    queryFn: () => apiGet<ContentPlan>(`/api/v1/workspaces/${workspaceId}/content-plans/latest`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });
  const reviewQueueQuery = useQuery({
    queryKey: queryKeys.reviewQueue(workspaceId),
    queryFn: () => apiGet<PostDraft[]>(`/api/v1/workspaces/${workspaceId}/drafts/review-queue`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });
  const publishingQueueQuery = useQuery({
    queryKey: queryKeys.publishingQueue(workspaceId),
    queryFn: () => apiGet<PostDraft[]>(`/api/v1/workspaces/${workspaceId}/drafts/publishing-queue`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });
  const activityQuery = useQuery({
    queryKey: queryKeys.activity(workspaceId),
    queryFn: () => apiGet<WorkspaceActivityEvent[]>(`/api/v1/workspaces/${workspaceId}/activity`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });
  const activitySummaryQuery = useQuery({
    queryKey: queryKeys.activitySummary(workspaceId),
    queryFn: () => apiGet<WorkspaceActivitySummary>(`/api/v1/workspaces/${workspaceId}/activity/summary`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  const latestRun = workflowRunsQuery.data?.[0];
  const recentActivity = activityQuery.data?.slice(0, 4) ?? [];
  const reviewQueue = reviewQueueQuery.data ?? [];
  const publishingQueue = publishingQueueQuery.data ?? [];
  const strategy = latestStrategyQuery.data;
  const plan = latestContentPlanQuery.data;
  const helperLinks = useMemo(
    () => [
      {
        label: strategy ? "Review strategy version" : "Generate first strategy",
        to: `/workspaces/${workspaceId}/strategy`,
      },
      {
        label: plan ? "Refine content plan" : "Build content plan",
        to: `/workspaces/${workspaceId}/planning`,
      },
      {
        label: publishingQueue.length ? "Open publishing queue" : "Open review workspace",
        to: `/workspaces/${workspaceId}/publishing`,
      },
    ],
    [plan, publishingQueue.length, strategy, workspaceId],
  );

  return (
    <div className="assistant-panel flex h-full w-full flex-col gap-4 p-3 text-white">
      <div className="flex items-start justify-between pt-0">
        <div className="flex items-center gap-3">
          <img
            src="/favicon.svg"
            alt="Marko"
            className="h-9 w-9 rounded-md border border-white/10 bg-black/60 p-1"
          />
          <div>
            <p className="text-sm font-semibold">Assistant</p>
            <p className="text-[10px] uppercase tracking-[0.35em] text-white/40">Read-only mode</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-white/60">
          {["+", "H", "X"].map((label) => (
            <div
              key={label}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-xs"
            >
              {label}
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 rounded-full border border-white/10 bg-black px-2 py-1 text-xs">
        <button
          type="button"
          onClick={() => setTab("chat")}
          className={`flex-1 rounded-full px-3 py-2 font-semibold ${
            tab === "chat" ? "bg-white/10 text-white" : "text-white/50"
          }`}
        >
          Chatbot
        </button>
        <button
          type="button"
          onClick={() => setTab("suggestions")}
          className={`flex-1 rounded-full px-3 py-2 font-semibold ${
            tab === "suggestions" ? "bg-white/10 text-white" : "text-white/50"
          }`}
        >
          Suggestions
        </button>
      </div>

      <div className="flex-1 overflow-y-auto pr-1">
        {tab === "chat" ? (
          <div className="space-y-4">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-md border border-white/10 bg-black/60 text-white">
                  #
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">Social Supervisor</p>
                  <p className="text-[10px] text-white/50">Orchestrator</p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.3em] text-white/50">
                <span>#</span>
                <span>Workflow summary</span>
              </div>
              <p className="text-sm leading-6 text-white/75">
                {activitySummaryQuery.data?.latest_summary ??
                  "The assistant rail reflects real workflow continuity, recent activity, and operational queues."}
              </p>
            </div>

            <div className="space-y-3">
              {recentActivity.map((event) => (
                <div key={event.id} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-xs text-white/75">
                  <div className="mb-1 text-[10px] font-bold uppercase tracking-[0.3em] text-white/45">
                    {event.actor_label ?? "System"}
                  </div>
                  <div>{event.summary}</div>
                </div>
              ))}
              {!recentActivity.length ? (
                <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center text-xs text-white/60">
                  Ask a question or run a workflow to populate activity.
                </div>
              ) : null}
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-white">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.35em] text-white/40">Draft Preview</p>
                  <p className="mt-1 text-sm font-bold text-white">{draftPreview.title}</p>
                </div>
                <span className="rounded-full border border-white/15 bg-white/10 px-2 py-0.5 text-[10px] font-bold uppercase text-white">
                  {draftPreview.brand}
                </span>
              </div>
              <pre className="mt-3 whitespace-pre-wrap rounded-xl border border-white/10 bg-black/40 p-3 text-xs leading-6 text-white">
                {draftPreview.caption}
              </pre>
            </div>
            {suggestions.map((suggestion) => (
              <div key={suggestion} className="rounded-2xl border border-white/10 bg-white/5 p-3 text-xs text-white">
                <p className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/50">Suggestion</p>
                <p className="mt-2 text-sm font-semibold text-white">{suggestion}</p>
                <button
                  type="button"
                  onClick={() => pushToast(`Queued: ${suggestion}`)}
                  className="mt-3 w-full rounded-xl bg-white px-3 py-2 text-xs font-bold text-black hover:bg-white/90"
                >
                  Execute
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-3xl border border-line bg-black/40 p-5 shadow-panel">
        <p className="text-xs uppercase tracking-[0.3em] text-white/35">System signals</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <StatusPill tone="success" label={`API ${statusQuery.data?.status ?? "checking"}`} />
          <StatusPill
            tone={statusQuery.data?.database === "connected" ? "success" : "neutral"}
            label={`DB ${statusQuery.data?.database ?? "unknown"}`}
          />
          <StatusPill
            tone={latestRun?.status === "completed" ? "success" : "neutral"}
            label={`${latestRun?.workflow_type ?? "workflow"} ${latestRun?.status ?? "idle"}`}
          />
        </div>
        <div className="mt-4 grid gap-3 text-sm text-white/80">
          <div className="rounded-2xl border border-line bg-white/[0.04] p-4">
            <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Strategy</p>
            <p className="mt-2 font-semibold">{strategy?.title ?? "No strategy generated yet"}</p>
          </div>
          <div className="rounded-2xl border border-line bg-white/[0.04] p-4">
            <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Plan</p>
            <p className="mt-2 font-semibold">{plan?.title ?? "No content plan generated yet"}</p>
          </div>
          <div className="rounded-2xl border border-line bg-white/[0.04] p-4">
            <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Queues</p>
            <p className="mt-2 font-semibold">
              {reviewQueue.length} in review | {publishingQueue.length} publish-ready
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {helperLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="flex items-center justify-between rounded-2xl border border-line bg-white/[0.03] px-4 py-3 text-sm text-white/85 transition hover:bg-white/8"
          >
            <span>{link.label}</span>
            <span aria-hidden="true" className="text-white/20">
              &rsaquo;
            </span>
          </Link>
        ))}
      </div>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          if (!chatInput.trim()) {
            return;
          }
          pushToast(`Assistant noted: ${chatInput.trim()}`);
          setChatInput("");
        }}
        className="rounded-[28px] border border-white/10 bg-white/5 p-3 shadow-[0_20px_60px_rgba(0,0,0,0.45)]"
      >
        <div className="flex flex-col gap-3">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-white">
              #
            </div>
            <div className="flex-1">
              <p className="mb-1 text-xs text-white/60">Add context (#), extensions (@), commands (/)</p>
              <input
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                type="text"
                placeholder="Ask or instruct the assistant..."
                className="min-w-0 w-full bg-transparent text-xs text-white placeholder:text-white/35 focus:outline-none"
              />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-full border border-white/10 bg-black/40 px-3 py-2 text-xs text-white">
              Guided
            </div>
            <div className="flex-1 rounded-full border border-white/10 bg-black/40 px-3 py-2 text-xs text-white/70">
              marko-2.0-mini
            </div>
            <button
              type="submit"
              className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-sm font-semibold text-black transition hover:bg-white/90"
            >
              &rsaquo;
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
