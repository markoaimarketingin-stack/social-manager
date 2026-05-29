import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

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
  
  // Normal Review States
  const [selectedDraftId, setSelectedDraftId] = useState("");
  const [reviewStatus, setReviewStatus] = useState<UpdateDraftRequest["review_status"]>("in_review");

  // A/B Testing Specialist States
  const isABTester = window.location.pathname.includes("ab-copy-tester");
  const [abPrompt, setAbPrompt] = useState("");
  const [isGeneratingAB, setIsGeneratingAB] = useState(false);
  const [variantA, setVariantA] = useState("");
  const [variantB, setVariantB] = useState("");
  const [abSelected, setAbSelected] = useState<"A" | "B" | null>(null);
  const [abFeedback, setAbFeedback] = useState<string | null>(null);

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

  const handleGenerateAB = async () => {
    if (!abPrompt.trim()) return;
    setIsGeneratingAB(true);
    setAbSelected(null);
    setAbFeedback(null);
    
    await new Promise((r) => setTimeout(r, 1500));
    
    setVariantA(
      `📊 Value-Focused Variant (Variant A):\n\n` +
      `Remote work is here to stay, but remote output requires focus. Here are 3 quick remote work setup guidelines that boost engineering speed:\n\n` +
      `1️⃣ Keep primary screens at eye level to eliminate neck strain.\n` +
      `2️⃣ Dedicate a physical space ONLY to working to split professional/personal habits.\n` +
      `3️⃣ Standardize visual boundaries in background scenes for calls.\n\n` +
      `How do you optimize your home station? Let us know below. #remotework #developer #productivity`
    );
    
    setVariantB(
      `🔥 Curiosity-Focused Variant (Variant B):\n\n` +
      `リモートワーク (Remote work) setups usually suck. 🤷‍♂️ Here is the ugly truth:\n\n` +
      `You don't need a $2,000 ergonomic chair. You just need visual boundaries. Dedicating a single physical corner exclusively to work tricks your brain into intense focus modes instantly.\n\n` +
      `What is the one home setup accessory you can't work without? 👇 #productivity #careerhacks #officestation`
    );
    
    setIsGeneratingAB(false);
  };

  const handleStageVariant = async (variant: "A" | "B") => {
    setAbSelected(variant);
    
    // Simulate staging
    await new Promise((r) => setTimeout(r, 800));
    setAbFeedback(`✓ Variant ${variant} successfully approved and staged to the publishing queue!`);
    
    // If we have queryClient, trigger refresh
    queryClient.invalidateQueries();
  };

  const compactDrafts = drafts.slice(0, 3);

  // ==========================================
  // RENDER PATH A: A/B TESTING SPECIALIST PAGE
  // ==========================================
  if (isABTester) {
    return (
      <div className="mx-auto flex h-full w-full max-w-6xl flex-col px-6 py-8 bg-[#0d1117] text-white">
        <SectionHeading
          eyebrow="Specialist Agent"
          title="A/B Variant Copy Tester"
          description="Test contrasting hooks, benefit structures, and engagement cues side-by-side to optimize for viral reach."
        />

        <div className="mt-8 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          {/* Form input */}
          <section
            className="rounded-2xl border p-6 text-white space-y-4"
            style={{ background: "#161b22", borderColor: "#30363d" }}
          >
            <h2 className="text-sm font-bold uppercase tracking-wider text-white/80">Generate A/B Copy Variants</h2>
            <p className="text-[11px] text-white/40">Provide a topic or draft message, and the AI copywriter will generate two contrasting variant pitches.</p>
            
            <div className="space-y-4 pt-2">
              <label className="block">
                <span className="mb-1.5 block text-xs font-bold text-white/60 uppercase tracking-wider">Base Brief / Topic</span>
                <textarea
                  value={abPrompt}
                  onChange={(e) => setAbPrompt(e.target.value)}
                  placeholder="E.g., Share a productive tip about engineering remote work stations."
                  className="w-full min-h-24 rounded-lg bg-[#0d1117] border border-[#30363d] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none resize-none"
                />
              </label>

              <button
                onClick={handleGenerateAB}
                disabled={isGeneratingAB || !abPrompt.trim()}
                className="px-4 py-2.5 rounded-lg text-xs font-bold transition-all shadow-[0_4px_12px_rgba(31,111,235,0.2)] disabled:opacity-50"
                style={{
                  background: "#1f6feb",
                  color: "#fff",
                  border: "1px solid rgba(255,255,255,0.1)",
                }}
              >
                {isGeneratingAB ? "Generating Variants..." : "⚡ Generate A/B Variants"}
              </button>
            </div>
          </section>

          {/* Guidelines */}
          <div
            className="rounded-2xl border p-5 text-white space-y-4"
            style={{ background: "#161b22", borderColor: "#30363d" }}
          >
            <h3 className="text-xs font-bold uppercase tracking-wider text-white/60">A/B Strategy Guidelines</h3>
            <div className="space-y-4 text-xs leading-relaxed text-white/60">
              <div className="p-3.5 rounded-lg bg-[#0d1117]/60 border border-[#21262d] space-y-1">
                <p className="font-bold text-white">Variant A (Value-First)</p>
                <p className="text-[11px] text-white/50">Focuses on educational lists, structured frameworks, and professional CTAs.</p>
              </div>
              <div className="p-3.5 rounded-lg bg-[#0d1117]/60 border border-[#21262d] space-y-1">
                <p className="font-bold text-white">Variant B (Curiosity-First)</p>
                <p className="text-[11px] text-white/50">Utilizes punchy controversy hooks, conversational formatting, and conversational questions.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Display Side-by-Side Variants */}
        {(variantA || variantB) && (
          <div className="mt-6 grid gap-6 md:grid-cols-2 animate-fadeIn">
            {/* Variant A */}
            <div
              className="rounded-2xl border p-5 text-white flex flex-col justify-between"
              style={{
                background: "#161b22",
                borderColor: abSelected === "A" ? "#238636" : "#30363d",
                boxShadow: abSelected === "A" ? "0 0 15px rgba(56,139,253,0.1)" : "none",
              }}
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-[#21262d] pb-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Variant A (Value)</h4>
                  <span className="text-[10px] text-white/40 font-mono">Readability: Easy</span>
                </div>
                <textarea
                  value={variantA}
                  onChange={(e) => setVariantA(e.target.value)}
                  className="w-full min-h-48 rounded-lg bg-[#0d1117] border border-[#21262d] px-3.5 py-2.5 text-xs text-white focus:outline-none resize-none leading-relaxed"
                />
              </div>
              <button
                onClick={() => handleStageVariant("A")}
                className="mt-4 w-full py-2 rounded-lg text-xs font-bold transition-all border border-[#30363d] hover:bg-white/5"
                style={{
                  background: abSelected === "A" ? "#238636" : "transparent",
                  color: "#fff",
                }}
              >
                {abSelected === "A" ? "✓ Staged Variant A" : "Approve & Stage Variant A"}
              </button>
            </div>

            {/* Variant B */}
            <div
              className="rounded-2xl border p-5 text-white flex flex-col justify-between"
              style={{
                background: "#161b22",
                borderColor: abSelected === "B" ? "#238636" : "#30363d",
                boxShadow: abSelected === "B" ? "0 0 15px rgba(56,139,253,0.1)" : "none",
              }}
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-[#21262d] pb-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Variant B (Punchy)</h4>
                  <span className="text-[10px] text-white/40 font-mono">Readability: High Engagement</span>
                </div>
                <textarea
                  value={variantB}
                  onChange={(e) => setVariantB(e.target.value)}
                  className="w-full min-h-48 rounded-lg bg-[#0d1117] border border-[#21262d] px-3.5 py-2.5 text-xs text-white focus:outline-none resize-none leading-relaxed"
                />
              </div>
              <button
                onClick={() => handleStageVariant("B")}
                className="mt-4 w-full py-2 rounded-lg text-xs font-bold transition-all border border-[#30363d] hover:bg-white/5"
                style={{
                  background: abSelected === "B" ? "#238636" : "transparent",
                  color: "#fff",
                }}
              >
                {abSelected === "B" ? "✓ Staged Variant B" : "Approve & Stage Variant B"}
              </button>
            </div>
          </div>
        )}

        {abFeedback && (
          <p className="text-xs text-center text-[#3fb950] font-semibold mt-4 animate-fadeIn">{abFeedback}</p>
        )}
      </div>
    );
  }

  // ==========================================
  // RENDER PATH B: ORIGINAL REVIEW QUEUE PAGE
  // ==========================================
  return (
    <div className="mx-auto flex h-full w-full max-w-6xl flex-col px-6 py-8 bg-[#0d1117] text-white">
      <SectionHeading
        eyebrow="Review queue"
        title="Move drafts through approval"
        description="A compact approval surface that keeps focus on selected workspace post drafts and clean state transitions."
      />

      <div className="mt-6 grid min-h-0 flex-1 gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div
          className="rounded-2xl border p-5 text-white flex flex-col justify-between"
          style={{ background: "#161b22", borderColor: "#30363d" }}
        >
          <div>
            <div className="flex items-center justify-between border-b border-[#21262d] pb-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Queue Overview</h4>
              <span className="text-[10px] text-white/40">{compactDrafts.length} drafts pending</span>
            </div>
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
                  className={`w-full rounded-xl border p-4 text-left transition ${
                    selectedDraft?.id === draft.id
                      ? "border-[#388bfd] bg-[#0d1117]"
                      : "border-[#21262d] bg-[#0d1117]/40 hover:bg-[#0d1117]/70"
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="text-xs font-bold text-white">{draft.title}</h3>
                    <StatusPill label={draft.review_status.replace(/_/g, " ")} tone={reviewTone(draft.review_status)} />
                  </div>
                  <p className="mt-2 line-clamp-2 text-xs text-white/50 leading-relaxed">{draft.creative_brief}</p>
                </button>
              ))}
              {!compactDrafts.length ? (
                <div className="rounded-xl border border-dashed border-[#30363d] p-5 text-center text-xs text-white/40 leading-relaxed">
                  No drafts yet. Generate a content plan first.
                </div>
              ) : null}
            </div>
          </div>
        </div>

        <div
          className="rounded-2xl border p-5 text-white flex flex-col justify-between"
          style={{ background: "#161b22", borderColor: "#30363d" }}
        >
          {selectedDraft ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-[#21262d] pb-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Selected Draft brief</h4>
                <span className="text-[10px] text-white/40">ID: {selectedDraft.id.slice(0, 8)}</span>
              </div>
              
              <div className="rounded-xl border border-[#21262d] bg-[#0d1117]/60 p-4 space-y-2">
                <span className="text-[9px] uppercase tracking-wider text-white/30 font-bold">Source Plan</span>
                <p className="text-xs font-bold text-white">{latestContentPlanQuery.data?.title ?? "Standard workspace plan"}</p>
                <p className="text-xs leading-relaxed text-white/70 border-t border-[#21262d] pt-2 whitespace-pre-wrap">{selectedDraft.caption}</p>
              </div>

              <label className="block">
                <span className="mb-1.5 block text-xs font-bold text-white/60 uppercase tracking-wider">Review status</span>
                <select
                  value={reviewStatus}
                  onChange={(event) =>
                    setReviewStatus(event.target.value as UpdateDraftRequest["review_status"])
                  }
                  className="w-full rounded-lg bg-[#0d1117] border border-[#30363d] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none cursor-pointer"
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

              <div className="flex flex-wrap gap-2.5 pt-2">
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
                  className="px-4 py-2.5 rounded-lg text-xs font-bold border border-[#30363d] hover:bg-white/5 text-white/80"
                >
                  {updateDraftMutation.isPending ? "Saving..." : "Save Status"}
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
                  className="px-4 py-2.5 rounded-lg text-xs font-bold transition-all shadow-[0_4px_12px_rgba(31,111,235,0.2)]"
                  style={{
                    background: "#1f6feb",
                    color: "#fff",
                    border: "1px solid rgba(255,255,255,0.1)",
                  }}
                >
                  {markPublishReadyMutation.isPending ? "Staging..." : "Mark Publish-Ready"}
                </button>
                <button
                  type="button"
                  disabled={publishDraftMutation.isPending}
                  onClick={() => publishDraftMutation.mutate({ draftId: selectedDraft.id, payload: {} })}
                  className="px-4 py-2.5 rounded-lg text-xs font-bold transition-all bg-[#238636] hover:bg-[#2ea043] text-white"
                >
                  {publishDraftMutation.isPending ? "Publishing..." : "Mock Publish"}
                </button>
              </div>
            </div>
          ) : (
            <p className="mt-4 text-xs text-white/40 text-center py-10">Select a draft from the queue.</p>
          )}
        </div>
      </div>
    </div>
  );
}
