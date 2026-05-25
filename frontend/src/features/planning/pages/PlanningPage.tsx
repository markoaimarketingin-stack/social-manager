import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import { Panel } from "../../../components/ui/Panel";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { StatusPill } from "../../../components/ui/StatusPill";
import { apiPost, apiPut } from "../../../lib/api/client";
import type { PlannedPost, WorkflowRun } from "../../../lib/api/types/domain";
import type {
  StartContentPlanRunRequest,
  StartDraftRunRequest,
  UpdatePlannedPostRequest,
} from "../../../lib/api/types/requests";
import { queryKeys } from "../../../lib/query/keys";
import { useWorkspaceContext } from "../../workspace/hooks/useWorkspaceContext";

const statusTone = (status: string) =>
  status === "approved" || status === "completed" || status === "publish_ready"
    ? "success"
    : status === "rejected" || status === "failed"
      ? "warning"
      : "neutral";

export function PlanningPage() {
  const queryClient = useQueryClient();
  const { workspaceId, latestStrategyQuery, contentPlansQuery, workflowRunsQuery, activityQuery } =
    useWorkspaceContext();
  const plans = contentPlansQuery.data ?? [];
  const [selectedPlanId, setSelectedPlanId] = useState("");
  const [selectedPostId, setSelectedPostId] = useState("");
  const [postForm, setPostForm] = useState<UpdatePlannedPostRequest | null>(null);
  const contentPlan = useMemo(
    () => plans.find((plan) => plan.id === selectedPlanId) ?? plans[0] ?? null,
    [plans, selectedPlanId],
  );
  const selectedPost = useMemo(
    () => contentPlan?.planned_posts.find((post) => post.id === selectedPostId) ?? null,
    [contentPlan, selectedPostId],
  );
  const latestStrategy = latestStrategyQuery.data ?? null;
  const latestPlanRun = workflowRunsQuery.data?.find((run) => run.workflow_type === "content_plan") ?? null;
  const latestDraftRun = workflowRunsQuery.data?.find((run) => run.workflow_type === "draft") ?? null;
  const priorPlan = useMemo(
    () =>
      contentPlan?.parent_plan_id
        ? plans.find((plan) => plan.id === contentPlan.parent_plan_id) ?? null
        : null,
    [contentPlan, plans],
  );

  useEffect(() => {
    if (plans.length > 0 && !selectedPlanId) {
      setSelectedPlanId(plans[0].id);
    }
  }, [plans, selectedPlanId]);

  useEffect(() => {
    if (contentPlan?.planned_posts.length) {
      setSelectedPostId((current) => {
        if (current && contentPlan.planned_posts.some((post) => post.id === current)) {
          return current;
        }
        return contentPlan.planned_posts[0].id;
      });
    }
  }, [contentPlan]);

  useEffect(() => {
    if (!selectedPost) {
      setPostForm(null);
      return;
    }

    setPostForm({
      scheduled_for: selectedPost.scheduled_for,
      platform: selectedPost.platform,
      format: selectedPost.format,
      title: selectedPost.title,
      hook: selectedPost.hook,
      angle: selectedPost.angle,
      call_to_action: selectedPost.call_to_action,
      status: selectedPost.status,
      notes: selectedPost.notes,
    });
  }, [selectedPost]);

  const generatePlanMutation = useMutation({
    mutationFn: (payload: StartContentPlanRunRequest) =>
      apiPost<WorkflowRun, StartContentPlanRunRequest>(
        `/api/v1/workspaces/${workspaceId}/content-plan-runs`,
        payload,
      ),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.workflowRuns(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.latestContentPlan(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.contentPlans(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
      ]);
    },
  });

  const updatePostMutation = useMutation({
    mutationFn: ({ postId, payload }: { postId: string; payload: UpdatePlannedPostRequest }) =>
      apiPut<PlannedPost, UpdatePlannedPostRequest>(`/api/v1/planned-posts/${postId}`, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.latestContentPlan(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.contentPlans(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
      ]);
    },
  });

  const generateDraftsMutation = useMutation({
    mutationFn: (payload: StartDraftRunRequest) =>
      apiPost<WorkflowRun, StartDraftRunRequest>(`/api/v1/workspaces/${workspaceId}/draft-runs`, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.workflowRuns(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.latestContentPlan(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.contentPlans(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.drafts(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.reviewQueue(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
      ]);
    },
  });

  const planningTimeline = (activityQuery.data ?? []).filter(
    (event) =>
      event.entity_type === "content_plan" ||
      event.entity_type === "planned_post" ||
      event.event_type === "workflow_completed",
  );

  return (
    <div className="mx-auto flex min-h-full w-full max-w-7xl flex-col px-5 py-10 lg:px-8">
      <SectionHeading
        eyebrow="Planning workspace"
        title="Move from strategy into a reviewable operating cycle"
        description="Plans are now versioned artifacts with editable planned posts, visible lineage, and direct handoff into draft generation."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Panel eyebrow="Plan generation" title="Build the next planning revision">
          <div className="mt-5 flex flex-wrap gap-2">
            <StatusPill
              label={`Plan workflow ${latestPlanRun?.status ?? "not started"}`}
              tone={statusTone(latestPlanRun?.status ?? "pending")}
            />
            <StatusPill
              label={contentPlan ? `Plan v${contentPlan.version_number}` : "No plan yet"}
              tone={contentPlan ? "success" : "neutral"}
            />
            <StatusPill
              label={`Draft workflow ${latestDraftRun?.status ?? "idle"}`}
              tone={statusTone(latestDraftRun?.status ?? "pending")}
            />
          </div>
          <p className="mt-5 text-sm leading-7 text-white/55">
            {contentPlan?.summary ??
              "Generate a content plan from the active strategy. Each plan revision stays visible so the team can track how the operating cadence evolved."}
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              disabled={generatePlanMutation.isPending || !latestStrategy}
              onClick={() =>
                generatePlanMutation.mutate({
                  brand_strategy_id: latestStrategy?.id ?? null,
                  planning_horizon_label: "Next 2 weeks",
                })
              }
              className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-black disabled:opacity-60"
            >
              {generatePlanMutation.isPending
                ? "Generating plan..."
                : contentPlan
                  ? "Generate next plan revision"
                  : "Generate content plan"}
            </button>
            <button
              type="button"
              disabled={generateDraftsMutation.isPending || !contentPlan}
              onClick={() =>
                generateDraftsMutation.mutate({
                  content_plan_id: contentPlan?.id ?? null,
                })
              }
              className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
            >
              {generateDraftsMutation.isPending ? "Generating drafts..." : "Generate drafts from plan"}
            </button>
          </div>
          {!latestStrategy ? (
            <p className="mt-4 text-sm text-amber-200">
              Generate a strategy first so planning has a real source artifact.
            </p>
          ) : null}
        </Panel>

        <Panel eyebrow="Plan revisions" title="Switch between historical planning cycles">
          <div className="mt-5 space-y-3">
            {plans.map((plan) => (
              <button
                key={plan.id}
                type="button"
                onClick={() => setSelectedPlanId(plan.id)}
                className={`w-full rounded-3xl border p-5 text-left transition ${
                  contentPlan?.id === plan.id
                    ? "border-white/15 bg-white/10"
                    : "border-line bg-white/5 hover:bg-white/8"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-white">
                      v{plan.version_number} {plan.title}
                    </p>
                    <p className="mt-1 text-xs uppercase tracking-[0.25em] text-white/35">
                      {plan.is_active ? "Active plan" : "Previous plan"}
                    </p>
                  </div>
                  <StatusPill label={plan.status.replace(/_/g, " ")} tone={statusTone(plan.status)} />
                </div>
                <p className="mt-3 text-sm leading-6 text-white/60">{plan.summary}</p>
              </button>
            ))}
            {plans.length === 0 ? (
              <p className="rounded-3xl border border-dashed border-line p-5 text-sm text-white/55">
                The planning revision list appears after the first plan is generated.
              </p>
            ) : null}
          </div>
        </Panel>
      </div>

      {contentPlan ? (
        <>
          <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
            <Panel eyebrow="Planning board" title={contentPlan.title}>
              <div className="mt-5 grid gap-4 md:grid-cols-2">
                {contentPlan.planned_posts.map((post) => (
                  <button
                    key={post.id}
                    type="button"
                    onClick={() => setSelectedPostId(post.id)}
                    className={`rounded-3xl border p-5 text-left transition ${
                      selectedPostId === post.id
                        ? "border-white/15 bg-white/10"
                        : "border-line bg-white/5 hover:bg-white/8"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <h3 className="text-lg font-semibold">{post.title}</h3>
                      <StatusPill label={post.status.replace(/_/g, " ")} tone={statusTone(post.status)} />
                    </div>
                    <p className="mt-3 text-sm text-white/55">
                      {new Date(post.scheduled_for).toLocaleDateString()} | {post.platform}
                    </p>
                    <p className="mt-2 text-sm font-medium text-white/80">{post.format}</p>
                    <p className="mt-3 text-sm leading-6 text-white/65">{post.hook}</p>
                  </button>
                ))}
              </div>
            </Panel>

            <Panel eyebrow="Workflow continuity" title="Why this plan exists">
              <div className="mt-5 space-y-4">
                <div className="rounded-3xl border border-line bg-white/5 p-5">
                  <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Source strategy</p>
                  <p className="mt-3 text-lg font-semibold">{latestStrategy?.title ?? "No strategy linked"}</p>
                  <p className="mt-3 text-sm leading-7 text-white/60">
                    {latestStrategy?.summary ??
                      "Planning provenance becomes visible once a strategy has been generated."}
                  </p>
                </div>
                <div className="rounded-3xl border border-line bg-white/5 p-5">
                  <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Plan lineage</p>
                  <p className="mt-3 text-sm leading-7 text-white/70">
                    {priorPlan
                      ? `This revision was generated from plan v${priorPlan.version_number}, preserving history while keeping v${contentPlan.version_number} active.`
                      : "This is the initial planning revision for the workspace."}
                  </p>
                </div>
              </div>
            </Panel>
          </div>

          <div className="mt-6 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
            <Panel eyebrow="Post editor" title={selectedPost?.title ?? "Select a planned post"}>
              {selectedPost && postForm ? (
                <div className="mt-5 space-y-4">
                  <label className="block">
                    <span className="mb-2 block text-sm font-medium text-white">Title</span>
                    <input
                      value={postForm.title}
                      onChange={(event) =>
                        setPostForm((current) => (current ? { ...current, title: event.target.value } : current))
                      }
                      className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                    />
                  </label>
                  <div className="grid gap-4 md:grid-cols-2">
                    <label className="block">
                      <span className="mb-2 block text-sm font-medium text-white">Date</span>
                      <input
                        type="date"
                        value={postForm.scheduled_for}
                        onChange={(event) =>
                          setPostForm((current) =>
                            current ? { ...current, scheduled_for: event.target.value } : current,
                          )
                        }
                        className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                      />
                    </label>
                    <label className="block">
                      <span className="mb-2 block text-sm font-medium text-white">Status</span>
                      <select
                        value={postForm.status}
                        onChange={(event) =>
                          setPostForm((current) =>
                            current
                              ? {
                                  ...current,
                                  status: event.target.value as UpdatePlannedPostRequest["status"],
                                }
                              : current,
                          )
                        }
                        className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                      >
                        {[
                          "planned",
                          "drafted",
                          "in_review",
                          "approved",
                          "publish_ready",
                          "published",
                          "rejected",
                        ].map((option) => (
                          <option key={option} value={option}>
                            {option.replace(/_/g, " ")}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                  {[
                    ["platform", "Platform"],
                    ["format", "Format"],
                    ["hook", "Hook"],
                    ["angle", "Angle"],
                    ["call_to_action", "Call to action"],
                    ["notes", "Notes"],
                  ].map(([key, label]) => (
                    <label key={key} className="block">
                      <span className="mb-2 block text-sm font-medium text-white">{label}</span>
                      <textarea
                        value={(postForm[key as keyof UpdatePlannedPostRequest] as string | null) ?? ""}
                        onChange={(event) =>
                          setPostForm((current) =>
                            current
                              ? {
                                  ...current,
                                  [key]: event.target.value,
                                }
                              : current,
                          )
                        }
                        className="min-h-24 w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                      />
                    </label>
                  ))}
                  <button
                    type="button"
                    disabled={updatePostMutation.isPending}
                    onClick={() =>
                      postForm &&
                      updatePostMutation.mutate({
                        postId: selectedPost.id,
                        payload: postForm,
                      })
                    }
                    className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
                  >
                    {updatePostMutation.isPending ? "Saving..." : "Save planned post"}
                  </button>
                </div>
              ) : (
                <p className="mt-5 text-sm leading-7 text-white/55">
                  Choose a planned post from the board to refine the scheduling brief and workflow status.
                </p>
              )}
            </Panel>

            <Panel eyebrow="Timeline" title="Planning activity">
              <div className="mt-5 space-y-3">
                {planningTimeline.slice(0, 6).map((event) => (
                  <div key={event.id} className="rounded-3xl border border-line bg-white/5 p-5">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-white">{event.summary}</p>
                      <StatusPill label={event.event_type.replace(/_/g, " ")} tone="neutral" />
                    </div>
                    <p className="mt-2 text-xs uppercase tracking-[0.25em] text-white/35">
                      {new Date(event.created_at).toLocaleString()}
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
