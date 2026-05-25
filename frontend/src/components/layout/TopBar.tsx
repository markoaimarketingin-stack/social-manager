import { useLocation } from "react-router-dom";

import { useWorkspaceChrome } from "../../features/workspace/components/WorkspaceChromeContext";
import { isDemoModeEnabled } from "../../lib/api/mock";

const routeMeta = [
  {
    match: "/brand-profile",
    eyebrow: "Brand setup",
    title: "Shape the brand system",
    description: "Define the voice, mission, and positioning inputs that power strategy workflows.",
  },
  {
    match: "/audience-segments",
    eyebrow: "Audience mapping",
    title: "Map the audiences worth winning",
    description: "Keep customer segments explicit so planning flows can reason about platform and message fit.",
  },
  {
    match: "/strategy",
    eyebrow: "Strategy workspace",
    title: "Direct the next strategic run",
    description: "Review the latest strategy output and keep upcoming work grounded in one visible brief.",
  },
  {
    match: "/planning",
    eyebrow: "Planning board",
    title: "Translate strategy into a weekly cadence",
    description: "Preserve the founder-recognizable planning view while the clean backend contracts catch up.",
  },
  {
    match: "/review",
    eyebrow: "Review queue",
    title: "See what is ready for approval",
    description: "Keep execution and QA visible without recreating the legacy publishing chaos.",
  },
  {
    match: "/publishing",
    eyebrow: "Publishing queue",
    title: "Stage publish-ready work",
    description: "Prepare scheduling and demo publishing without external provider complexity.",
  },
  {
    match: "/intelligence",
    eyebrow: "Intelligence hub",
    title: "Analyze signals and specialist inputs",
    description: "A faithful operator-facing surface for trends, competitors, audience context, and copy cues.",
  },
];

export function TopBar() {
  const location = useLocation();
  const currentRoute = routeMeta.find((item) => location.pathname.includes(item.match)) ?? null;
  const {
    assistantCollapsed,
    toggleAssistant,
    openKnowledgeBase,
    openNotifications,
    openTrainModal,
    pushToast,
  } = useWorkspaceChrome();

  const actionButtons = [
    { label: "Knowledge Base", onClick: openKnowledgeBase },
    { label: "Train Model", onClick: openTrainModal },
    {
      label: isDemoModeEnabled() ? "Demo Mode" : "Run Analysis",
      onClick: () =>
        isDemoModeEnabled()
          ? pushToast("Demo mode is active. Local mock data will keep the UI complete.")
          : pushToast("Analysis run queued."),
    },
  ];

  return (
    <header className="flex items-center justify-between border-b border-white/5 bg-black/70 px-5 py-4 backdrop-blur lg:px-8">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-black shadow-[0_0_0_1px_rgba(255,255,255,0.04)]">
          #
        </div>
        <div className="max-w-2xl">
          <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">
            {currentRoute?.eyebrow ?? "Workspace overview"}
          </p>
          <h2 className="mt-1 text-lg font-semibold tracking-tight text-white">
            {currentRoute?.title ?? "Social operating system"}
          </h2>
          <p className="mt-2 hidden text-sm leading-6 text-white/55 lg:block">
            {currentRoute?.description ??
              "The new shell preserves the legacy product shape while every route stays typed, modular, and workspace-scoped."}
          </p>
        </div>
      </div>
      <div className="hidden items-center gap-3 lg:flex">
        {actionButtons.map((button) => (
          <button
            key={button.label}
            type="button"
            onClick={button.onClick}
            className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white/80 transition hover:bg-white/10 hover:text-white"
          >
            {button.label}
          </button>
        ))}
        <button
          type="button"
          onClick={openNotifications}
          className="flex h-10 w-10 items-center justify-center rounded-full border border-white/5 bg-white/5 text-sm text-white/45"
          title="Notifications"
        >
          N
        </button>
        <button
          type="button"
          onClick={toggleAssistant}
          className="flex h-10 w-10 items-center justify-center rounded-full border border-white/5 bg-white/5 text-sm text-white/45"
          title={assistantCollapsed ? "Open assistant" : "Collapse assistant"}
        >
          {assistantCollapsed ? "+" : "X"}
        </button>
      </div>
    </header>
  );
}
