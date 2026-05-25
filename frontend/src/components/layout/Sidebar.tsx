import { NavLink } from "react-router-dom";

const navigationGroups = (workspaceId: string) => [
  {
    title: "Orchestrator",
    items: [
      { label: "Social Supervisor", to: `/workspaces/${workspaceId}`, icon: "SV" },
      { label: "Dashboard", to: `/workspaces/${workspaceId}`, icon: "DB" },
    ],
  },
  {
    title: "Specialist Agents",
    items: [
      { label: "Trends", to: `/workspaces/${workspaceId}/intelligence`, icon: "TR" },
      { label: "Competitors", to: `/workspaces/${workspaceId}/intelligence`, icon: "CP" },
      { label: "Segments", to: `/workspaces/${workspaceId}/audience-segments`, icon: "SG" },
      { label: "Positioning", to: `/workspaces/${workspaceId}/brand-profile`, icon: "BP" },
      { label: "Copywriter", to: `/workspaces/${workspaceId}/strategy`, icon: "CW" },
      { label: "A/B Copy Tester", to: `/workspaces/${workspaceId}/planning`, icon: "AB" },
      { label: "Community", to: `/workspaces/${workspaceId}/review`, icon: "CM" },
    ],
  },
  {
    title: "Analysis",
    items: [{ label: "Execution history", to: `/workspaces/${workspaceId}/publishing`, icon: "EX" }],
  },
  {
    title: "Command Center",
    items: [
      { label: "Strategy Workspace", to: `/workspaces/${workspaceId}/strategy`, icon: "ST" },
      { label: "Planning", to: `/workspaces/${workspaceId}/planning`, icon: "PL" },
      { label: "Review Queue", to: `/workspaces/${workspaceId}/review`, icon: "RV" },
      { label: "Publishing Queue", to: `/workspaces/${workspaceId}/publishing`, icon: "PQ" },
    ],
  },
];

export function Sidebar({ workspaceId }: { workspaceId: string }) {
  return (
    <div className="left-sidebar flex h-full w-full flex-col overflow-hidden px-4 py-4">
      <div className="border-b border-white/5 px-2 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-black shadow-inset">
            <img src="/favicon.svg" alt="Marko AI" className="h-8 w-8 object-contain" />
          </div>
          <div>
            <p className="brand-title font-['Space_Grotesk'] text-lg font-bold tracking-tight text-white">
              Marko AI
            </p>
          </div>
        </div>
      </div>

      <nav className="scrollbar-thin mt-6 flex-1 overflow-y-auto pr-2">
        {navigationGroups(workspaceId).map((group, groupIndex) => (
          <div key={group.title} className={groupIndex === 0 ? "" : "mt-6"}>
            <p className="mb-3 px-2 text-[10px] font-semibold uppercase tracking-[0.35em] text-white/35">
              {group.title}
            </p>
            <div className="space-y-2">
              {group.items.map((item) => (
                <NavLink
                  key={item.label}
                  to={item.to}
                  end={item.to.endsWith(workspaceId)}
                  className={({ isActive }) =>
                    `flex w-full items-center justify-between rounded-xl border px-3 py-3 text-left text-sm transition ${
                      isActive
                        ? "border-white/8 bg-white/8 text-white"
                        : "border-transparent text-white/75 hover:border-white/8 hover:bg-white/5 hover:text-white"
                    }`
                  }
                >
                  <span className="flex items-center">
                    <span className="mr-3 text-white/18">&rsaquo;</span>
                    <span className="mr-3 inline-flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/[0.03] text-[10px] font-semibold text-white/72">
                      {item.icon}
                    </span>
                    <span>{item.label}</span>
                  </span>
                  <span className="text-[10px] text-white/20">&rsaquo;</span>
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="mt-auto border-t border-white/5 pt-4">
        <button
          type="button"
          className="mb-3 flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-[11px] text-white/45 transition hover:bg-white/5 hover:text-white/75"
        >
          <span>Demo role:</span>
          <span className="font-semibold text-white capitalize">manager</span>
        </button>
        <div className="user-card flex items-center gap-3 rounded-2xl bg-white/6 px-3 py-3">
          <div className="user-badge flex h-10 w-10 items-center justify-center rounded-full bg-sky-500 text-sm font-bold text-white">
            DU
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-white">Demo User</p>
            <p className="truncate text-[11px] text-white/40">demo@example.com</p>
          </div>
        </div>
        <button
          type="button"
          className="logout-btn mt-3 flex w-full items-center justify-center gap-2 rounded-2xl bg-white/12 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/16"
        >
          Log out
        </button>
      </div>
    </div>
  );
}
