import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

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

export function ReviewPage() {
  const queryClient = useQueryClient();
  const {
    workspaceId,
    reviewQueueQuery,
    publishingQueueQuery,
    latestContentPlanQuery,
    workflowRunsQuery,
  } = useWorkspaceContext();

  const draftsQuery = useQuery({
    queryKey: queryKeys.drafts(workspaceId),
    queryFn: () => apiGet<PostDraft[]>(`/api/v1/workspaces/${workspaceId}/drafts`),
    enabled: workspaceId.length > 0,
  });

  const drafts = draftsQuery.data ?? [];
  const latestDraftRun = workflowRunsQuery.data?.find((run) => run.workflow_type === "draft") ?? null;
  const [selectedDraftId, setSelectedDraftId] = useState("");
  const [reviewStatus, setReviewStatus] = useState<UpdateDraftRequest["review_status"]>("in_review");

  useEffect(() => {
    if (!selectedDraftId && drafts.length) {
      setSelectedDraftId(drafts[0].id);
    }
  }, [drafts, selectedDraftId]);

  const selectedDraft = useMemo(
    () => drafts.find((draft) => draft.id === selectedDraftId) ?? drafts[0] ?? null,
    [drafts, selectedDraftId],
  );

  useEffect(() => {
    if (selectedDraft) {
      setReviewStatus(selectedDraft.review_status);
    }
  }, [selectedDraft]);

  const updateDraftMutation = useMutation({
    mutationFn: ({ draftId, payload }: { draftId: string; payload: UpdateDraftRequest }) =>
      apiPut<PostDraft, UpdateDraftRequest>(`/api/v1/drafts/${draftId}`, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.drafts(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.reviewQueue(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.publishingQueue(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
      ]);
    },
  });

  const markPublishReadyMutation = useMutation({
    mutationFn: ({ draftId, payload }: { draftId: string; payload: MarkDraftPublishReadyRequest }) =>
      apiPost<PostDraft, MarkDraftPublishReadyRequest>(`/api/v1/drafts/${draftId}/publish-ready`, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.drafts(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.reviewQueue(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.publishingQueue(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
      ]);
    },
  });

  const publishDraftMutation = useMutation({
    mutationFn: ({ draftId, payload }: { draftId: string; payload: PublishDraftRequest }) =>
      apiPost<PostDraft, PublishDraftRequest>(`/api/v1/drafts/${draftId}/publish`, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.drafts(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.reviewQueue(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.publishingQueue(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
      ]);
    },
  });

  const compactDrafts = drafts.slice(0, 3);

  return (
    <div className="mx-auto flex h-full w-full max-w-6xl flex-col px-5 py-8 lg:px-8">
      <SectionHeading
        eyebrow="Review queue"
        title="Move drafts through approval"
        description="A compact approval surface that keeps focus on one selected draft and clean state transitions."
      />

      <div className="mt-6 grid min-h-0 flex-1 gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel eyebrow="Queue overview" title="What is waiting for action" className="min-h-0 overflow-hidden">
          <div className="mt-4 flex flex-wrap gap-2">
            <StatusPill
              label={`Draft workflow ${latestDraftRun?.status ?? "not started"}`}
              tone={reviewTone(latestDraftRun?.status ?? "pending")}
            />
            <StatusPill label={`${reviewQueueQuery.data?.length ?? 0} in review`} tone="warning" />
            <StatusPill label={`${publishingQueueQuery.data?.length ?? 0} publish-ready`} tone="success" />
          </div>

          <div className="mt-4 space-y-3">
            {compactDrafts.map((draft) => (
              <button
                key={draft.id}
                type="button"
                onClick={() => setSelectedDraftId(draft.id)}
                className={`w-full rounded-2xl border px-4 py-4 text-left transition ${
                  selectedDraft?.id === draft.id
                    ? "border-white/15 bg-white/10"
                    : "border-line bg-white/5 hover:bg-white/8"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-base font-semibold">{draft.title}</h3>
                  <StatusPill label={draft.review_status.replace(/_/g, " ")} tone={reviewTone(draft.review_status)} />
                </div>
                <p className="mt-2 line-clamp-2 text-sm leading-6 text-white/60">{draft.creative_brief}</p>
              </button>
            ))}
            {!compactDrafts.length ? (
              <div className="rounded-2xl border border-dashed border-line p-5 text-sm text-white/55">
                No drafts yet. Generate a content plan first.
              </div>
            ) : null}
          </div>
        </Panel>

        <Panel eyebrow="Selected draft" title={selectedDraft?.title ?? "Select a draft"} className="min-h-0 overflow-hidden">
          {selectedDraft ? (
            <div className="mt-4 space-y-4">
              <div className="rounded-2xl border border-line bg-white/5 p-4">
                <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Source plan</p>
                <p className="mt-2 text-base font-semibold text-white">
                  {latestContentPlanQuery.data?.title ?? "No plan generated yet"}
                </p>
                <p className="mt-2 line-clamp-3 text-sm leading-6 text-white/60">{selectedDraft.caption}</p>
              </div>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white">Review status</span>
                <select
                  value={reviewStatus}
                  onChange={(event) =>
                    setReviewStatus(event.target.value as UpdateDraftRequest["review_status"])
                  }
                  className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
                >
                  {["draft", "in_review", "approved", "publish_ready", "published", "rejected", "changes_requested"].map(
                    (option) => (
                      <option key={option} value={option}>
                        {option.replace(/_/g, " ")}
                      </option>
                    ),
                  )}
                </select>
              </label>

              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  disabled={updateDraftMutation.isPending}
                  onClick={() =>
                    updateDraftMutation.mutate({
                      draftId: selectedDraft.id,
                      payload: {
                        title: selectedDraft.title,
                        caption: selectedDraft.caption,
                        creative_brief: selectedDraft.creative_brief,
                        call_to_action: selectedDraft.call_to_action,
                        hashtags: selectedDraft.hashtags,
                        reviewer_notes: selectedDraft.reviewer_notes,
                        scheduled_publish_at: selectedDraft.scheduled_publish_at,
                        review_status: reviewStatus,
                      },
                    })
                  }
                  className="rounded-full border border-white/10 bg-white/5 px-5 py-2.5 text-xs font-semibold text-white transition-all hover:bg-white/10 hover:border-white/20 hover:-translate-y-0.5 active:translate-y-0 active:scale-95 disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:scale-100 disabled:pointer-events-none"
                >
                  {updateDraftMutation.isPending ? "Saving..." : "Save review"}
                </button>
                <button
                  type="button"
                  disabled={markPublishReadyMutation.isPending}
                  onClick={() =>
                    markPublishReadyMutation.mutate({
                      draftId: selectedDraft.id,
                      payload: { scheduled_publish_at: selectedDraft.scheduled_publish_at ?? null },
                    })
                  }
                  className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-5 py-2.5 text-xs font-semibold text-emerald-100 transition-all hover:bg-emerald-300/20 hover:-translate-y-0.5 active:translate-y-0 active:scale-95 disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:scale-100 disabled:pointer-events-none"
                >
                  {markPublishReadyMutation.isPending ? "Staging..." : "Mark publish-ready"}
                </button>
                <button
                  type="button"
                  disabled={publishDraftMutation.isPending}
                  onClick={() => publishDraftMutation.mutate({ draftId: selectedDraft.id, payload: {} })}
                  className="rounded-full bg-white px-5 py-2.5 text-xs font-bold text-black shadow-lg shadow-white/5 transition-all hover:bg-white/90 hover:-translate-y-0.5 active:translate-y-0 active:scale-95 disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:scale-100 disabled:pointer-events-none"
                >
                  {publishDraftMutation.isPending ? "Publishing..." : "Mock publish"}
                </button>
              </div>
            </div>
          ) : (
            <p className="mt-4 text-sm leading-7 text-white/55">Select a draft from the queue.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
