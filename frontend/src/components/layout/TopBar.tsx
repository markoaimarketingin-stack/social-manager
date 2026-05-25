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
    <header className="flex items-center justify-between border-b border-white/5 bg-black/70 px-5 py-4 backdrop-blur lg:px-8">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-black shadow-[0_0_0_1px_rgba(255,255,255,0.04)]">
          #
        </div>
        <div className="max-w-xl">
          <h2 className="text-base font-semibold tracking-tight text-white md:text-lg">Supervisor</h2>
          <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Orchestrator</p>
        </div>
      </div>
      <div className="hidden items-center gap-2 lg:flex">
        {actionButtons.map((button) => (
          <button
            key={button.label}
            type="button"
            onClick={button.onClick}
            className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-medium text-white/80 transition hover:bg-white/10 hover:text-white"
          >
            {button.label}
          </button>
        ))}
      </div>
    </header>
  );
}
