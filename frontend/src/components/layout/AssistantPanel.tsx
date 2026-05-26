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
    <div className="assistant-panel flex h-full w-full flex-col gap-5 overflow-hidden px-5 py-6 text-white bg-[#020202]">
      <div className="flex items-center justify-between pb-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="relative flex h-2 w-2 items-center justify-center">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
          </div>
          <div>
            <p className="brand-title text-base font-bold tracking-tight text-white/95">Intelligence</p>
            <p className="text-[10px] uppercase tracking-widest text-emerald-400/70 font-medium mt-1">Context Active</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1 rounded-xl border border-white/5 bg-white/[0.02] p-1 text-xs">
        <button
          type="button"
          onClick={() => setTab("chat")}
          className={`flex-1 rounded-lg px-3 py-2 font-medium transition-all ${
            tab === "chat" ? "bg-white/10 text-white shadow-sm" : "text-white/40 hover:text-white/80 hover:bg-white/[0.04]"
          }`}
        >
          Chat
        </button>
        <button
          type="button"
          onClick={() => setTab("suggestions")}
          className={`flex-1 rounded-lg px-3 py-2 font-medium transition-all ${
            tab === "suggestions" ? "bg-white/10 text-white shadow-sm" : "text-white/40 hover:text-white/80 hover:bg-white/[0.04]"
          }`}
        >
          Guidance
        </button>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin pr-1 pb-4">
        {tab === "chat" ? (
          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-white/50 shadow-inset">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
              <div className="mt-0.5 rounded-2xl rounded-tl-sm bg-white/[0.03] border border-white/5 px-4 py-3">
                <p className="text-[13px] leading-relaxed text-white/80">
                  {activitySummaryQuery.data?.latest_summary ??
                    "System nominal. Monitoring active workspace context."}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {suggestions.map((suggestion) => (
              <button key={suggestion} type="button" onClick={() => setChatInput(suggestion)} className="w-full text-left rounded-xl border border-white/5 bg-white/[0.02] p-4 text-[13px] leading-relaxed text-white/70 transition hover:bg-white/[0.05] hover:text-white/90">
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="mt-auto border-t border-white/5 pt-5 pb-1">
        <form
          className="relative flex items-center xl:rounded-full rounded-xl border border-white/10 bg-[#000] px-3 shadow-inset transition-colors focus-within:border-white/20 hover:bg-white/[0.02] focus-within:ring-1 focus-within:ring-white/10"
          onSubmit={(event) => {
            event.preventDefault();
            if (chatInput.trim()) {
              pushToast(`Task registered: ${chatInput.trim()}`);
              setChatInput("");
            }
          }}
        >
          <input
            type="text"
            className="w-full bg-transparent py-3 pl-1 pr-10 text-[13px] text-white placeholder-white/30 outline-none"
            placeholder="Issue command..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
          />
          <button
            type="submit"
            disabled={!chatInput.trim()}
            className="absolute right-2.5 flex h-7 w-7 items-center justify-center rounded-full bg-white/10 text-white/50 transition-all hover:bg-white/20 hover:text-white disabled:pointer-events-none disabled:opacity-30 active:scale-95"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
          </button>
        </form>
      </div>
    </div>
  );
}
