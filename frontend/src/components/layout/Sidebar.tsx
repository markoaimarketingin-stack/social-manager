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

/* ── SVG Icons (18×18 size, matched to PM dashboard icons) ─────────────────── */
const IC = {
  grid: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <rect x="3.5" y="4" width="7" height="7" rx="1.5" />
      <rect x="13.5" y="4" width="7" height="4.5" rx="1.5" />
      <rect x="13.5" y="11.5" width="7" height="8.5" rx="1.5" />
      <rect x="3.5" y="14" width="7" height="6" rx="1.5" />
    </svg>
  ),
  bars: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <path d="M4 7.5h16" strokeLinecap="round" />
      <path d="M7.5 4v16" strokeLinecap="round" />
      <path d="M11 11h7" strokeLinecap="round" />
      <path d="M11 15h5" strokeLinecap="round" />
      <rect x="4" y="4" width="16" height="16" rx="2.5" />
    </svg>
  ),
  doc: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M14 2v6h6" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 13H8M16 17H8M10 9H8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  trend: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <path d="M4 16l5-5 4 4 7-8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 7h4v4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  target: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" />
    </svg>
  ),
  users: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <circle cx="9" cy="7" r="4" />
      <path d="M2 20c0-3.3 2.7-6 6-6h2c3.3 0 6 2.7 6 6" strokeLinecap="round" />
      <circle cx="18" cy="9" r="3" />
      <path d="M14 17.5c0-2.2 1.8-4 4-4h1" strokeLinecap="round" />
    </svg>
  ),
  pen: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" strokeLinecap="round" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4z" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  flask: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <path d="M9 3h6M10 3v6.5L6 18a1.5 1.5 0 0 0 1.5 2h9a1.5 1.5 0 0 0 1.5-2L14 9.5V3" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M8.5 14h7" strokeLinecap="round" />
    </svg>
  ),
  chat: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <path d="M8 10h8M8 14h5m-8 6 3.6-3H19a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2v3Z" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  upload: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[18px] w-[18px]">
      <path d="M4 12h11" strokeLinecap="round" />
      <path d="M11.5 5 19 12l-7.5 7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M4 5v14" strokeLinecap="round" />
    </svg>
  ),
  settings: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33 1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82 1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  logout: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
};

const NAV_GROUPS = (wid: string): Array<{ title: string; items: NavItem[] }> => [
  {
    title: "TASK WORKSPACES",
    items: [
      { label: "Dashboard", to: `/workspaces/${wid}/dashboard`, icon: IC.grid },
      { label: "Content Studio", to: `/workspaces/${wid}/copywriter`, icon: IC.pen },
      { label: "Approval Inbox", to: `/workspaces/${wid}/ab-copy-tester`, icon: IC.flask },
      { label: "Publishing Calendar", to: `/workspaces/${wid}/community`, icon: IC.chat },
      { label: "Analytics Center", to: `/workspaces/${wid}/trends`, icon: IC.trend },
      { label: "Brand Settings", to: `/workspaces/${wid}/brand-profile`, icon: IC.settings },
    ],
  },
];

