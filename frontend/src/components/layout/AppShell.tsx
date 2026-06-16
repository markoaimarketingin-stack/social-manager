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
        <div className="absolute left-[-7rem] top-[-7rem] h-56 w-56 rounded-full bg-[#000000] blur-3xl" />
        <div className="absolute right-[-5rem] top-16 h-64 w-64 rounded-full bg-white/[0.025] blur-3xl" />
      </div>
      <aside className="relative hidden h-full w-[236px] shrink-0 border-r border-white/[0.03] bg-black lg:flex">
        {sidebar}
      </aside>
      <div className="relative flex h-full min-w-0 flex-1">
        <main className="flex min-h-0 flex-1">
          <section className="flex min-w-0 flex-1 flex-col overflow-hidden">
            {topbar}
            <div className="shell-scroll flex-1 overflow-y-auto overflow-x-hidden">{children}</div>
          </section>
          {!assistantCollapsed ? (
            <aside className="hidden h-full w-[304px] shrink-0 border-l border-white/[0.04] bg-[#040404] xl:flex">
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
            className="flex items-center gap-3 rounded-full border border-white/10 bg-[#000000] px-5 py-3 text-sm font-semibold text-white shadow-[0_20px_60px_rgba(0,0,0,0.45)] backdrop-blur transition hover:scale-[1.02] hover:bg-[#050505]"
          >
            <span className="text-white/70">#</span>
            <span>Talk to assistant</span>
          </button>
        </div>
      ) : null}
    </div>
  );
}
