import { useWorkspaceChrome } from "../../features/workspace/components/WorkspaceChromeContext";

export function TopBar() {
  const {
    openKnowledgeBase,
    openTrainModal,
    pushToast,
  } = useWorkspaceChrome();

  const actionButtons = [
    { label: "Knowledge Base", onClick: openKnowledgeBase },
    { label: "Train Model", onClick: openTrainModal },
    { label: "Refresh", onClick: () => window.location.reload() },
    { label: "Run Analysis", onClick: () => pushToast("Analysis run queued.") },
  ];

  return (
    <header className="flex h-[4.9rem] shrink-0 items-center justify-between border-b border-white/[0.04] bg-black px-5 lg:px-6">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black shadow-[0_0_0_1px_rgba(255,255,255,0.04)]">
          <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
            <path d="M5 13.2 9 17l10-10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div className="max-w-xl">
          <h2 className="text-[0.98rem] font-semibold text-white md:text-[1.02rem]">Supervisor</h2>
          <p className="text-[9px] uppercase tracking-[0.32em] text-white/38">Orchestrator</p>
        </div>
      </div>
      <div className="hidden items-center gap-2 lg:flex">
        {actionButtons.map((button) => (
          <button
            key={button.label}
            type="button"
            onClick={button.onClick}
            className="rounded-full border border-white/[0.08] bg-white/[0.04] px-3.5 py-2 text-[11px] font-medium text-white/78 transition hover:bg-white/[0.08] hover:text-white"
          >
            {button.label}
          </button>
        ))}
      </div>
    </header>
  );
}
