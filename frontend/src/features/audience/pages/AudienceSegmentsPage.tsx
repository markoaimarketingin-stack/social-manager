import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import type { FormEvent } from "react";
import { useParams } from "react-router-dom";

import { apiDelete, apiGet, apiPost, apiPut } from "../../../lib/api/client";
import type { AudienceSegment } from "../../../lib/api/types/domain";
import type {
  CreateAudienceSegmentRequest,
  UpdateAudienceSegmentRequest,
} from "../../../lib/api/types/requests";
import { queryKeys } from "../../../lib/query/keys";
import { Panel } from "../../../components/ui/Panel";
import { SectionHeading } from "../../../components/ui/SectionHeading";

const initialFormState = {
  name: "",
  description: "",
  age_range: "",
  interests: "",
  primary_platform: "",
  messaging_angle: "",
};

export function AudienceSegmentsPage() {
  const { workspaceId = "" } = useParams();
  const queryClient = useQueryClient();
  const [formState, setFormState] = useState(initialFormState);
  const [editingSegmentId, setEditingSegmentId] = useState<string | null>(null);

  const audienceSegmentsQuery = useQuery({
    queryKey: queryKeys.audienceSegments(workspaceId),
    queryFn: () => apiGet<AudienceSegment[]>(`/api/v1/workspaces/${workspaceId}/audience-segments`),
    enabled: workspaceId.length > 0,
  });

  const upsertMutation = useMutation({
    mutationFn: async (payload: CreateAudienceSegmentRequest | UpdateAudienceSegmentRequest) => {
      if (editingSegmentId) {
        return apiPut<AudienceSegment, UpdateAudienceSegmentRequest>(
          `/api/v1/workspaces/${workspaceId}/audience-segments/${editingSegmentId}`,
          payload,
        );
      }
      return apiPost<AudienceSegment, CreateAudienceSegmentRequest>(
        `/api/v1/workspaces/${workspaceId}/audience-segments`,
        payload,
      );
    },
    onSuccess: async () => {
      setFormState(initialFormState);
      setEditingSegmentId(null);
      await queryClient.invalidateQueries({ queryKey: queryKeys.audienceSegments(workspaceId) });
      await queryClient.invalidateQueries({ queryKey: queryKeys.workspace(workspaceId) });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (segmentId: string) =>
      apiDelete(`/api/v1/workspaces/${workspaceId}/audience-segments/${segmentId}`),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.audienceSegments(workspaceId) });
      await queryClient.invalidateQueries({ queryKey: queryKeys.workspace(workspaceId) });
    },
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    upsertMutation.mutate({
      ...formState,
      interests: formState.interests
        .split(",")
        .map((interest) => interest.trim())
        .filter(Boolean),
    });
  };

  return (
    <div className="mx-auto flex min-h-full w-full max-w-6xl flex-col px-5 py-10 lg:px-8">
      <SectionHeading
        eyebrow="Audience foundation"
        title="Audience segments"
        description="Create the structured audience inputs the later strategy workflows will consume."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <section className="rounded-[2rem] border border-line bg-white p-6 text-black">
          <h2 className="text-xl font-semibold">
            {editingSegmentId ? "Edit segment" : "Add segment"}
          </h2>
          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            {[
              { key: "name", label: "Segment name" },
              { key: "age_range", label: "Age range" },
              { key: "primary_platform", label: "Primary platform" },
              { key: "interests", label: "Interests (comma separated)" },
            ].map((field) => (
              <label key={field.key} className="block">
                <span className="mb-2 block text-sm font-medium">{field.label}</span>
                <input
                  value={formState[field.key as keyof typeof formState]}
                  onChange={(event) =>
                    setFormState((current) => ({ ...current, [field.key]: event.target.value }))
                  }
                  className="w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                />
              </label>
            ))}

            {[
              { key: "description", label: "Description" },
              { key: "messaging_angle", label: "Messaging angle" },
            ].map((field) => (
              <label key={field.key} className="block">
                <span className="mb-2 block text-sm font-medium">{field.label}</span>
                <textarea
                  value={formState[field.key as keyof typeof formState]}
                  onChange={(event) =>
                    setFormState((current) => ({ ...current, [field.key]: event.target.value }))
                  }
                  className="min-h-28 w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                />
              </label>
            ))}

            <div className="flex flex-wrap gap-3">
              <button
                type="submit"
                disabled={upsertMutation.isPending}
                className="rounded-full bg-black px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_50px_rgba(0,0,0,0.18)] disabled:opacity-60"
              >
                {upsertMutation.isPending
                  ? "Saving..."
                  : editingSegmentId
                    ? "Save changes"
                    : "Add segment"}
              </button>
              {editingSegmentId ? (
                <button
                  type="button"
                  onClick={() => {
                    setEditingSegmentId(null);
                    setFormState(initialFormState);
                  }}
                  className="rounded-full border border-black/10 px-5 py-3 text-sm font-semibold"
                >
                  Cancel edit
                </button>
              ) : null}
            </div>
          </form>
        </section>

        <Panel eyebrow="Saved segments" title="Segment library">
          <div className="mt-5 space-y-4">
            {(audienceSegmentsQuery.data ?? []).map((segment) => (
              <article key={segment.id} className="rounded-3xl border border-line bg-white/5 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold">{segment.name}</h2>
                    <p className="mt-2 text-sm text-white/55">
                      {segment.description || "No description yet."}
                    </p>
                  </div>
                  <span className="rounded-full border border-line px-3 py-1 text-xs text-white/55">
                    {segment.primary_platform || "Platform TBD"}
                  </span>
                </div>

                <p className="mt-4 text-sm text-ink/80">
                  Interests: {segment.interests.length ? segment.interests.join(", ") : "None listed"}
                </p>
                <p className="mt-1 text-sm text-ink/80">
                  Messaging angle: {segment.messaging_angle || "Not defined yet"}
                </p>

                <div className="mt-4 flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setEditingSegmentId(segment.id);
                      setFormState({
                        name: segment.name,
                        description: segment.description ?? "",
                        age_range: segment.age_range ?? "",
                        interests: segment.interests.join(", "),
                        primary_platform: segment.primary_platform ?? "",
                        messaging_angle: segment.messaging_angle ?? "",
                      });
                    }}
                    className="rounded-full border border-line px-4 py-2 text-sm"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteMutation.mutate(segment.id)}
                    className="rounded-full border border-red-500/30 px-4 py-2 text-sm text-red-200"
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}

            {audienceSegmentsQuery.data?.length ? null : (
              <div className="rounded-3xl border border-dashed border-line p-6 text-sm text-white/55">
                No audience segments yet. Add the first one to give future workflows structured input.
              </div>
            )}
          </div>
        </Panel>
      </div>
    </div>
  );
}
