import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useParams } from "react-router-dom";

import { ApiError, apiGet, apiPost, apiPut } from "../../../lib/api/client";
import type { BrandProfile, WorkflowRun, WorkspaceDetail } from "../../../lib/api/types/domain";
import type {
  StartStrategyRunRequest,
  UpsertBrandProfileRequest,
} from "../../../lib/api/types/requests";
import { queryKeys } from "../../../lib/query/keys";
import { SectionHeading } from "../../../components/ui/SectionHeading";

const emptyForm = {
  brand_name: "",
  industry: "",
  description: "",
  website_url: "",
  voice_summary: "",
  mission: "",
  banned_phrases: "",
};

export function BrandProfilePage() {
  const { workspaceId = "" } = useParams();
  const queryClient = useQueryClient();
  const [formState, setFormState] = useState(emptyForm);
  const [feedback, setFeedback] = useState<string | null>(null);

  const workspaceQuery = useQuery({
    queryKey: queryKeys.workspace(workspaceId),
    queryFn: () => apiGet<WorkspaceDetail>(`/api/v1/workspaces/${workspaceId}`),
    enabled: workspaceId.length > 0,
  });

  const brandProfileQuery = useQuery({
    queryKey: queryKeys.brandProfile(workspaceId),
    queryFn: () => apiGet<BrandProfile>(`/api/v1/workspaces/${workspaceId}/brand-profile`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  useEffect(() => {
    if (brandProfileQuery.data) {
      const voice = brandProfileQuery.data.voice_summary ?? "";
      const splitIdx = voice.indexOf("\n[BANNED_PHRASES]:");
      const cleanVoice = splitIdx !== -1 ? voice.slice(0, splitIdx) : voice;
      const banned = splitIdx !== -1 ? voice.slice(splitIdx + "\n[BANNED_PHRASES]:".length).trim() : "";

      setFormState({
        brand_name: brandProfileQuery.data.brand_name,
        industry: brandProfileQuery.data.industry,
        description: brandProfileQuery.data.description ?? "",
        website_url: brandProfileQuery.data.website_url ?? "",
        voice_summary: cleanVoice,
        mission: brandProfileQuery.data.mission ?? "",
        banned_phrases: banned,
      });
    }
  }, [brandProfileQuery.data]);

  const saveBrandProfileMutation = useMutation({
    mutationFn: (payload: UpsertBrandProfileRequest) =>
      apiPut<BrandProfile, UpsertBrandProfileRequest>(
        `/api/v1/workspaces/${workspaceId}/brand-profile`,
        payload,
      ),
    onSuccess: async () => {
      setFeedback("✓ Brand settings saved successfully");
      await queryClient.invalidateQueries({ queryKey: queryKeys.brandProfile(workspaceId) });
      await queryClient.invalidateQueries({ queryKey: queryKeys.workspace(workspaceId) });
    },
    onError: (error) => {
      setFeedback(error instanceof Error ? error.message : "Failed to save brand profile");
    },
  });

  const strategyRunMutation = useMutation({
    mutationFn: (payload: StartStrategyRunRequest) =>
      apiPost<WorkflowRun, StartStrategyRunRequest>(
        `/api/v1/workspaces/${workspaceId}/strategy-runs`,
        payload,
      ),
    onSuccess: async () => {
      setFeedback("✓ Strategy workflow completed successfully");
      await queryClient.invalidateQueries({ queryKey: queryKeys.workflowRuns(workspaceId) });
      await queryClient.invalidateQueries({ queryKey: queryKeys.strategies(workspaceId) });
      await queryClient.invalidateQueries({ queryKey: queryKeys.latestStrategy(workspaceId) });
      await queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) });
      await queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) });
    },
    onError: (error) => {
      setFeedback(error instanceof Error ? error.message : "Failed to run strategy workflow");
    },
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFeedback(null);
    saveBrandProfileMutation.mutate({
      ...formState,
      voice_summary: `${formState.voice_summary}\n[BANNED_PHRASES]: ${formState.banned_phrases}`,
      website_url: formState.website_url.trim() ? formState.website_url.trim() : null,
    });
  };

  return (
    <div className="mx-auto flex min-h-full w-full max-w-6xl flex-col px-6 py-8 bg-[#000000] text-white">
      <SectionHeading
        eyebrow="Memory Agent Settings"
        title="Brand Settings & Memory Profile"
        description="Manage tone guidelines, voice constraints, banned phrases, and audience settings governing memory retrieval."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <section
          className="rounded-2xl border p-6 text-white space-y-6"
          style={{ background: "#000000", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <h2 className="text-sm font-bold uppercase tracking-wider text-white/80">
            {workspaceQuery.data?.name ?? "Workspace"} Profile Details
          </h2>

          <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
            <div className="grid gap-4 md:grid-cols-2">
              {[
                { key: "brand_name", label: "Brand name" },
                { key: "industry", label: "Industry" },
              ].map((field) => (
                <label key={field.key} className="block">
                  <span className="mb-1.5 block text-xs font-bold text-white/60 uppercase tracking-wider">{field.label}</span>
                  <input
                    value={formState[field.key as keyof typeof formState]}
                    onChange={(event) =>
                      setFormState((current) => ({
                        ...current,
                        [field.key]: event.target.value,
                      }))
                    }
                    className="w-full rounded-lg bg-[#000000] border border-[rgba(255,255,255,0.08)] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none"
                  />
                </label>
              ))}
            </div>

            <label className="block">
              <span className="mb-1.5 block text-xs font-bold text-white/60 uppercase tracking-wider">Website URL</span>
              <input
                value={formState.website_url}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    website_url: event.target.value,
                  }))
                }
                className="w-full rounded-lg bg-[#000000] border border-[rgba(255,255,255,0.08)] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none"
              />
            </label>

            <label className="block">
              <span className="mb-1.5 block text-xs font-bold text-white/60 uppercase tracking-wider">Banned Phrases</span>
              <textarea
                value={formState.banned_phrases}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    banned_phrases: event.target.value,
                  }))
                }
                placeholder="E.g., guarantee, risk-free, cash-back, absolute profit (separated by commas)"
                className="min-h-16 w-full rounded-lg bg-[#000000] border border-[rgba(255,255,255,0.08)] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none resize-none"
              />
            </label>

            {[
              { key: "description", label: "Description / Product details" },
              { key: "voice_summary", label: "Voice summary (friendly, expert, direct etc.)" },
              { key: "mission", label: "Mission & Value Statement" },
            ].map((field) => (
              <label key={field.key} className="block">
                <span className="mb-1.5 block text-xs font-bold text-white/60 uppercase tracking-wider">{field.label}</span>
                <textarea
                  value={formState[field.key as keyof typeof formState]}
                  onChange={(event) =>
                    setFormState((current) => ({
                      ...current,
                      [field.key]: event.target.value,
                    }))
                  }
                  className="min-h-24 w-full rounded-lg bg-[#000000] border border-[rgba(255,255,255,0.08)] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none resize-none"
                />
              </label>
            ))}

            {feedback && (
              <p
                className="text-xs font-semibold"
                style={{ color: feedback.startsWith("✓") ? "#3fb950" : "#f85149" }}
              >
                {feedback}
              </p>
            )}

            <div className="flex flex-wrap gap-2.5 pt-2">
              <button
                type="submit"
                disabled={saveBrandProfileMutation.isPending}
                className="px-4 py-2.5 rounded-lg text-xs font-bold transition-all shadow-[0_4px_12px_rgba(35,134,54,0.2)] disabled:opacity-55"
                style={{
                  background: "#238636",
                  color: "#fff",
                  border: "1px solid rgba(255,255,255,0.05)",
                }}
              >
                {saveBrandProfileMutation.isPending ? "Saving..." : "Save Brand Profile"}
              </button>
              <button
                type="button"
                disabled={strategyRunMutation.isPending}
                onClick={() =>
                  strategyRunMutation.mutate({
                    goal: "Generate a first strategy snapshot from Sprint 1 inputs",
                  })
                }
                className="px-4 py-2.5 rounded-lg text-xs font-bold transition-all border border-[rgba(255,255,255,0.08)] hover:bg-[#000000] disabled:opacity-55 text-white/80"
              >
                {strategyRunMutation.isPending ? "Running..." : "Run Strategy Workflow"}
              </button>
            </div>
          </form>
        </section>

        {/* Strategic context */}
        <div
          className="rounded-2xl border p-5 text-white space-y-4"
          style={{ background: "#000000", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <h3 className="text-xs font-bold uppercase tracking-wider text-white/60">What this powers</h3>
          <div className="space-y-4 text-xs leading-relaxed text-white/60">
            <p>Brand inputs will become typed workflow inputs instead of mutable shared app state.</p>
            <div className="flex items-center gap-4 py-2 border-y border-[rgba(255,255,255,0.04)]">
              <p>
                Workspace Members:{" "}
                <span className="font-bold text-white">{workspaceQuery.data?.member_count ?? 0}</span>
              </p>
              <p>
                Audience Segments:{" "}
                <span className="font-bold text-white">{workspaceQuery.data?.audience_segment_count ?? 0}</span>
              </p>
            </div>
            <p className="text-white/40 leading-relaxed">
              Strategy generation writes a typed workflow run now, so backend logic can attach directly
              to the same contract later.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
