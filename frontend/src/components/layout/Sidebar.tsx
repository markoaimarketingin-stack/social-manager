import { NavLink } from "react-router-dom";

type SidebarIconKey =
  | "supervisor"
  | "dashboard"
  | "trends"
  | "competitors"
  | "segments"
  | "positioning"
  | "copywriter"
  | "ab"
  | "community"
  | "execution";

type NavigationItem = {
  label: string;
  to: string;
  icon: SidebarIconKey;
  end?: boolean;
  strong?: boolean;
};

const navigationGroups = (workspaceId: string): Array<{ title: string; items: NavigationItem[] }> => [
  {
    title: "Orchestrator",
    items: [
      { label: "Social Supervisor", to: `/workspaces/${workspaceId}/social-supervisor`, icon: "supervisor", end: true },
      { label: "Dashboard", to: `/workspaces/${workspaceId}/dashboard`, icon: "dashboard", strong: true },
    ],
  },
  {
    title: "Specialist Agents",
    items: [
      { label: "Trends", to: `/workspaces/${workspaceId}/trends`, icon: "trends" },
      { label: "Competitors", to: `/workspaces/${workspaceId}/competitors`, icon: "competitors" },
      { label: "Segments", to: `/workspaces/${workspaceId}/segments`, icon: "segments" },
      { label: "Positioning", to: `/workspaces/${workspaceId}/positioning`, icon: "positioning" },
      { label: "Copywriter", to: `/workspaces/${workspaceId}/copywriter`, icon: "copywriter" },
      { label: "A/B Copy Tester", to: `/workspaces/${workspaceId}/ab-copy-tester`, icon: "ab" },
      { label: "Community", to: `/workspaces/${workspaceId}/community`, icon: "community" },
    ],
  },
  {
    title: "Analysis",
    items: [{ label: "Execution history", to: `/workspaces/${workspaceId}/execution-history`, icon: "execution" }],
  },
];

function SidebarIcon({ icon, active }: { icon: SidebarIconKey; active: boolean }) {
  const className = active ? "text-white" : "text-[#8a8f99]";

  switch (icon) {
    case "supervisor":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="none">
          <path d="M8 10.5h8M9 6h6l-1 2.4V11l3.8 5.5c.5.8-.1 1.8-1.1 1.8H7.3c-1 0-1.6-1-1.1-1.8L10 11V8.4L9 6Z" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case "dashboard":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 4.8 4.7 10.5a.9.9 0 0 0 .5 1.6H7v5.1c0 .5.4.9.9.9h3.3v-4.3h1.6v4.3h3.3c.5 0 .9-.4.9-.9V12.1h1.8a.9.9 0 0 0 .5-1.6L12 4.8Z" />
        </svg>
      );
    case "trends":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="none">
          <path d="m5 15 4.2-4.2 3.2 3.2 5.6-5.6M14.5 8.4H18v3.5" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case "competitors":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="none">
          <path d="M5.5 6.5v11h13m-10-3.7 2.8-3 2.5 2 3.2-4.3" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case "segments":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 12.2a3.4 3.4 0 1 0 0-6.8 3.4 3.4 0 0 0 0 6.8Zm-6.5 4.5a3 3 0 0 1 3-3H9a5.7 5.7 0 0 0-3.5 5H3.9a1 1 0 0 1-1-1c0-2 1.6-3.5 3.6-3.5Zm10 2a5.7 5.7 0 0 0-3.5-5h.4a3 3 0 0 1 3 3c2 0 3.6 1.5 3.6 3.5a1 1 0 0 1-1 1H15.5Zm-8.2 0a4.7 4.7 0 0 1 9.4 0H7.3Z" />
        </svg>
      );
    case "positioning":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="7.5" stroke="currentColor" strokeWidth="1.7" />
          <circle cx="12" cy="12" r="3.3" stroke="currentColor" strokeWidth="1.7" />
          <circle cx="12" cy="12" r="1" fill="currentColor" />
        </svg>
      );
    case "copywriter":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="none">
          <path d="m5 19 3.8-1 8.3-8.3a1.9 1.9 0 1 0-2.8-2.8L6 15.2 5 19Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          <path d="m12.7 8.3 3 3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      );
    case "ab":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="none">
          <path d="M9 5v14M6 8h6M6.8 16h4.4M14 17l4-8 4 8M15.6 13.8h4.8" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case "community":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="none">
          <path d="M7.5 14.5c-1.7 0-3 1.3-3 3v.8h6v-.8c0-1.7-1.3-3-3-3Zm9 0c-1.7 0-3 1.3-3 3v.8h6v-.8c0-1.7-1.3-3-3-3ZM12 13a3.2 3.2 0 1 0 0-6.4A3.2 3.2 0 0 0 12 13Zm-4.7-.7a2.6 2.6 0 1 0 0-5.2 2.6 2.6 0 0 0 0 5.2Zm9.4 0a2.6 2.6 0 1 0 0-5.2 2.6 2.6 0 0 0 0 5.2Z" fill="currentColor" />
        </svg>
      );
    case "execution":
      return (
        <svg className={`h-[15px] w-[15px] ${className}`} viewBox="0 0 24 24" fill="none">
          <path d="M6 6v12h12M9 14l2.5-2.5 2 1.8 3.5-4.3" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
  }
}

