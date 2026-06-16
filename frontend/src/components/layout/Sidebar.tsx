import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

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
  icon: ReactNode;
};

// SVG Icons matching the performance marketer style
const Icons = {
  supervisor: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <rect x="3" y="3" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
      <rect x="11" y="3" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
      <rect x="3" y="11" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
      <rect x="11" y="11" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
    </svg>
  ),
  dashboard: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <path d="M3 5h14M3 10h14M3 15h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  trends: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <path d="M3 14l4-4 3 3 4-5 3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  competitors: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <circle cx="7" cy="10" r="4" stroke="currentColor" strokeWidth="1.5"/>
      <circle cx="13" cy="10" r="4" stroke="currentColor" strokeWidth="1.5"/>
    </svg>
  ),
  segments: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M10 3v7l5 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  positioning: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <circle cx="10" cy="10" r="3" stroke="currentColor" strokeWidth="1.5"/>
      <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5"/>
    </svg>
  ),
  copywriter: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <path d="M4 6h12M4 10h8M4 14h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M14 12l2 2-2 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  abtest: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <path d="M4 14l3-8 3 8M5.5 11h4M13 6v8M11 9l2-3 2 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  community: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="1.5"/>
      <circle cx="14" cy="12" r="2.5" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M3 17c0-2.5 2-4 5-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  publish: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <path d="M10 3v10M6 7l4-4 4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M4 15h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  history: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M10 6v4l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  brand: (
    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
      <path d="M10 3l1.8 5.4H17l-4.6 3.3 1.8 5.4L10 14.2l-4.2 2.9 1.8-5.4L3 8.4h5.2L10 3z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
    </svg>
  ),
};

