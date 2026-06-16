import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Panel } from "../../../components/ui/Panel";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { StatusPill } from "../../../components/ui/StatusPill";
import { apiPost } from "../../../lib/api/client";
import type { PostDraft } from "../../../lib/api/types/domain";
import type { PublishDraftRequest } from "../../../lib/api/types/requests";
import { queryKeys } from "../../../lib/query/keys";
import { useWorkspaceContext } from "../../workspace/hooks/useWorkspaceContext";

const platformHealth = [
  { platform: "Instagram", state: "Connected", tone: "success" as const },
  { platform: "LinkedIn", state: "Queue ready", tone: "neutral" as const },
  { platform: "X", state: "Not linked", tone: "warning" as const },
];

export function PublishingPage() {
  const queryClient = useQueryClient();
  const { workspaceId, publishingQueueQuery, reviewQueueQuery, activityQuery } = useWorkspaceContext();
  const publishingQueue = publishingQueueQuery.data ?? [];
  const reviewQueue = reviewQueueQuery.data ?? [];
  const leadDraft = publishingQueue[0] ?? null;
  const recentPublishActivity = (activityQuery.data ?? [])
    .filter((item) => ["publish_ready", "published"].includes(item.event_type))
    .slice(0, 2);

  const publishMutation = useMutation({
    mutationFn: ({ draftId, payload }: { draftId: string; payload: PublishDraftRequest }) =>
      apiPost<PostDraft, PublishDraftRequest>(`/api/v1/drafts/${draftId}/publish`, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.drafts(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.publishingQueue(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.reviewQueue(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
      ]);
    },
  });

  return (
    <div className="mx-auto flex h-full w-full max-w-6xl flex-col overflow-hidden px-5 py-6 lg:px-8">
      <SectionHeading
        eyebrow="Publishing queue"
        title="Stage publish-ready work"
        description="A compact, single-screen publishing surface with queue state and platform posture."
      />

      <div className="mt-5 grid gap-4 md:grid-cols-4">
        <div className="rounded-2xl border border-white/5 bg-[#000000] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
          <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">In review</p>
          <p className="mt-2 text-3xl font-semibold text-white">{reviewQueue.length}</p>
        </div>
        <div className="rounded-2xl border border-white/5 bg-[#000000] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
          <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Publish-ready</p>
          <p className="mt-2 text-3xl font-semibold text-white">{publishingQueue.length}</p>
        </div>
        <div className="rounded-2xl border border-white/5 bg-[#000000] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
          <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Latest state</p>
          <p className="mt-2 text-sm font-semibold text-white">
            {leadDraft?.review_status.replace(/_/g, " ") ?? "Queue idle"}
          </p>
        </div>
        <div className="rounded-2xl border border-white/5 bg-[#000000] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
          <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Platforms</p>
          <p className="mt-2 text-sm font-semibold text-white">3 tracked</p>
        </div>
      </div>

      <div className="mt-5 grid min-h-0 flex-1 gap-5 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel eyebrow="Queue" title="Ready to schedule or publish" className="min-h-0 overflow-hidden">
          {leadDraft ? (
            <div className="mt-4 rounded-3xl border border-line bg-[#000000] p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-lg font-semibold text-white">{leadDraft.title}</p>
                  <p className="mt-1 text-sm text-white/55">
                    {leadDraft.scheduled_publish_at
                      ? `Scheduled for ${new Date(leadDraft.scheduled_publish_at).toLocaleString()}`
                      : "Waiting for a scheduled slot"}
                  </p>
                </div>
                <StatusPill label={leadDraft.review_status.replace(/_/g, " ")} tone="success" />
              </div>
              <p className="mt-4 rounded-2xl border border-white/10 bg-[#000000] p-4 text-sm leading-7 text-white/70">
                {leadDraft.caption}
              </p>
              <button
                type="button"
                disabled={publishMutation.isPending}
                onClick={() => publishMutation.mutate({ draftId: leadDraft.id, payload: {} })}
                className="mt-4 rounded-full bg-white px-5 py-2.5 text-xs font-bold text-black shadow-lg shadow-white/5 transition-all hover:bg-white/90 disabled:opacity-60"
              >
                {publishMutation.isPending ? "Publishing..." : "Publish now"}
              </button>
            </div>
          ) : (
            <div className="mt-4 rounded-3xl border border-dashed border-line p-6 text-sm text-white/55">
              No publish-ready drafts yet. Approve one in the review queue.
            </div>
          )}
        </Panel>

        <Panel eyebrow="Platform status" title="Publishing posture" className="min-h-0 overflow-hidden">
          <div className="mt-4 space-y-3">
            {platformHealth.map((item) => (
              <div key={item.platform} className="rounded-2xl border border-white/5 bg-[#000000] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-base font-semibold">{item.platform}</p>
                  <StatusPill label={item.state} tone={item.tone} />
                </div>
              </div>
            ))}
            {recentPublishActivity.map((event) => (
              <div key={event.id} className="rounded-2xl border border-white/5 bg-[#000000] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
                <p className="text-sm font-semibold text-white">{event.summary}</p>
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