export function Sidebar({ workspaceId }: { workspaceId: string }) {
  return (
    <div className="left-sidebar flex h-full w-full flex-col overflow-hidden px-4 py-4">
      <div className="border-b border-white/[0.045] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[0.5rem] bg-white/[0.04] p-1">
            <img src="/marko-ai-logo.png" alt="Marko AI" className="h-8 w-8 rounded-[0.3rem] object-cover" />
          </div>
          <div className="min-w-0">
            <p className="brand-title truncate text-[0.98rem] font-extrabold leading-tight text-white">
              Marko AI
            </p>
            <p className="mt-0.5 text-[9px] font-medium uppercase tracking-[0.26em] text-[#8ea7d4]">Orchestrator</p>
          </div>
        </div>
      </div>

      <nav className="scrollbar-thin mt-4 flex-1 overflow-y-auto space-y-4 pr-1">
        {navigationGroups(workspaceId).map((group) => (
          <div key={group.title}>
            <p className="mb-2 px-2 text-[9px] font-semibold uppercase tracking-[0.25em] text-[#7f93ba]">
              {group.title}
            </p>
            <div className="space-y-1.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.label}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    `group flex w-full items-center justify-between rounded-[999px] border px-3.5 py-[0.72rem] text-left text-[0.9rem] transition-all duration-150 ${
                      isActive
                        ? "border-white/[0.06] bg-white/[0.03] text-white"
                        : "border-transparent bg-transparent text-white/88 hover:border-white/[0.03] hover:bg-white/[0.02]"
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <span className="flex min-w-0 items-center gap-3">
                        <span className="flex h-5 w-5 shrink-0 items-center justify-center">
                          <SidebarIcon icon={item.icon} active={isActive} />
                        </span>
                        <span className={`truncate ${item.strong || isActive ? "font-semibold text-white" : "font-medium text-white/92"}`}>
                          {item.label}
                        </span>
                      </span>
                      <svg
                        className={`h-[12px] w-[12px] shrink-0 transition-colors ${isActive ? "text-white/28" : "text-white/18 group-hover:text-white/28"}`}
                        viewBox="0 0 24 24"
                        fill="none"
                      >
                        <path d="m9 6 6 6-6 6" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="mt-auto border-t border-white/[0.045] pt-3">
        <button
          type="button"
          className="mb-2.5 flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[10px] text-white/44 transition hover:bg-white/[0.03] hover:text-white/72"
        >
          <svg className="h-[13px] w-[13px] text-white/42" viewBox="0 0 24 24" fill="none">
            <path d="M8 7h8m0 0-2.5-2.5M16 7l-2.5 2.5M16 17H8m0 0 2.5-2.5M8 17l2.5 2.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span>Demo role:</span>
          <span className="font-semibold text-white">Manager</span>
        </button>

        <div className="flex items-center justify-between gap-3 rounded-lg bg-[#253146] px-3 py-2.5 text-left">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-[0.84rem] font-bold text-black">
              GU
            </div>
            <div className="min-w-0">
              <p className="truncate text-[0.9rem] font-semibold text-white">Guest User</p>
              <p className="truncate text-[10px] text-white/42">Free Plan</p>
            </div>
          </div>
          <button type="button" className="text-white/55 transition hover:text-white" aria-label="Open account settings">
            <svg className="h-[17px] w-[17px]" viewBox="0 0 24 24" fill="currentColor">
              <path d="m10.7 3.2.6 1.9c.2.5.6.9 1.1 1l2 .3c1 .2 1.4 1.4.7 2.1L14 9.9c-.4.4-.5 1-.4 1.5l.3 2c.2 1-.9 1.8-1.8 1.3l-1.8-1a1.7 1.7 0 0 0-1.6 0l-1.8 1c-.9.5-2-.3-1.8-1.3l.3-2c.1-.5 0-1.1-.4-1.5L3 8.5c-.7-.7-.3-1.9.7-2.1l2-.3c.5-.1.9-.5 1.1-1l.6-1.9c.3-1 1.7-1 2 0Zm.3 5.5a3.3 3.3 0 1 0 0 6.6 3.3 3.3 0 0 0 0-6.6Z" />
            </svg>
          </button>
        </div>

        <button
          type="button"
          className="mt-2.5 flex w-full items-center justify-center gap-2 rounded-[0.6rem] bg-[#374256] px-4 py-2.5 text-[0.88rem] font-semibold text-white transition hover:bg-[#44506a]"
        >
          <svg className="h-[15px] w-[15px]" viewBox="0 0 24 24" fill="none">
            <path d="M14 7h3.5A1.5 1.5 0 0 1 19 8.5v7a1.5 1.5 0 0 1-1.5 1.5H14M10 16l4-4-4-4M14 12H5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Logout
        </button>
      </div>
    </div>
  );
}
