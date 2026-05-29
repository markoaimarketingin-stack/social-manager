import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import { Panel } from "../../../components/ui/Panel";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { StatusPill } from "../../../components/ui/StatusPill";
import { apiPatch, apiPost } from "../../../lib/api/client";
import type { BrandStrategy, WorkflowRun } from "../../../lib/api/types/domain";
import type { ReviewStrategyRequest, StartStrategyRunRequest } from "../../../lib/api/types/requests";
import { queryKeys } from "../../../lib/query/keys";
import { useWorkspaceContext } from "../../workspace/hooks/useWorkspaceContext";

const reviewOptions: Array<ReviewStrategyRequest["status"]> = [
  "draft",
  "in_review",
  "approved",
  "needs_revision",
  "rejected",
];

const statusTone = (status: string) =>
  status === "approved" || status === "completed"
    ? "success"
    : status === "needs_revision" || status === "rejected" || status === "failed"
      ? "warning"
      : "neutral";

const formatTimestamp = (value: string | null | undefined) =>
  value
    ? new Date(value).toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      })
    : "Not reviewed yet";

export function StrategyPage() {
  const queryClient = useQueryClient();
  const { workspaceId, brandProfileQuery, strategiesQuery, workflowRunsQuery, activityQuery } =
    useWorkspaceContext();
  const strategies = strategiesQuery.data ?? [];
  const latestRun = workflowRunsQuery.data?.find((run) => run.workflow_type === "strategy") ?? null;
  const [selectedStrategyId, setSelectedStrategyId] = useState("");
  const selectedStrategy = useMemo(
    () => strategies.find((strategy) => strategy.id === selectedStrategyId) ?? strategies[0] ?? null,
    [selectedStrategyId, strategies],
  );
  const previousStrategy = useMemo(
    () =>
      selectedStrategy?.parent_strategy_id
        ? strategies.find((strategy) => strategy.id === selectedStrategy.parent_strategy_id) ?? null
        : null,
    [selectedStrategy, strategies],
  );
  const [reviewNotes, setReviewNotes] = useState("");
  const [reviewStatus, setReviewStatus] = useState<ReviewStrategyRequest["status"]>("in_review");

  useEffect(() => {
    if (strategies.length > 0 && !selectedStrategyId) {
      setSelectedStrategyId(strategies[0].id);
    }
  }, [selectedStrategyId, strategies]);

  useEffect(() => {
    setReviewNotes(selectedStrategy?.review_notes ?? "");
    setReviewStatus((selectedStrategy?.status as ReviewStrategyRequest["status"]) ?? "in_review");
  }, [selectedStrategy]);

  const runMutation = useMutation({
    mutationFn: (payload: StartStrategyRunRequest) =>
      apiPost<WorkflowRun, StartStrategyRunRequest>(
        `/api/v1/workspaces/${workspaceId}/strategy-runs`,
        payload,
      ),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.workflowRuns(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.latestStrategy(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.strategies(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
      ]);
    },
  });

  const reviewMutation = useMutation({
    mutationFn: (payload: ReviewStrategyRequest) =>
      apiPatch<BrandStrategy, ReviewStrategyRequest>(
        `/api/v1/strategies/${selectedStrategy?.id}/review`,
        payload,
      ),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.latestStrategy(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.strategies(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
      ]);
    },
  });

  const strategyTimeline = (activityQuery.data ?? []).filter(
    (event) => event.entity_type === "strategy" || event.event_type === "workflow_completed",
  );
  const missingBrandSetup = !brandProfileQuery.data;

  return (
    <div className="mx-auto flex min-h-full w-full max-w-7xl flex-col px-5 py-10 lg:px-8">
      <SectionHeading
        eyebrow="Strategy workflow"
        title="Versioned strategy with visible provenance"
        description="Each strategy run now creates a persistent revision, marks an active version, and leaves an activity trail that planning can inherit without rebuilding the old frontend supervisor logic."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel eyebrow="Workflow control" title="Generate the next strategy revision">
          <div className="mt-5 flex flex-wrap gap-2">
            <StatusPill
              label={`Workflow ${latestRun?.status ?? "not started"}`}
              tone={statusTone(latestRun?.status ?? "pending")}
            />
            <StatusPill
              label={selectedStrategy ? `Version ${selectedStrategy.version_number}` : "No strategy yet"}
              tone={selectedStrategy ? "success" : "neutral"}
            />
            <StatusPill
              label={selectedStrategy?.is_active ? "Active strategy" : "Historical revision"}
              tone={selectedStrategy?.is_active ? "success" : "neutral"}
            />
          </div>
          <p className="mt-5 text-sm leading-7 text-white/55">
            {selectedStrategy?.summary ??
              "Generate the first strategy after the brand profile is ready. Each new run will create a revision and preserve the older narrative for comparison."}
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() =>
                runMutation.mutate({
                  goal: selectedStrategy
                    ? "Revise the strategy using the latest brand and audience context"
                    : "Create the first believable strategy foundation",
                })
              }
              disabled={runMutation.isPending || missingBrandSetup}
              className="rounded-full bg-white px-5 py-3 text-sm font-bold text-black shadow-lg shadow-white/5 disabled:opacity-60 transition-all hover:bg-white/90 hover:-translate-y-0.5 active:translate-y-0 active:scale-95 disabled:hover:translate-y-0 disabled:hover:scale-100 disabled:pointer-events-none"
            >
              {runMutation.isPending
                ? "Generating strategy..."
                : selectedStrategy
                  ? "Generate next version"
                  : "Generate strategy"}
            </button>
            <div className="rounded-full border border-line px-4 py-3 text-sm text-white/65">
              {missingBrandSetup
                ? "Brand profile required first"
                : `${brandProfileQuery.data?.brand_name ?? "Brand"} is ready for strategy generation`}
            </div>
          </div>
          {runMutation.isError ? (
            <p className="mt-4 text-sm text-red-300">{runMutation.error.message}</p>
          ) : null}
        </Panel>

        <Panel eyebrow="Revision history" title="Choose an active or historical version">
          <div className="mt-5 space-y-3">
            {strategies.map((strategy) => (
              <button
                key={strategy.id}
                type="button"
                onClick={() => setSelectedStrategyId(strategy.id)}
                className={`w-full rounded-3xl border p-5 text-left transition ${
                  selectedStrategy?.id === strategy.id
                    ? "border-white/15 bg-white/10"
                    : "border-line bg-white/5 hover:bg-white/8"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-white">
                      v{strategy.version_number} {strategy.title}
                    </p>
                    <p className="mt-1 text-xs uppercase tracking-[0.25em] text-white/35">
                      {strategy.is_active ? "Active version" : "Superseded revision"}
                    </p>
                  </div>
                  <StatusPill label={strategy.status.replace(/_/g, " ")} tone={statusTone(strategy.status)} />
                </div>
                <p className="mt-3 text-sm leading-6 text-white/60">{strategy.summary}</p>
              </button>
            ))}
            {strategies.length === 0 ? (
              <p className="rounded-3xl border border-dashed border-line p-5 text-sm text-white/55">
                The version selector activates after the first strategy run.
              </p>
            ) : null}
          </div>
        </Panel>
      </div>

      {selectedStrategy ? (
        <>
          <div className="mt-6 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
            <Panel eyebrow="Review flow" title="Approve the strategy before planning">
              <div className="mt-5 space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="rounded-3xl border border-line bg-white/5 p-4">
                    <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Source workflow</p>
                    <p className="mt-3 text-sm font-medium text-white">
                      {selectedStrategy.source_workflow_run_id ? "Connected" : "Manual"}
                    </p>
                  </div>
                  <div className="rounded-3xl border border-line bg-white/5 p-4">
                    <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Reviewed at</p>
                    <p className="mt-3 text-sm font-medium text-white">
                      {formatTimestamp(selectedStrategy.reviewed_at)}
                    </p>
                  </div>
                  <div className="rounded-3xl border border-line bg-white/5 p-4">
                    <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Lineage</p>
                    <p className="mt-3 text-sm font-medium text-white">
                      {previousStrategy
                        ? `Updated from v${previousStrategy.version_number}`
                        : "Initial version"}
                    </p>
                  </div>
                </div>

                <div className="rounded-3xl border border-line bg-white/5 p-5">
                  <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Positioning statement</p>
                  <p className="mt-3 text-sm leading-7 text-white/85">
                    {selectedStrategy.positioning_statement}
                  </p>
                </div>

                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-white">Review status</span>
                  <select
                    value={reviewStatus}
                    onChange={(event) =>
                      setReviewStatus(event.target.value as ReviewStrategyRequest["status"])
                    }
                    className="w-full rounded-lg bg-[#0d1117] border border-[#30363d] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none cursor-pointer"
                  >
                    {reviewOptions.map((option) => (
                      <option key={option} value={option}>
                        {option.replace(/_/g, " ")}
                      </option>
                    ))}
                  </select>
                </label>
 
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-white">Review notes</span>
                  <textarea
                    value={reviewNotes}
                    onChange={(event) => setReviewNotes(event.target.value)}
                    className="min-h-24 w-full rounded-lg bg-[#0d1117] border border-[#30363d] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none resize-none"
                  />
                </label>

                <button
                  type="button"
                  onClick={() =>
                    reviewMutation.mutate({
                      status: reviewStatus,
                      review_notes: reviewNotes.trim() ? reviewNotes.trim() : null,
                    })
                  }
                  disabled={reviewMutation.isPending}
                  className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60 transition-all hover:bg-white/10 hover:border-white/20 hover:-translate-y-0.5 active:translate-y-0 active:scale-95"
                >
                  {reviewMutation.isPending ? "Saving review..." : "Save review decision"}
                </button>
              </div>
            </Panel>

            <Panel eyebrow="Revision compare" title="What changed from the previous version">
              {previousStrategy ? (
                <div className="mt-5 space-y-4">
                  <div className="rounded-3xl border border-line bg-white/5 p-5">
                    <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Previous summary</p>
                    <p className="mt-3 text-sm leading-7 text-white/60">{previousStrategy.summary}</p>
                  </div>
                  <div className="rounded-3xl border border-white/8 bg-black/35 p-5">
                    <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Current summary</p>
                    <p className="mt-3 text-sm leading-7 text-white/80">{selectedStrategy.summary}</p>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="rounded-3xl border border-line bg-white/5 p-5">
                      <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Previous audience focus</p>
                      <p className="mt-3 text-sm leading-7 text-white/60">{previousStrategy.audience_focus}</p>
                    </div>
                    <div className="rounded-3xl border border-line bg-white/5 p-5">
                      <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Current audience focus</p>
                      <p className="mt-3 text-sm leading-7 text-white/80">{selectedStrategy.audience_focus}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="mt-5 text-sm leading-7 text-white/55">
                  The first generated strategy becomes the baseline. Later versions will show what
                  changed in language and focus without adding complicated diff tooling.
                </p>
              )}
            </Panel>
          </div>

          <div className="mt-6 grid gap-6 xl:grid-cols-2">
            <Panel eyebrow="Platform plans" title="Channel operating plans">
              <div className="mt-5 space-y-4">
                {selectedStrategy.platform_plans.map((plan) => (
                  <div key={plan.id} className="rounded-3xl border border-line bg-white/5 p-5">
                    <div className="flex items-center justify-between gap-3">
                      <h3 className="text-lg font-semibold">{plan.platform_name}</h3>
                      <StatusPill label="Planning input" tone="success" />
                    </div>
                    <p className="mt-3 text-sm leading-7 text-white/75">{plan.objective}</p>
                    <div className="mt-4 grid gap-3 md:grid-cols-3">
                      <div>
                        <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Cadence</p>
                        <p className="mt-2 text-sm text-white/70">{plan.cadence_summary}</p>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Mix</p>
                        <p className="mt-2 text-sm text-white/70">{plan.content_mix}</p>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Signal</p>
                        <p className="mt-2 text-sm text-white/70">{plan.success_signal}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel eyebrow="Timeline" title="Strategy activity">
              <div className="mt-5 space-y-3">
                {strategyTimeline.slice(0, 6).map((event) => (
                  <div key={event.id} className="rounded-3xl border border-line bg-white/5 p-5">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-white">{event.summary}</p>
                      <StatusPill label={event.event_type.replace(/_/g, " ")} tone="neutral" />
                    </div>
                    <p className="mt-2 text-xs uppercase tracking-[0.25em] text-white/35">
                      {formatTimestamp(event.created_at)}
                    </p>
                  </div>
                ))}
              </div>
            </Panel>
          </div>
        </>
      ) : null}
    </div>
  );
}