const NAV_GROUPS = (workspaceId: string): Array<{ title: string; items: NavItem[] }> => [
  {
    title: "Orchestrator",
    items: [
      { label: "Social Supervisor", to: `/workspaces/${workspaceId}/dashboard`, icon: Icons.supervisor },
      { label: "Dashboard", to: `/workspaces/${workspaceId}/publishing`, icon: Icons.dashboard },
    ],
  },
  {
    title: "Specialist Agents",
    items: [
      { label: "Trends", to: `/workspaces/${workspaceId}/trends`, icon: Icons.trends },
      { label: "Competitors", to: `/workspaces/${workspaceId}/competitors`, icon: Icons.competitors },
      { label: "Segments", to: `/workspaces/${workspaceId}/segments`, icon: Icons.segments },
      { label: "Positioning", to: `/workspaces/${workspaceId}/positioning`, icon: Icons.positioning },
      { label: "Copywriter", to: `/workspaces/${workspaceId}/copywriter`, icon: Icons.copywriter },
      { label: "A/B Copy Tester", to: `/workspaces/${workspaceId}/ab-copy-tester`, icon: Icons.abtest },
      { label: "Community", to: `/workspaces/${workspaceId}/community`, icon: Icons.community },
    ],
  },
  {
    title: "Operations",
    items: [
      { label: "Publish ads campaign", to: `/workspaces/${workspaceId}/brand-profile`, icon: Icons.publish },
      { label: "Execution history", to: `/workspaces/${workspaceId}/execution-history`, icon: Icons.history },
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
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : user?.email?.[0]?.toUpperCase() ?? "GU";

  return (
    <div className="flex h-full w-full flex-col" style={{ background: "#0a0a0a", color: "#e2e8f0" }}>
      {/* Brand Header */}
      <div className="shrink-0 px-4 py-4">
        <div className="flex items-center gap-3">
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white"
            style={{ background: "linear-gradient(135deg, #1f6feb 0%, #388bfd 100%)", border: "1px solid rgba(56,139,253,0.3)" }}
          >
            <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4">
              <path d="M10 2L2 7l8 5 8-5-8-5zM2 13l8 5 8-5M2 10l8 5 8-5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <p className="text-sm font-bold leading-none text-white">Marko AI</p>
            <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.2em]" style={{ color: "#388bfd" }}>
              Social Manager
            </p>
          </div>
        </div>
      </div>

      <div className="mx-4 h-px shrink-0" style={{ background: "rgba(255,255,255,0.05)" }} />

      {/* Navigation */}
      <nav className="shell-scroll flex-1 overflow-y-auto px-3 py-3">
        {NAV_GROUPS(workspaceId).map((group) => (
          <div key={group.title} className="mb-5">
            <p
              className="mb-2 px-2 text-[10px] font-bold uppercase tracking-[0.22em]"
              style={{ color: "rgba(148,163,184,0.6)" }}
            >
              {group.title}
            </p>

            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `group flex h-9 items-center justify-between rounded-md px-3 text-sm no-underline transition-all duration-150 ${
                      isActive
                        ? "bg-[#0d1f3c] text-white"
                        : "text-[#8b9aa8] hover:bg-white/[0.04] hover:text-[#c9d5e0]"
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <span className="flex min-w-0 items-center gap-2.5">
                        <span
                          className="shrink-0 transition-colors"
                          style={{ color: isActive ? "#388bfd" : "currentColor" }}
                        >
                          {item.icon}
                        </span>
                        <span className="truncate font-medium text-[13px]">{item.label}</span>
                      </span>
                      <span
                        className="shrink-0 text-base leading-none transition-colors"
                        style={{ color: isActive ? "rgba(255,255,255,0.4)" : "rgba(255,255,255,0.15)" }}
                      >
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

      {/* Bottom Section */}
      <div className="shrink-0 px-3 pb-3" style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>
        {/* Connected Platforms */}
        {connections.length > 0 && (
          <div className="py-2 flex flex-wrap gap-1">
            {connections.map((c) => (
              <span
                key={c.platform}
                className="rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider"
                style={{ background: "rgba(255,255,255,0.05)", color: "rgba(255,255,255,0.4)", border: "1px solid rgba(255,255,255,0.08)" }}
              >
                {c.platform}
              </span>
            ))}
          </div>
        )}

        {/* Connect Button */}
        <button
          onClick={onGoConnect}
          className="mb-3 mt-2 flex w-full items-center justify-center gap-1.5 rounded-md py-2 text-xs font-semibold transition-colors"
          style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", color: "rgba(255,255,255,0.6)" }}
        >
          <span>+</span>
          <span>Connect Platforms</span>
        </button>

        {/* User Profile */}
        <div
          className="flex items-center gap-2.5 rounded-md px-3 py-2.5"
          style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div
            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold text-black"
            style={{ background: "linear-gradient(135deg, #e2e8f0, #cbd5e1)" }}
          >
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-semibold text-white leading-tight">{user?.name || "Guest User"}</p>
            <p className="truncate text-[10px] leading-tight" style={{ color: "rgba(255,255,255,0.35)" }}>
              {user?.email || "Free Plan"}
            </p>
          </div>
          <button
            onClick={onOpenSettings}
            className="shrink-0 transition-colors hover:text-white"
            style={{ color: "rgba(255,255,255,0.4)" }}
            title="Settings"
          >
            <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5">
              <path d="M8 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M12.7 8a4.8 4.8 0 0 0-.1-.9l1.4-1.1a.3.3 0 0 0 .1-.4l-1.4-2.4a.3.3 0 0 0-.4-.1l-1.7.7a5 5 0 0 0-.8-.4L9.5 2a.3.3 0 0 0-.3-.3H6.8A.3.3 0 0 0 6.5 2L6.3 3.8a5 5 0 0 0-.8.4l-1.7-.7a.3.3 0 0 0-.4.1L2 5.9a.3.3 0 0 0 .1.4L3.4 7.4a4.8 4.8 0 0 0-.1.9 4.8 4.8 0 0 0 .1.9L2 10.3a.3.3 0 0 0-.1.4L3.3 13a.3.3 0 0 0 .4.1l1.7-.7a5 5 0 0 0 .8.4l.2 1.8c0 .2.2.3.3.3h2.5c.2 0 .3-.1.3-.3l.2-1.8a5 5 0 0 0 .8-.4l1.7.7a.3.3 0 0 0 .4-.1l1.3-2.3a.3.3 0 0 0-.1-.4L12.7 9a4.8 4.8 0 0 0 .1-.9z" stroke="currentColor" strokeWidth="1.2"/>
            </svg>
          </button>
          <button
            onClick={onLogout}
            className="shrink-0 transition-colors hover:text-white"
            style={{ color: "rgba(255,255,255,0.4)" }}
            title="Logout"
          >
            <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5">
              <path d="M6 14H3a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1h3M11 11l3-3-3-3M14 8H6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
