import type { PropsWithChildren, ReactNode } from "react";

type AppShellProps = PropsWithChildren<{
  sidebar: ReactNode;
  topbar: ReactNode;
  assistant: ReactNode;
  assistantCollapsed?: boolean;
  onOpenAssistant?: () => void;
}>;

export function AppShell({
  sidebar,
  topbar,
  assistant,
  children,
  assistantCollapsed = false,
  onOpenAssistant,
}: AppShellProps) {
  return (
    <div className="relative flex h-screen overflow-hidden bg-canvas text-ink">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-8rem] top-[-8rem] h-72 w-72 rounded-full bg-white/5 blur-3xl" />
        <div className="absolute right-[-6rem] top-20 h-80 w-80 rounded-full bg-glow/10 blur-3xl" />
      </div>
      <aside className="relative hidden h-full w-[280px] shrink-0 border-r border-line bg-[#020202]/95 lg:flex">
        {sidebar}
      </aside>
      <div className="relative flex h-full min-w-0 flex-1">
        <main className="flex min-h-0 flex-1">
          <section className="flex min-w-0 flex-1 flex-col overflow-hidden">
            {topbar}
            <div className="flex-1 overflow-hidden">{children}</div>
          </section>
          {!assistantCollapsed ? (
            <aside className="hidden h-full w-[300px] shrink-0 border-l border-line bg-[#040404]/90 xl:flex backdrop-blur-md">
              {assistant}
            </aside>
          ) : null}
        </main>
      </div>
      {assistantCollapsed ? (
        <div className="fixed bottom-6 right-6 z-40">
          <button
            type="button"
            onClick={onOpenAssistant}
            className="flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white shadow-[0_20px_60px_rgba(0,0,0,0.45)] backdrop-blur transition hover:scale-[1.02] hover:bg-white/10"
          >
            <span className="text-white/70">#</span>
            <span>Talk to assistant</span>
          </button>
        </div>
      ) : null}
    </div>
  );
}
