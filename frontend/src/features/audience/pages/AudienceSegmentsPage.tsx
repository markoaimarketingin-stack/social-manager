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
    <div className="mx-auto flex min-h-full w-full max-w-6xl flex-col px-6 py-8 bg-[#000000] text-white">
      <SectionHeading
        eyebrow="Audience foundation"
        title="Audience segments"
        description="Create the structured audience inputs strategy workflows consume."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <section
          className="rounded-2xl border p-6 text-white space-y-6"
          style={{ background: "#161b22", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <h2 className="text-sm font-bold uppercase tracking-wider text-white/80">
            {editingSegmentId ? "Edit Audience Segment" : "Add Audience Segment"}
          </h2>
          <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
            {[
              { key: "name", label: "Segment name" },
              { key: "age_range", label: "Age range (e.g. 25-35)" },
              { key: "primary_platform", label: "Primary platform (e.g. linkedin, instagram)" },
              { key: "interests", label: "Interests (comma separated)" },
            ].map((field) => (
              <label key={field.key} className="block">
                <span className="mb-1.5 block text-xs font-bold text-white/60 uppercase tracking-wider">{field.label}</span>
                <input
                  value={formState[field.key as keyof typeof formState]}
                  onChange={(event) =>
                    setFormState((current) => ({ ...current, [field.key]: event.target.value }))
                  }
                  className="w-full rounded-lg bg-[#000000] border border-[rgba(255,255,255,0.08)] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none"
                />
              </label>
            ))}

            {[
              { key: "description", label: "Description / Persona traits" },
              { key: "messaging_angle", label: "Messaging angle / Core hook" },
            ].map((field) => (
              <label key={field.key} className="block">
                <span className="mb-1.5 block text-xs font-bold text-white/60 uppercase tracking-wider">{field.label}</span>
                <textarea
                  value={formState[field.key as keyof typeof formState]}
                  onChange={(event) =>
                    setFormState((current) => ({ ...current, [field.key]: event.target.value }))
                  }
                  className="min-h-24 w-full rounded-lg bg-[#000000] border border-[rgba(255,255,255,0.08)] px-3.5 py-2.5 text-xs text-white focus:border-[#388bfd] focus:outline-none transition-colors outline-none resize-none"
                />
              </label>
            ))}

            <div className="flex flex-wrap gap-2.5 pt-2">
              <button
                type="submit"
                disabled={upsertMutation.isPending}
                className="px-4 py-2.5 rounded-lg text-xs font-bold transition-all shadow-[0_4px_12px_rgba(35,134,54,0.2)] disabled:opacity-55"
                style={{
                  background: "#238636",
                  color: "#fff",
                  border: "1px solid rgba(255,255,255,0.05)",
                }}
              >
                {upsertMutation.isPending
                  ? "Saving..."
                  : editingSegmentId
                    ? "Save Changes"
                    : "Add Segment"}
              </button>
              {editingSegmentId ? (
                <button
                  type="button"
                  onClick={() => {
                    setEditingSegmentId(null);
                    setFormState(initialFormState);
                  }}
                  className="px-4 py-2.5 rounded-lg text-xs font-bold transition-all border border-[rgba(255,255,255,0.08)] hover:bg-white/5 text-white/80"
                >
                  Cancel Edit
                </button>
              ) : null}
            </div>
          </form>
        </section>

        {/* Saved segments list */}
        <div
          className="rounded-2xl border p-5 text-white flex flex-col"
          style={{ background: "#161b22", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <h3 className="text-xs font-bold uppercase tracking-wider text-white/60 mb-4">Segment Library</h3>
          <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1 scrollbar-thin">
            {(audienceSegmentsQuery.data ?? []).map((segment) => (
              <article
                key={segment.id}
                className="rounded-xl border p-4 bg-[#000000]/60 space-y-3.5 hover:border-[#388bfd]/30 transition-all duration-200"
                style={{ borderColor: "rgba(255,255,255,0.04)" }}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-xs font-bold text-white">{segment.name}</h2>
                    <p className="mt-1.5 text-[11px] text-white/50 leading-relaxed">
                      {segment.description || "No description yet."}
                    </p>
                  </div>
                  <span
                    className="rounded-full border px-2.5 py-0.5 text-[9px] font-bold uppercase tracking-wider shrink-0"
                    style={{
                      background: "rgba(56,139,253,0.06)",
                      color: "#388bfd",
                      borderColor: "rgba(56,139,253,0.2)",
                    }}
                  >
                    {segment.primary_platform || "Platform TBD"}
                  </span>
                </div>

                <div className="text-[10px] space-y-1 text-white/40 pt-2 border-t border-[rgba(255,255,255,0.04)]">
                  <p>
                    <span className="font-semibold text-white/60">Interests:</span>{" "}
                    {segment.interests.length ? segment.interests.join(", ") : "None listed"}
                  </p>
                  <p>
                    <span className="font-semibold text-white/60">Messaging Angle:</span>{" "}
                    {segment.messaging_angle || "Not defined yet"}
                  </p>
                </div>

                <div className="flex gap-2 pt-1.5">
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
                    className="px-3 py-1.5 rounded-md text-[10px] font-bold transition-all border border-[rgba(255,255,255,0.08)] hover:bg-white/5 text-white/80"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteMutation.mutate(segment.id)}
                    className="px-3 py-1.5 rounded-md text-[10px] font-bold transition-all border border-red-500/20 bg-red-500/5 hover:bg-red-500/10 text-[#f85149]"
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}

            {audienceSegmentsQuery.data?.length ? null : (
              <div className="rounded-xl border border-dashed border-[rgba(255,255,255,0.08)] p-6 text-center text-xs text-white/40 leading-relaxed">
                No audience segments yet. Add the first one to give future workflows structured input.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
