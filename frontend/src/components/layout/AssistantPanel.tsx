import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { useWorkspaceChrome } from "../../features/workspace/components/WorkspaceChromeContext";
import { ApiError, apiGet } from "../../lib/api/client";
import type { WorkspaceActivitySummary } from "../../lib/api/types/domain";
import { queryKeys } from "../../lib/query/keys";

type AssistantPanelProps = {
  workspaceId: string;
};

const suggestions = [
  "Approve the active strategy before regenerating planning.",
  "Stage at least one publish-ready draft for the founder walkthrough.",
  "Use the intelligence hub to anchor trend and competitor context.",
];

export function AssistantPanel({ workspaceId }: AssistantPanelProps) {
  const [tab, setTab] = useState<"chat" | "suggestions">("chat");
  const [chatInput, setChatInput] = useState("");
  const { pushToast } = useWorkspaceChrome();

  const activitySummaryQuery = useQuery({
    queryKey: queryKeys.activitySummary(workspaceId),
    queryFn: () => apiGet<WorkspaceActivitySummary>(`/api/v1/workspaces/${workspaceId}/activity/summary`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  return (
    <div className="assistant-panel flex h-full w-full flex-col gap-4 overflow-hidden p-3 text-white">
      <div className="flex items-start justify-between pt-0">
        <div className="flex items-center gap-3">
          <img
            src="/favicon.svg"
            alt="Marko"
            className="h-9 w-9 rounded-md border border-white/10 bg-black/60 p-1"
          />
          <div>
            <p className="text-sm font-semibold">Assistant</p>
            <p className="text-[10px] uppercase tracking-[0.35em] text-white/40">Read-only mode</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-white/60">
          {["+", "↺", "X"].map((label) => (
            <div
              key={label}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-xs"
            >
              {label}
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 rounded-full border border-white/10 bg-black px-2 py-1 text-xs">
        <button
          type="button"
          onClick={() => setTab("chat")}
          className={`flex-1 rounded-full px-3 py-2 font-semibold ${
            tab === "chat" ? "bg-white/10 text-white" : "text-white/50"
          }`}
        >
          Chatbot
        </button>
        <button
          type="button"
          onClick={() => setTab("suggestions")}
          className={`flex-1 rounded-full px-3 py-2 font-semibold ${
            tab === "suggestions" ? "bg-white/10 text-white" : "text-white/50"
          }`}
        >
          Suggestions
        </button>
      </div>

      <div className="flex-1 overflow-hidden pr-1">
        {tab === "chat" ? (
          <div className="space-y-4">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-md border border-white/10 bg-black/60 text-white">
                  #
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">Social Supervisor</p>
                  <p className="text-[10px] text-white/50">Orchestrator</p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.3em] text-white/50">
                <span>#</span>
                <span>Context</span>
              </div>
              <p className="text-sm leading-6 text-white/75">
                {activitySummaryQuery.data?.latest_summary ??
                  "Ask mode is for Q&A and fetching context. Agent mode can prepare optimizations behind confirmation."}
              </p>
            </div>
            <div className="h-24 rounded-2xl border border-dashed border-white/10 bg-white/[0.02]" />
          </div>
        ) : (
          <div className="space-y-3">
            {suggestions.map((suggestion) => (
              <div key={suggestion} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-white">
                <p className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/50">Suggestion</p>
                <p className="mt-2 text-sm font-semibold text-white">{suggestion}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          if (!chatInput.trim()) {
            return;
          }
          pushToast(`Assistant noted: ${chatInput.trim()}`);
          setChatInput("");
        }}
        className="rounded-[28px] border border-white/10 bg-white/5 p-3 shadow-[0_20px_60px_rgba(0,0,0,0.45)]"
      >
        <div className="flex flex-col gap-3">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-white">
              #
            </div>
            <div className="flex-1">
              <p className="mb-1 text-xs text-white/60">Add context (#), extensions (@), commands (/)</p>
              <input
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                type="text"
                placeholder="Ask or instruct the assistant..."
                className="min-w-0 w-full bg-transparent text-xs text-white placeholder:text-white/35 focus:outline-none"
              />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-full border border-white/10 bg-black/40 px-3 py-2 text-xs text-white">
              Guided
            </div>
            <div className="flex-1 rounded-full border border-white/10 bg-black/40 px-3 py-2 text-xs text-white/70">
              marko-2.0-mini
            </div>
            <button
              type="submit"
              className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-sm font-semibold text-black transition hover:bg-white/90"
            >
              &rsaquo;
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
