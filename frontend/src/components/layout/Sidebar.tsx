import { NavLink } from "react-router-dom";

const navigationGroups = (workspaceId: string) => [
  {
    title: "Command Center",
    items: [
      { label: "Overview", to: `/workspaces/${workspaceId}`, icon: "OV" },
      { label: "Intelligence", to: `/workspaces/${workspaceId}/intelligence`, icon: "IN" },
      { label: "Strategy", to: `/workspaces/${workspaceId}/strategy`, icon: "ST" },
      { label: "Planning", to: `/workspaces/${workspaceId}/planning`, icon: "PL" },
      { label: "Review Queue", to: `/workspaces/${workspaceId}/review`, icon: "RV" },
      { label: "Publishing", to: `/workspaces/${workspaceId}/publishing`, icon: "PQ" },
    ],
  },
  {
    title: "Configuration",
    items: [
      { label: "Audience Segments", to: `/workspaces/${workspaceId}/audience-segments`, icon: "AS" },
      { label: "Brand Profile", to: `/workspaces/${workspaceId}/brand-profile`, icon: "BP" },
    ],
  },
];

export function Sidebar({ workspaceId }: { workspaceId: string }) {
  return (
    <div className="left-sidebar flex h-full w-full flex-col overflow-hidden px-5 py-6">
      <div className="border-b border-white/5 pb-6">
        <div className="flex items-center gap-3 px-1">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-black/50 shadow-inset">
            <svg className="w-5 h-5 text-white/90" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
          </div>
          <div>
            <p className="brand-title font-sans text-base font-bold tracking-tight text-white/95">
              Social OS
            </p>
            <p className="text-[10px] uppercase tracking-widest text-white/40 font-medium mt-0.5">Workspace</p>
          </div>
        </div>
      </div>

      <nav className="scrollbar-thin mt-6 flex-1 overflow-y-auto pr-2 space-y-8">
        {navigationGroups(workspaceId).map((group) => (
          <div key={group.title}>
            <p className="mb-3 px-2 text-[10px] font-bold uppercase tracking-[0.25em] text-white/30">
              {group.title}
            </p>
            <div className="space-y-1">
              {group.items.map((item) => (
                <NavLink
                  key={item.label}
                  to={item.to}
                  end={item.to.endsWith(workspaceId)}
                  className={({ isActive }) =>
                    `group flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm transition-all duration-200 ${
                      isActive
                        ? "bg-white/10 text-white shadow-sm"
                        : "text-white/60 hover:bg-white/[0.04] hover:text-white/90"
                    }`
                  }
                >
                  <span className="flex items-center gap-3">
                    <span className="flex h-6 w-6 items-center justify-center rounded-md border border-white/5 bg-white/[0.02] text-[9px] font-bold text-white/50 transition-colors group-hover:bg-white/10 group-hover:text-white/80 group-[.active]:border-white/10 group-[.active]:bg-white/15 group-[.active]:text-white">
                      {item.icon}
                    </span>
                    <span className="font-medium">{item.label}</span>
                  </span>
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="mt-auto border-t border-white/5 pt-5 pb-2">
        <button type="button" className="w-full user-card flex items-center justify-between gap-3 rounded-2xl bg-white/[0.03] border border-white/5 px-3 py-3 transition-all hover:bg-white/[0.06] hover:-translate-y-0.5 active:translate-y-0 active:scale-95 text-left">
          <div className="flex items-center gap-3">
            <div className="relative user-badge flex h-9 w-9 items-center justify-center rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-bold border border-indigo-500/30">
              DU
              <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-500 border-2 border-black"></span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-semibold text-white/90">Demo User</p>
              <p className="truncate text-[10px] text-white/40 font-medium">Session Active</p>
            </div>
          </div>
          <svg className="w-4 h-4 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l4-4 4 4m0 6l-4 4-4-4" /></svg>
        </button>
      </div>
    </div>
  );
}
