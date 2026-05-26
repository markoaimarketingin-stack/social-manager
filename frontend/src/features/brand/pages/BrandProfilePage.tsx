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
import { Panel } from "../../../components/ui/Panel";
import { SectionHeading } from "../../../components/ui/SectionHeading";

const emptyForm = {
  brand_name: "",
  industry: "",
  description: "",
  website_url: "",
  voice_summary: "",
  mission: "",
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
      setFormState({
        brand_name: brandProfileQuery.data.brand_name,
        industry: brandProfileQuery.data.industry,
        description: brandProfileQuery.data.description ?? "",
        website_url: brandProfileQuery.data.website_url ?? "",
        voice_summary: brandProfileQuery.data.voice_summary ?? "",
        mission: brandProfileQuery.data.mission ?? "",
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
      setFeedback("Brand profile saved");
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
      setFeedback("Strategy workflow stub executed");
      await queryClient.invalidateQueries({ queryKey: queryKeys.workflowRuns(workspaceId) });
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
      website_url: formState.website_url.trim() ? formState.website_url.trim() : null,
    });
  };

  return (
    <div className="mx-auto flex min-h-full w-full max-w-6xl flex-col px-5 py-10 lg:px-8">
      <SectionHeading
        eyebrow="Workspace foundation"
        title="Brand profile"
        description="Capture the brand inputs that will eventually feed strategy and planning workflows."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <section className="rounded-[2rem] border border-line bg-white p-6 text-black">
          <h2 className="text-xl font-semibold">
            {workspaceQuery.data?.name ?? "Workspace"} profile
          </h2>

          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            {[
              { key: "brand_name", label: "Brand name" },
              { key: "industry", label: "Industry" },
              { key: "website_url", label: "Website URL" },
            ].map((field) => (
              <label key={field.key} className="block">
                <span className="mb-2 block text-sm font-medium">{field.label}</span>
                <input
                  value={formState[field.key as keyof typeof formState]}
                  onChange={(event) =>
                    setFormState((current) => ({
                      ...current,
                      [field.key]: event.target.value,
                    }))
                  }
                  className="w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                />
              </label>
            ))}

            {[
              { key: "description", label: "Description" },
              { key: "voice_summary", label: "Voice summary" },
              { key: "mission", label: "Mission" },
            ].map((field) => (
              <label key={field.key} className="block">
                <span className="mb-2 block text-sm font-medium">{field.label}</span>
                <textarea
                  value={formState[field.key as keyof typeof formState]}
                  onChange={(event) =>
                    setFormState((current) => ({
                      ...current,
                      [field.key]: event.target.value,
                    }))
                  }
                  className="min-h-28 w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                />
              </label>
            ))}

            {feedback ? <p className="text-sm text-black/70">{feedback}</p> : null}

            <div className="flex flex-wrap gap-3 mt-4">
              <button
                type="submit"
                disabled={saveBrandProfileMutation.isPending}
                className="rounded-full bg-black px-5 py-3 text-sm font-bold text-white shadow-[0_18px_50px_rgba(0,0,0,0.18)] transition-all hover:bg-black/80 hover:-translate-y-0.5 active:translate-y-0 active:scale-95 disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:scale-100 disabled:pointer-events-none"
              >
                {saveBrandProfileMutation.isPending ? "Saving..." : "Save brand profile"}
              </button>
              <button
                type="button"
                disabled={strategyRunMutation.isPending}
                onClick={() =>
                  strategyRunMutation.mutate({
                    goal: "Generate a first strategy snapshot from Sprint 1 inputs",
                  })
                }
                className="rounded-full border border-black/10 px-5 py-3 text-sm font-semibold transition-all hover:bg-black/5 hover:-translate-y-0.5 active:translate-y-0 active:scale-95 disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:scale-100 disabled:pointer-events-none"
              >
                {strategyRunMutation.isPending ? "Running..." : "Run strategy stub"}
              </button>
            </div>
          </form>
        </section>

        <Panel eyebrow="What this powers" title="Typed workflow inputs">
          <div className="mt-5 space-y-4 text-sm leading-7 text-ink/85">
            <p>Brand inputs will become typed workflow inputs instead of mutable shared app state.</p>
            <p>
              Workspace members:{" "}
              <span className="font-semibold">{workspaceQuery.data?.member_count ?? 0}</span> |
              Audience segments:{" "}
              <span className="font-semibold">{workspaceQuery.data?.audience_segment_count ?? 0}</span>
            </p>
            <p className="text-white/55">
              Full AI strategy generation is intentionally deferred. The current button writes a typed
              workflow run record only.
            </p>
          </div>
        </Panel>
      </div>
    </div>
  );
}
