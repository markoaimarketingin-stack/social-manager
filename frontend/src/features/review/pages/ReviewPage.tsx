import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import { Panel } from "../../../components/ui/Panel";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { StatusPill } from "../../../components/ui/StatusPill";
import { apiGet, apiPost, apiPut } from "../../../lib/api/client";
import type { PostDraft } from "../../../lib/api/types/domain";
import type {
  MarkDraftPublishReadyRequest,
  PublishDraftRequest,
  UpdateDraftRequest,
} from "../../../lib/api/types/requests";
import { queryKeys } from "../../../lib/query/keys";
import { useWorkspaceContext } from "../../workspace/hooks/useWorkspaceContext";

const reviewTone = (status: string) =>
  status === "approved" || status === "publish_ready" || status === "published"
    ? "success"
    : status === "changes_requested" || status === "rejected"
      ? "warning"
      : "neutral";

const toDatetimeLocal = (value: string | null | undefined) => {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  const tzOffset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - tzOffset).toISOString().slice(0, 16);
};

export function ReviewPage() {
  const queryClient = useQueryClient();
  const {
    workspaceId,
    reviewQueueQuery,
    publishingQueueQuery,
    latestContentPlanQuery,
    workflowRunsQuery,
    activityQuery,
  } = useWorkspaceContext();
  const draftsQuery = useQuery({
    queryKey: queryKeys.drafts(workspaceId),
    queryFn: () => apiGet<PostDraft[]>(`/api/v1/workspaces/${workspaceId}/drafts`),
    enabled: workspaceId.length > 0,
  });
  const drafts = draftsQuery.data ?? [];
  const [selectedDraftId, setSelectedDraftId] = useState("");
  const [draftForm, setDraftForm] = useState<UpdateDraftRequest | null>(null);
  const latestDraftRun = workflowRunsQuery.data?.find((run) => run.workflow_type === "draft") ?? null;
  const publishReadyQueue = publishingQueueQuery.data ?? [];
  const selectedDraft = useMemo(
    () => drafts.find((draft) => draft.id === selectedDraftId) ?? drafts[0] ?? null,
    [drafts, selectedDraftId],
  );

  useEffect(() => {
    if (drafts.length > 0 && !selectedDraftId) {
      setSelectedDraftId(drafts[0].id);
    }
  }, [drafts, selectedDraftId]);

  useEffect(() => {
    if (!selectedDraft) {
      setDraftForm(null);
      return;
    }
    setDraftForm({
      title: selectedDraft.title,
      caption: selectedDraft.caption,
      creative_brief: selectedDraft.creative_brief,
      call_to_action: selectedDraft.call_to_action,
      hashtags: selectedDraft.hashtags,
      review_status: selectedDraft.review_status,
      reviewer_notes: selectedDraft.reviewer_notes,
      scheduled_publish_at: selectedDraft.scheduled_publish_at,
    });
  }, [selectedDraft]);

  const invalidateQueues = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.drafts(workspaceId) }),
      queryClient.invalidateQueries({ queryKey: queryKeys.reviewQueue(workspaceId) }),
      queryClient.invalidateQueries({ queryKey: queryKeys.publishingQueue(workspaceId) }),
      queryClient.invalidateQueries({ queryKey: queryKeys.latestContentPlan(workspaceId) }),
      queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
      queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
    ]);
  };

  const updateDraftMutation = useMutation({
    mutationFn: ({ draftId, payload }: { draftId: string; payload: UpdateDraftRequest }) =>
      apiPut<PostDraft, UpdateDraftRequest>(`/api/v1/drafts/${draftId}`, payload),
    onSuccess: invalidateQueues,
  });

  const markPublishReadyMutation = useMutation({
    mutationFn: ({ draftId, payload }: { draftId: string; payload: MarkDraftPublishReadyRequest }) =>
      apiPost<PostDraft, MarkDraftPublishReadyRequest>(`/api/v1/drafts/${draftId}/publish-ready`, payload),
    onSuccess: invalidateQueues,
  });

  const publishDraftMutation = useMutation({
    mutationFn: ({ draftId, payload }: { draftId: string; payload: PublishDraftRequest }) =>
      apiPost<PostDraft, PublishDraftRequest>(`/api/v1/drafts/${draftId}/publish`, payload),
    onSuccess: invalidateQueues,
  });

  const reviewTimeline = (activityQuery.data ?? []).filter(
    (event) =>
      event.entity_type === "post_draft" ||
      event.event_type === "approval_granted" ||
      event.event_type === "publish_ready" ||
      event.event_type === "published",
  );

  return (
    <div className="mx-auto flex min-h-full w-full max-w-7xl flex-col px-5 py-10 lg:px-8">
      <SectionHeading
        eyebrow="Review queue"
        title="Move drafts through approval and publish-ready state"
        description="The review surface now behaves like a lightweight operational queue: drafts are versioned, approval state is explicit, and publishing prep is believable without provider complexity."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel eyebrow="Queue overview" title="What is waiting for action">
          <div className="mt-5 flex flex-wrap gap-2">
            <StatusPill
              label={`Draft workflow ${latestDraftRun?.status ?? "not started"}`}
              tone={reviewTone(latestDraftRun?.status ?? "pending")}
            />
            <StatusPill label={`${reviewQueueQuery.data?.length ?? 0} in review`} tone="warning" />
            <StatusPill label={`${publishReadyQueue.length} publish-ready`} tone="success" />
          </div>
          <div className="mt-5 space-y-4">
            {drafts.map((draft) => (
              <button
                key={draft.id}
                type="button"
                onClick={() => setSelectedDraftId(draft.id)}
                className={`w-full rounded-3xl border p-5 text-left transition ${
                  selectedDraft?.id === draft.id
                    ? "border-white/15 bg-white/10"
                    : "border-line bg-white/5 hover:bg-white/8"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold">{draft.title}</h3>
                  <StatusPill
                    label={draft.review_status.replace(/_/g, " ")}
                    tone={reviewTone(draft.review_status)}
                  />
                </div>
                <p className="mt-3 text-sm leading-6 text-white/60">{draft.creative_brief}</p>
                <p className="mt-2 text-xs uppercase tracking-[0.25em] text-white/35">
                  v{draft.version_number} {draft.is_current_version ? "| current version" : "| historical"}
                </p>
              </button>
            ))}
            {drafts.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-line p-6 text-sm text-white/55">
                No drafts yet. Generate a content plan first, then create drafts from it.
              </div>
            ) : null}
          </div>
        </Panel>

        <Panel eyebrow="Workflow context" title="Operational handoff">
          <div className="mt-5 space-y-4">
            <div className="rounded-3xl border border-line bg-white/5 p-5">
              <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Source plan</p>
              <p className="mt-3 text-lg font-semibold">
                {latestContentPlanQuery.data?.title ?? "No plan generated yet"}
              </p>
              <p className="mt-3 text-sm leading-7 text-white/60">
                {latestContentPlanQuery.data?.summary ??
                  "Once a plan exists, generated drafts appear here for review, approval, scheduling, and mock publishing."}
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-3xl border border-line bg-white/5 p-5">
                <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Review queue</p>
                <p className="mt-3 text-3xl font-semibold text-white">{reviewQueueQuery.data?.length ?? 0}</p>
              </div>
              <div className="rounded-3xl border border-line bg-white/5 p-5">
                <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Publish queue</p>
                <p className="mt-3 text-3xl font-semibold text-white">{publishReadyQueue.length}</p>
              </div>
            </div>
          </div>
        </Panel>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel eyebrow="Draft detail" title={selectedDraft?.title ?? "Select a draft"}>
          {selectedDraft && draftForm ? (
            <div className="mt-5 space-y-4">
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white">Title</span>
                <input
                  value={draftForm.title}
                  onChange={(event) =>
                    setDraftForm((current) => (current ? { ...current, title: event.target.value } : current))
                  }
                  className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white">Caption</span>
                <textarea
                  value={draftForm.caption}
                  onChange={(event) =>
                    setDraftForm((current) => (current ? { ...current, caption: event.target.value } : current))
                  }
                  className="min-h-44 w-full rounded-3xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white">Creative brief</span>
                <textarea
                  value={draftForm.creative_brief}
                  onChange={(event) =>
                    setDraftForm((current) =>
                      current ? { ...current, creative_brief: event.target.value } : current,
                    )
                  }
                  className="min-h-28 w-full rounded-3xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white">Call to action</span>
                <textarea
                  value={draftForm.call_to_action}
                  onChange={(event) =>
                    setDraftForm((current) =>
                      current ? { ...current, call_to_action: event.target.value } : current,
                    )
                  }
                  className="min-h-24 w-full rounded-3xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                />
              </label>
            </div>
          ) : (
            <p className="mt-5 text-sm leading-7 text-white/55">
              Pick a draft from the queue to edit copy, approve it, or move it into publishing prep.
            </p>
          )}
        </Panel>

        <Panel eyebrow="Review action" title="Approval and publishing controls">
          {selectedDraft && draftForm ? (
            <div className="mt-5 space-y-4">
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white">Review status</span>
                <select
                  value={draftForm.review_status}
                  onChange={(event) =>
                    setDraftForm((current) =>
                      current
                        ? {
                            ...current,
                            review_status: event.target.value as UpdateDraftRequest["review_status"],
                          }
                        : current,
                    )
                  }
                  className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                >
                  {[
                    "draft",
                    "in_review",
                    "approved",
                    "publish_ready",
                    "published",
                    "rejected",
                    "changes_requested",
                  ].map((option) => (
                    <option key={option} value={option}>
                      {option.replace(/_/g, " ")}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white">Reviewer notes</span>
                <textarea
                  value={draftForm.reviewer_notes ?? ""}
                  onChange={(event) =>
                    setDraftForm((current) =>
                      current ? { ...current, reviewer_notes: event.target.value } : current,
                    )
                  }
                  className="min-h-32 w-full rounded-3xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white">Hashtags</span>
                <input
                  value={draftForm.hashtags.join(", ")}
                  onChange={(event) =>
                    setDraftForm((current) =>
                      current
                        ? {
                            ...current,
                            hashtags: event.target.value
                              .split(",")
                              .map((tag) => tag.trim())
                              .filter(Boolean),
                          }
                        : current,
                    )
                  }
                  className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white">Schedule for</span>
                <input
                  type="datetime-local"
                  value={toDatetimeLocal(draftForm.scheduled_publish_at)}
                  onChange={(event) =>
                    setDraftForm((current) =>
                      current
                        ? {
                            ...current,
                            scheduled_publish_at: event.target.value
                              ? new Date(event.target.value).toISOString()
                              : null,
                          }
                        : current,
                    )
                  }
                  className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                />
              </label>
              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  disabled={updateDraftMutation.isPending}
                  onClick={() =>
                    draftForm &&
                    updateDraftMutation.mutate({
                      draftId: selectedDraft.id,
                      payload: draftForm,
                    })
                  }
                  className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
                >
                  {updateDraftMutation.isPending ? "Saving review..." : "Save draft review"}
                </button>
                <button
                  type="button"
                  disabled={markPublishReadyMutation.isPending}
                  onClick={() =>
                    markPublishReadyMutation.mutate({
                      draftId: selectedDraft.id,
                      payload: {
                        scheduled_publish_at: draftForm.scheduled_publish_at ?? null,
                      },
                    })
                  }
                  className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-5 py-3 text-sm font-semibold text-emerald-100 disabled:opacity-60"
                >
                  {markPublishReadyMutation.isPending ? "Staging..." : "Mark publish-ready"}
                </button>
                <button
                  type="button"
                  disabled={publishDraftMutation.isPending}
                  onClick={() =>
                    publishDraftMutation.mutate({
                      draftId: selectedDraft.id,
                      payload: {},
                    })
                  }
                  className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-black disabled:opacity-60"
                >
                  {publishDraftMutation.isPending ? "Publishing..." : "Mock publish now"}
                </button>
              </div>
              {selectedDraft.mock_publishing_receipt ? (
                <div className="rounded-3xl border border-white/10 bg-black/35 p-4 text-sm text-white/70">
                  Receipt ID: {String(selectedDraft.mock_publishing_receipt.receipt_id ?? "unknown")}
                </div>
              ) : null}
            </div>
          ) : (
            <p className="mt-5 text-sm leading-7 text-white/55">
              This panel becomes the lightweight approval loop once drafts exist.
            </p>
          )}
        </Panel>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel eyebrow="Publish-ready queue" title="Scheduled and staged drafts">
          <div className="mt-5 space-y-3">
            {publishReadyQueue.map((draft) => (
              <div key={draft.id} className="rounded-3xl border border-line bg-white/5 p-5">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-white">{draft.title}</p>
                  <StatusPill label={draft.review_status.replace(/_/g, " ")} tone="success" />
                </div>
                <p className="mt-2 text-sm text-white/55">
                  {draft.scheduled_publish_at
                    ? `Scheduled for ${new Date(draft.scheduled_publish_at).toLocaleString()}`
                    : "No schedule selected yet"}
                </p>
              </div>
            ))}
            {publishReadyQueue.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-line p-5 text-sm text-white/55">
                Approved drafts will appear here once they are marked publish-ready.
              </div>
            ) : null}
          </div>
        </Panel>

        <Panel eyebrow="Timeline" title="Review and publishing activity">
          <div className="mt-5 space-y-3">
            {reviewTimeline.slice(0, 6).map((event) => (
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
    </div>
  );
}
