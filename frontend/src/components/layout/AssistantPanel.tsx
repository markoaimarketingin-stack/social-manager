import { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";

import { useWorkspaceChrome } from "../../features/workspace/components/WorkspaceChromeContext";
import { useWorkspaceContext } from "../../features/workspace/hooks/useWorkspaceContext";

type AssistantPanelProps = {
  workspaceId: string;
};

type AssistantTab = "chatbot" | "suggestions";

const routeCopy = {
  overview: {
    title: "Workspace overview",
    summary: "Monitoring the full operating lane across strategy, planning, review, and publish staging.",
    command: "Summarize the workspace operating posture",
  },
  intelligence: {
    title: "Intelligence board",
    summary: "Watching the upstream signal layer so planning and approvals stay grounded in live context.",
    command: "Surface the strongest intelligence signal",
  },
  strategy: {
    title: "Strategy workflow",
    summary: "Tracking revision status, active version lineage, and the next approval handoff into planning.",
    command: "Explain the current strategy revision",
  },
  planning: {
    title: "Planning cycle",
    summary: "Holding the bridge between approved strategy and the next reviewable post sequence.",
    command: "Show the next planning action",
  },
  review: {
    title: "Review queue",
    summary: "Following draft movement, reviewer decisions, and items close to publish-ready staging.",
    command: "Show what is waiting for approval",
  },
  publishing: {
    title: "Publishing queue",
    summary: "Watching publish-ready drafts, schedule posture, and the next outbound slot.",
    command: "Summarize the publishing queue",
  },
  brand: {
    title: "Brand profile",
    summary: "Standing by on brand inputs that will shape the next strategy generation pass.",
    command: "Check whether the brand profile is strategy-ready",
  },
  audience: {
    title: "Audience segments",
    summary: "Tracking segmentation inputs that sharpen platform angles and message fit.",
    command: "Summarize the active audience mix",
  },
} as const;

function getRouteKey(pathname: string) {
  if (pathname.endsWith("/intelligence")) return "intelligence";
  if (pathname.endsWith("/strategy")) return "strategy";
  if (pathname.endsWith("/planning")) return "planning";
  if (pathname.endsWith("/review")) return "review";
  if (pathname.endsWith("/publishing")) return "publishing";
  if (pathname.endsWith("/brand-profile")) return "brand";
  if (pathname.endsWith("/audience-segments")) return "audience";
  return "overview";
}

function formatRelativeMoment(value: string | null | undefined) {
  if (!value) return "Standing by";

  const diffMs = Date.now() - new Date(value).getTime();
  const minutes = Math.max(1, Math.round(diffMs / 60000));

  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  return `${days}d ago`;
}

function statusLabel(status: string | null | undefined) {
  return status ? status.replace(/_/g, " ") : "idle";
}

export function AssistantPanel({ workspaceId }: AssistantPanelProps) {
  const [tab, setTab] = useState<AssistantTab>("chatbot");
  const [chatInput, setChatInput] = useState("");
  const [messageIndex, setMessageIndex] = useState(0);
  const { pathname } = useLocation();
  const {
    toggleAssistant,
    openKnowledgeBase,
    openNotifications,
    pushToast,
  } = useWorkspaceChrome();
  const {
    workspaceQuery,
    brandProfileQuery,
    workflowRunsQuery,
    latestStrategyQuery,
    latestContentPlanQuery,
    reviewQueueQuery,
    publishingQueueQuery,
    activityQuery,
    activitySummaryQuery,
  } = useWorkspaceContext();

  const routeKey = getRouteKey(pathname);
  const routeMeta = routeCopy[routeKey];
  const workspaceName = workspaceQuery.data?.name ?? workspaceId;
  const activity = activityQuery.data ?? [];
  const latestActivity = activity[0] ?? null;
  const latestStrategy = latestStrategyQuery.data ?? null;
  const latestPlan = latestContentPlanQuery.data ?? null;
  const reviewQueue = reviewQueueQuery.data ?? [];
  const publishingQueue = publishingQueueQuery.data ?? [];
  const workflowRuns = workflowRunsQuery.data ?? [];
  const latestRun = workflowRuns[0] ?? null;

  const operationalMessages = useMemo(() => {
    const messages = [
      activitySummaryQuery.data?.latest_summary,
      routeMeta.summary,
      latestStrategy
        ? `Strategy v${latestStrategy.version_number} is ${statusLabel(latestStrategy.status)}${latestStrategy.is_active ? " and remains the active operating version." : "."}`
        : null,
      latestPlan
        ? `${latestPlan.title} is ${statusLabel(latestPlan.status)} with ${latestPlan.planned_posts.length} planned posts attached to the current workflow.`
        : null,
      reviewQueue.length > 0
        ? `${reviewQueue.length} draft${reviewQueue.length > 1 ? "s are" : " is"} still moving through review.`
        : "No drafts are blocked in review right now.",
      publishingQueue[0]
        ? `Next publish-ready item: '${publishingQueue[0].title}'${publishingQueue[0].scheduled_publish_at ? ` scheduled for ${new Date(publishingQueue[0].scheduled_publish_at).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}.` : " awaiting a scheduled slot."}`
        : "Nothing is staged in the publish-ready queue yet.",
      latestRun
        ? `Latest workflow run is ${statusLabel(latestRun.status)} on ${statusLabel(latestRun.workflow_type)}.`
        : null,
      brandProfileQuery.data
        ? `${brandProfileQuery.data.brand_name} brand context is loaded for downstream operations.`
        : "Brand profile context has not been completed yet.",
    ].filter((value): value is string => Boolean(value));

    return Array.from(new Set(messages));
  }, [
    activitySummaryQuery.data?.latest_summary,
    brandProfileQuery.data,
    latestPlan,
    latestRun,
    latestStrategy,
    publishingQueue,
    reviewQueue.length,
    routeMeta.summary,
  ]);

  useEffect(() => {
    setMessageIndex(0);
  }, [pathname]);

  useEffect(() => {
    if (tab !== "chatbot" || operationalMessages.length <= 1) {
      return;
    }

    const interval = window.setInterval(() => {
      setMessageIndex((current) => (current + 1) % operationalMessages.length);
    }, 4800);

    return () => window.clearInterval(interval);
  }, [operationalMessages.length, tab]);

  const currentMessage = operationalMessages[messageIndex] ?? "Supervisor linked to the current workspace.";
  const liveSignals = [
    latestStrategy ? `Strategy v${latestStrategy.version_number}` : null,
    latestPlan ? `${latestPlan.planned_posts.length} post${latestPlan.planned_posts.length === 1 ? "" : "s"} in plan` : null,
    reviewQueue.length ? `${reviewQueue.length} in review` : null,
    publishingQueue.length ? `${publishingQueue.length} publish-ready` : null,
  ].filter((value): value is string => Boolean(value));

  const suggestions = [
    routeMeta.command,
    publishingQueue[0]
      ? `Open the publish-ready context for '${publishingQueue[0].title}'`
      : "Show the next item that should move to publish-ready",
    latestActivity?.summary ?? "Summarize the latest workflow event",
  ];

  const isSubmitDisabled = !chatInput.trim();

  return (
    <div className="assistant-panel flex h-full w-full flex-col overflow-hidden bg-[#050505] text-white">
      <div className="border-b border-white/[0.05] px-3.5 pb-3.5 pt-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-start gap-3">
            <div className="assistant-orb relative mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-[0.65rem] border border-white/10 bg-[#0c0c0c] shadow-[inset_0_1px_0_rgba(255,255,255,0.06),0_10px_26px_rgba(0,0,0,0.36)]">
              <div className="absolute inset-0 rounded-[0.95rem] bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.08),transparent_60%)]" />
              <svg className="relative h-4 w-4 text-white/90" viewBox="0 0 24 24" fill="none">
                <path
                  d="M8 8.75h8M8 12h5m-2-7 1.2 2.3L15 8.5l-2.2 1.2L11 12l-1.2-2.3L7.5 8.5l2.3-1.2L11 5Z"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <rect x="4.5" y="4.5" width="15" height="15" rx="4" stroke="currentColor" strokeWidth="1.5" />
              </svg>
            </div>
            <div className="min-w-0">
              <p className="brand-title text-[0.92rem] font-semibold text-white">Assistant</p>
              <p className="mt-0.5 text-[9px] uppercase tracking-[0.34em] text-[#bba48f]">Read-only mode</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={openKnowledgeBase}
              className="flex h-8 w-8 items-center justify-center rounded-[0.7rem] border border-white/10 bg-white/[0.05] text-white/65 transition-all duration-200 hover:border-white/18 hover:bg-white/[0.08] hover:text-white"
              aria-label="Open knowledge base"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none">
                <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
            <button
              type="button"
              onClick={openNotifications}
              className="flex h-8 w-8 items-center justify-center rounded-[0.7rem] border border-white/10 bg-white/[0.05] text-white/65 transition-all duration-200 hover:border-white/18 hover:bg-white/[0.08] hover:text-white"
              aria-label="Open operational notifications"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 7v5l3 2m5-2a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
            <button
              type="button"
              onClick={toggleAssistant}
              className="flex h-8 w-8 items-center justify-center rounded-[0.7rem] border border-white/10 bg-white/[0.05] text-white/65 transition-all duration-200 hover:border-white/18 hover:bg-white/[0.08] hover:text-white"
              aria-label="Collapse assistant"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none">
                <path d="m7 7 10 10M17 7 7 17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
          </div>
        </div>

        <div className="mt-4 rounded-[1.05rem] border border-white/[0.08] bg-black p-1 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
          <div className="grid grid-cols-2 gap-1 text-[0.84rem] font-semibold">
            {[
              { key: "chatbot" as const, label: "Chatbot" },
              { key: "suggestions" as const, label: "Suggestions" },
            ].map((item) => (
              <button
                key={item.key}
                type="button"
                onClick={() => setTab(item.key)}
                className={`rounded-[0.85rem] px-3 py-2 transition-all duration-250 ${
                  tab === item.key
                    ? "bg-white/[0.12] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]"
                    : "text-[#85776b] hover:bg-white/[0.04] hover:text-[#cdb79f]"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="scrollbar-thin min-h-0 flex-1 overflow-y-auto px-3.5 pb-3.5 pt-4">
        {tab === "chatbot" ? (
          <div className="flex min-h-full flex-col">
            <div className="space-y-3">
              <div className="rounded-[0.9rem] border border-white/[0.08] bg-[#1b1a19] px-3 py-2.5 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] transition-all duration-200 hover:border-white/[0.12] hover:bg-[#201f1d]">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-[0.7rem] border border-white/10 bg-black text-[#f6e2c8] shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
                    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <path
                        d="M9 9.5h.01M15 9.5h.01M8.2 15h7.6M8 5h8a3 3 0 0 1 3 3v5a3 3 0 0 1-3 3h-1.8L12 19l-2.2-3H8a3 3 0 0 1-3-3V8a3 3 0 0 1 3-3Z"
                        stroke="currentColor"
                        strokeWidth="1.7"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <p className="text-[0.9rem] font-semibold text-white">Social Supervisor</p>
                    <p className="mt-0.5 text-[0.76rem] text-[#b69879]">Orchestrator</p>
                  </div>
                </div>
              </div>

              <div className="assistant-message-card rounded-[1rem] border border-white/[0.08] bg-[#1a1918] px-3.5 py-3.5 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] transition-all duration-300 hover:border-white/[0.12] hover:bg-[#1d1c1b]">
                <p key={`${routeKey}-${messageIndex}`} className="assistant-message text-[0.88rem] leading-[1.5] text-[#dfd3c6]">
                  {activitySummaryQuery.isLoading ? "Linking current workspace context..." : currentMessage}
                </p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  <span className="rounded-full border border-white/[0.08] bg-black/30 px-2 py-0.5 text-[9px] uppercase tracking-[0.24em] text-white/42">
                    {routeMeta.title}
                  </span>
                  {liveSignals.slice(0, 2).map((signal) => (
                    <span
                      key={signal}
                      className="rounded-full border border-white/[0.08] bg-black/30 px-2 py-0.5 text-[9px] uppercase tracking-[0.2em] text-white/42"
                    >
                      {signal}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex-1" />

            <div className="px-1 pb-1 pt-4">
              <div className="flex items-center justify-between text-[9px] uppercase tracking-[0.28em] text-white/24">
                <span>{workspaceName}</span>
                <span>{formatRelativeMoment(latestActivity?.created_at)}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => setChatInput(suggestion)}
                className="w-full rounded-[0.95rem] border border-white/[0.07] bg-[#161515] px-3.5 py-3 text-left text-[0.86rem] leading-6 text-[#d5c8bb] transition-all duration-200 hover:-translate-y-[1px] hover:border-white/[0.12] hover:bg-[#1b1a1a]"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="border-t border-white/[0.05] px-3.5 pb-3 pt-3">
        <form
          className="assistant-dock rounded-[1.2rem] border border-white/[0.08] bg-[#171615]/92 p-3 shadow-[0_16px_42px_rgba(0,0,0,0.42),inset_0_1px_0_rgba(255,255,255,0.04)] backdrop-blur-xl"
          onSubmit={(event) => {
            event.preventDefault();
            if (!chatInput.trim()) {
              return;
            }
            pushToast(`Assistant logged: ${chatInput.trim()}`);
            setChatInput("");
          }}
        >
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-[0.7rem] border border-white/[0.11] bg-white/[0.04] text-white/78">
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none">
                <path
                  d="m8.5 12 4-4a2.8 2.8 0 1 1 4 4l-5.2 5.2a4.2 4.2 0 1 1-6-6L10 6"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[0.78rem] text-white/62">Add context (#), extensions (@), commands (/)</p>
              <input
                type="text"
                className="mt-1 w-full bg-transparent p-0 text-[0.86rem] text-white placeholder:text-white/28 focus:outline-none"
                placeholder="Ask or instruct the assistant..."
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
              />
            </div>
          </div>

          <div className="mt-3 flex items-center gap-2">
            <button
              type="button"
              onClick={() => pushToast(`Context attached from ${routeMeta.title}.`)}
              className="flex min-w-[74px] items-center justify-between gap-2 rounded-full border border-white/[0.1] bg-black/35 px-3 py-2 text-[0.82rem] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] transition-all duration-200 hover:border-white/[0.16] hover:bg-black/55"
            >
              <span>Ask</span>
              <svg className="h-4 w-4 text-white/70" viewBox="0 0 24 24" fill="none">
                <path d="m7 10 5 5 5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <button
              type="button"
              onClick={() => pushToast(`Using route context: ${routeMeta.title}.`)}
              className="flex min-w-0 flex-1 items-center justify-between gap-2 rounded-full border border-white/[0.1] bg-black/35 px-3 py-2 text-[0.82rem] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] transition-all duration-200 hover:border-white/[0.16] hover:bg-black/55"
            >
              <span className="truncate">marko-2.0-mini</span>
              <svg className="h-4 w-4 shrink-0 text-white/70" viewBox="0 0 24 24" fill="none">
                <path d="m7 10 5 5 5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <button
              type="submit"
              disabled={isSubmitDisabled}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#8f8b85] text-black transition-all duration-200 hover:scale-[1.02] hover:bg-[#a9a39c] disabled:cursor-not-allowed disabled:bg-white/[0.1] disabled:text-white/28 disabled:hover:scale-100"
              aria-label="Send command"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none">
                <path
                  d="M5 12h12m0 0-4.5-4.5M17 12l-4.5 4.5"
                  stroke="currentColor"
                  strokeWidth="1.9"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