export function Sidebar({ workspaceId, user, onLogout, onOpenSettings }: SidebarProps) {
  const initials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : user?.email?.split("@")[0]?.slice(0, 2).toUpperCase() ?? "GU";

  const displayName = user?.name || user?.email?.split("@")[0] || "User";

  return (
    <aside
      className="flex h-full w-full shrink-0 flex-col text-[0.86rem]"
      style={{ backgroundColor: "#050505" }}
    >
      {/* Branding matches PM */}
      <div className="flex items-center gap-[12px] px-[24px] pt-7 pb-8">
        <img
          src="/marko%20ai.png"
          alt="Marko AI"
          className="h-11 w-11 object-contain"
        />
        <div
          style={{
            color: "#ffffff",
            fontSize: "22px",
            fontWeight: 700,
            lineHeight: 1,
            letterSpacing: "-0.02em",
          }}
        >
          Marko AI
        </div>
      </div>

      {/* Navigation sections */}
      <nav className="flex-1 overflow-y-auto pl-[24px] pr-[20px] scrollbar-thin">
        {NAV_GROUPS(workspaceId).map((group, groupIndex) => (
          <div key={group.title} className={groupIndex > 0 ? "mt-[36px]" : "mt-2"}>
            <p
              style={{
                color: "rgba(255,255,255,0.48)",
                fontSize: "11px",
                fontWeight: 700,
                letterSpacing: "0.24em",
                textTransform: "uppercase",
                paddingLeft: "0px",
                marginBottom: "14px",
              }}
            >
              {group.title}
            </p>
            <div className="flex flex-col gap-[12px]">
              {group.items.map(({ label, to, icon }) => {
                // If it is active
                const isDashboard = label === "Dashboard";

                return (
                  <NavLink
                    key={to}
                    to={to}
                    className="group flex w-full items-center transition-all duration-150"
                  >
                    {({ isActive }) => {
                      const isActiveDashboard = isDashboard && isActive;
                      return (
                        <div
                          className="flex w-full items-center"
                          style={{
                            height: isActiveDashboard ? "60px" : "52px",
                            backgroundColor: isActiveDashboard
                              ? "rgba(255,255,255,0.06)"
                              : isActive
                              ? "rgba(255,255,255,0.06)"
                              : "transparent",
                            borderRadius: isActiveDashboard ? "16px" : "14px",
                            border: isActive
                              ? "1px solid rgba(255,255,255,0.10)"
                              : "1px solid transparent",
                            boxShadow: isActiveDashboard ? "0 12px 30px rgba(0,0,0,0.28)" : "none",
                            paddingLeft: "18px",
                            paddingRight: "16px",
                            color: "#ffffff",
                            fontSize: "14px",
                            fontWeight: 600,
                            letterSpacing: "-0.008em",
                            lineHeight: "18px",
                            display: "flex",
                            alignItems: "center",
                            gap: "14px",
                          }}
                        >
                          <span
                            className="flex h-[24px] w-[24px] shrink-0 items-center justify-center"
                            style={{
                              color: isActive ? "#ffffff" : "rgba(255,255,255,0.58)",
                            }}
                          >
                            {icon}
                          </span>
                          <span
                            className="flex-1 text-left text-[0.88rem]"
                            style={{
                              color: isActive ? "#ffffff" : "rgba(255,255,255,0.58)",
                            }}
                          >
                            {label}
                          </span>
                          <svg
                            className="ml-auto h-4 w-4 shrink-0 transition-all duration-150"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth={1.75}
                            style={{
                              color: isActive ? "#ffffff" : "rgba(255,255,255,0.35)",
                              transform: isActive ? "translateX(2px)" : "none",
                            }}
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      );
                    }}
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* User footer matches PM */}
      <div
        className="px-5 py-6"
        style={{
          borderTop: "1px solid rgba(255,255,255,0.08)",
        }}
      >
        <div className="flex items-center gap-3">
          <div
            className="grid shrink-0 place-items-center rounded-full"
            style={{
              width: "36px",
              height: "36px",
              backgroundColor: "#151515",
              border: "1px solid rgba(255,255,255,0.1)",
              color: "#ffffff",
              fontSize: "12px",
              fontWeight: 800,
            }}
          >
            {initials}
          </div>
          <div className="flex-1 min-w-0">
            <div className="truncate text-[14px] font-bold text-white">
              {displayName}
            </div>
            <div className="text-[11px] text-zinc-400 font-medium">Free Plan</div>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={onOpenSettings}
              className="p-1.5 rounded-md text-zinc-500 hover:text-white hover:bg-[#000000] transition-all"
              aria-label="Settings"
              title="Settings"
            >
              {IC.settings}
            </button>
            <button
              type="button"
              onClick={onLogout}
              className="p-1.5 rounded-md text-zinc-500 hover:text-white hover:bg-[#000000] transition-all"
              aria-label="Logout"
              title="Logout"
            >
              {IC.logout}
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}
