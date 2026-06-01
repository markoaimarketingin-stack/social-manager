import { NavLink } from "react-router-dom";
import { PLATFORM_WORKSPACES } from "../../features/platforms/platformWorkspaces";

type SidebarProps = {
  workspaceId: string;
  user: { id: number; email: string; name: string } | null;
  connections: Array<{ platform: string; account_name: string }>;
  onLogout: () => void;
  onGoConnect: () => void;
  onOpenSettings?: () => void;
};

type NavItem = {
  label: string;
  to: string;
  icon: string;
};

const NAV_GROUPS = (workspaceId: string): Array<{ title: string; items: NavItem[] }> => [
  {
    title: "Orchestrator",
    items: [
      { label: "Social Supervisor", to: `/workspaces/${workspaceId}/dashboard`, icon: "♜" },
      { label: "Dashboard", to: `/workspaces/${workspaceId}/publishing`, icon: "⌂" },
    ],
  },
  {
    title: "Channel Workspaces",
    items: PLATFORM_WORKSPACES.map((platform) => ({
      label: platform.label,
      to: `/workspaces/${workspaceId}/${platform.route}`,
      icon: platform.shortLabel,
    })),
  },
  {
    title: "Specialist Agents",
    items: [
      { label: "Trends", to: `/workspaces/${workspaceId}/trends`, icon: "⌁" },
      { label: "Competitors", to: `/workspaces/${workspaceId}/competitors`, icon: "⌙" },
      { label: "Segments", to: `/workspaces/${workspaceId}/segments`, icon: "♟" },
      { label: "Positioning", to: `/workspaces/${workspaceId}/positioning`, icon: "◎" },
      { label: "Copywriter", to: `/workspaces/${workspaceId}/copywriter`, icon: "✎" },
      { label: "A/B Copy Tester", to: `/workspaces/${workspaceId}/ab-copy-tester`, icon: "⚗" },
      { label: "Community", to: `/workspaces/${workspaceId}/community`, icon: "☁" },
    ],
  },
  {
    title: "Analysis",
    items: [
      { label: "Execution history", to: `/workspaces/${workspaceId}/execution-history`, icon: "▥" },
    ],
  },
];

export function Sidebar({
  workspaceId,
  user,
  connections,
  onLogout,
  onGoConnect,
  onOpenSettings,
}: SidebarProps) {
  const initials = user?.name
    ? user.name.split(" ").map((namePart) => namePart[0]).join("").toUpperCase().slice(0, 2)
    : user?.email?.[0]?.toUpperCase() ?? "GU";

  return (
    <div className="flex h-full w-full flex-col bg-black text-white">
      <div className="shrink-0 px-5 pb-5 pt-5">
        <div className="flex items-center gap-4">
          <div className="flex h-[60px] w-[60px] items-center justify-center rounded-md border border-white/5 bg-[#050505] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)]">
            <div className="flex h-11 w-11 items-center justify-center rounded-md border border-white/10 bg-[#111] text-2xl">
              ⚙
            </div>
          </div>
          <div>
            <p className="text-2xl font-black leading-none tracking-tight">Marko AI</p>
            <p className="mt-1 text-[11px] font-semibold uppercase tracking-[0.28em] text-[#9cc9ff]">
              Orchestrator
            </p>
          </div>
        </div>
      </div>

      <div className="h-px shrink-0 bg-[#1f2937] mx-5" />

      <nav className="shell-scroll flex-1 space-y-6 overflow-y-auto px-5 py-5">
        {NAV_GROUPS(workspaceId).map((group) => (
          <div key={group.title} className="space-y-3">
            <p className="px-2 text-[12px] font-bold uppercase tracking-[0.28em] text-[#9cc9ff]/80">
              {group.title}
            </p>

            <div className="space-y-2">
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `group flex h-[57px] items-center justify-between rounded-full border px-6 py-4 text-base no-underline transition-all duration-200 ${
                      isActive
                        ? "border-[#0d6efd]/45 bg-[#020b17] text-white shadow-[inset_0_0_0_1px_rgba(13,110,253,0.16)]"
                        : "border-white/[0.04] bg-black text-white hover:border-white/10 hover:bg-[#080808]"
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <span className="flex min-w-0 items-center gap-4">
                        <span
                          className={`flex h-5 w-5 shrink-0 items-center justify-center text-sm font-black ${
                            isActive ? "text-[#58a6ff]" : "text-[#b8c7d9]"
                          }`}
                        >
                          {item.icon}
                        </span>
                        <span className="truncate font-medium">{item.label}</span>
                      </span>
                      <span className={`text-3xl leading-none ${isActive ? "text-white/35" : "text-white/20 group-hover:text-white/35"}`}>
                        ›
                      </span>
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="shrink-0 border-t border-[#1f2937] px-5 py-4">
        {connections.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-1.5">
            {connections.map((connection) => (
              <span key={connection.platform} className="rounded-full border border-white/10 bg-white/[0.03] px-2 py-1 text-[10px] font-bold uppercase text-white/55">
                {connection.platform}
              </span>
            ))}
          </div>
        )}

        <button
          onClick={onGoConnect}
          className="mb-4 flex w-full items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-bold text-white transition hover:bg-white/[0.08]"
        >
          + Connect Platforms
        </button>

        <div className="mb-3 flex items-center gap-2 text-xs text-[#93a4ba]">
          <span>↔</span>
          <span>Demo role:</span>
          <span className="font-bold text-white">Manager</span>
        </div>

        <div className="flex items-center gap-3 rounded-lg bg-[#1f2937] px-4 py-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-white text-sm font-black text-black">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-base font-bold">{user?.name || "Guest User"}</p>
            <p className="truncate text-xs text-white/45">{user?.email || "Free Plan"}</p>
          </div>
          <button onClick={onOpenSettings} className="text-xl text-white/60 hover:text-white" title="Settings">
            ⚙
          </button>
        </div>

        <button
          onClick={onLogout}
          className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-[#334155] px-4 py-3 text-sm font-bold text-white transition hover:bg-[#475569]"
        >
          ↪ Logout
        </button>
      </div>
    </div>
  );
}
