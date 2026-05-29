import { NavLink } from "react-router-dom";

type SidebarProps = {
  workspaceId: string;
  user: { id: number; email: string; name: string } | null;
  connections: Array<{ platform: string; account_name: string }>;
  onLogout: () => void;
  onGoConnect: () => void;
  onOpenSettings?: () => void;
};

const NAV_GROUPS = (workspaceId: string) => [
  {
    title: "Orchestrator",
    items: [
      {
        label: "Supervisor",
        to: `/workspaces/${workspaceId}/dashboard`,
        icon: (
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
            <path d="M7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5zm4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5z"/>
          </svg>
        ),
      },
    ],
  },
  {
    title: "Agents",
    isNested: true,
    subgroups: [
      {
        title: "Audience & Market",
        items: [
          {
            label: "ICP Strategy",
            to: `/workspaces/${workspaceId}/segments`,
            icon: (
              <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
                <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1H7zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
                <path fillRule="evenodd" d="M5.216 14A2.238 2.238 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.325 6.325 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1h4.216z"/>
                <path d="M4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/>
              </svg>
            ),
          },
          {
            label: "Demand Landscape",
            to: `/workspaces/${workspaceId}/trends`,
            icon: (
              <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
              </svg>
            ),
          },
          {
            label: "Competitor Signals",
            to: `/workspaces/${workspaceId}/competitors`,
            icon: (
              <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                <path d="M4.285 9.567a.5.5 0 0 1 .683.183A3.498 3.498 0 0 0 8 11.5a3.498 3.498 0 0 0 3.032-1.75.5.5 0 1 1 .866.5A4.498 4.498 0 0 1 8 12.5a4.498 4.498 0 0 1-3.898-2.25.5.5 0 0 1 .183-.683z"/>
              </svg>
            ),
          },
          {
            label: "Market Expansion",
            to: `/workspaces/${workspaceId}/intelligence`,
            icon: (
              <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
                <path d="M0 0h1v15h15v1H0V0zm10 3.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-1 0V4.9l-3.613 4.417a.5.5 0 0 1-.74.037L7.06 6.767l-3.656 5.027a.5.5 0 0 1-.808-.588l4-5.5a.5.5 0 0 1 .758-.06l2.609 2.61L13.445 4H10.5a.5.5 0 0 1-.5-.5z"/>
              </svg>
            ),
          },
        ],
      },
      {
        title: "Offer & Creative",
        items: [
          {
            label: "Offer Strategy",
            to: `/workspaces/${workspaceId}/positioning`,
            icon: (
              <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
                <path d="M12.5 16a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm.5-5v1h1a.5.5 0 0 1 0 1h-1v1a.5.5 0 0 1-1 0v-1h-1a.5.5 0 0 1 0-1h1v-1a.5.5 0 0 1 1 0zm-2-6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/>
                <path d="M2 13c0 1 1 1 1 1h5.256A4.493 4.493 0 0 1 8 12.5a4.49 4.49 0 0 1 1.544-3.393C8.383 9.043 7.243 9 5 9c-4 0-5 3-5 4s1 1 1 1h1z"/>
              </svg>
            ),
          },
          {
            label: "Value Prop Messaging",
            to: `/workspaces/${workspaceId}/strategy`,
            icon: (
              <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
                <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
              </svg>
            ),
          },
        ],
      },
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
    : user?.email?.[0]?.toUpperCase() ?? "D";

  return (
    <div className="flex h-full w-full flex-col" style={{ background: "#06090e", color: "#e6edf3" }}>
      {/* Brand header */}
      <div
        className="flex items-center gap-3 px-5 py-4 shrink-0"
        style={{ borderBottom: "1px solid #161b22" }}
      >
        <div
          className="flex h-9 w-9 items-center justify-center rounded-xl text-white text-sm font-bold shrink-0 shadow-[0_0_15px_rgba(31,111,235,0.25)]"
          style={{ background: "linear-gradient(135deg, #1f6feb, #388bfd)", border: "1px solid rgba(255,255,255,0.1)" }}
        >
          M
        </div>
        <div>
          <p className="font-bold text-[1.05rem] tracking-wide" style={{ color: "#ffffff", lineHeight: 1.1 }}>
            MarkoAI
          </p>
          <p className="text-[9px] uppercase tracking-[0.25em]" style={{ color: "#388bfd" }}>
            Social Intelligence
          </p>
        </div>
      </div>

      {/* Connected platforms strip */}
      {connections.length > 0 && (
        <div
          className="px-5 py-2 flex flex-wrap gap-1.5 shrink-0 bg-white/[0.01]"
          style={{ borderBottom: "1px solid #161b22" }}
        >
          {connections.map((c) => {
            const colors: Record<string, string> = {
              linkedin: "#0077b5",
              instagram: "#e1306c",
              facebook: "#1877f2",
              x: "#e6edf3",
            };
            return (
              <span
                key={c.platform}
                className="px-2 py-0.5 rounded-full text-[9px] font-semibold uppercase tracking-wider"
                style={{
                  background: `${colors[c.platform] || "#555"}18`,
                  color: colors[c.platform] || "#8b949e",
                  border: `1px solid ${colors[c.platform] || "#555"}33`,
                }}
              >
                {c.platform}
              </span>
            );
          })}
        </div>
      )}

      {/* Navigation */}
      <nav className="scrollbar-none flex-1 overflow-y-auto py-4 px-3 space-y-5">
        {NAV_GROUPS(workspaceId).map((group) => (
          <div key={group.title} className="space-y-1.5">
            <p
              className="px-2.5 text-[10px] font-bold uppercase tracking-[0.2em]"
              style={{ color: "#484f58" }}
            >
              {group.title}
            </p>

            {group.isNested ? (
              <div className="space-y-4 pl-1">
                {group.subgroups?.map((sub) => (
                  <div key={sub.title} className="space-y-1">
                    <p
                      className="px-2 text-[9px] font-semibold uppercase tracking-wider text-white/35"
                    >
                      {sub.title}
                    </p>
                    <div className="space-y-0.5">
                      {sub.items.map((item) => (
                        <NavLink
                          key={item.label}
                          to={item.to}
                          className={({ isActive }) =>
                            `flex items-center gap-3 rounded-lg px-3 py-2 text-xs transition-all duration-200 no-underline ${
                              isActive
                                ? "text-white"
                                : "text-white/60 hover:text-white/90 hover:bg-white/[0.03]"
                            }`
                          }
                          style={({ isActive }) =>
                            isActive
                              ? {
                                  background: "rgba(31,111,235,0.1)",
                                  border: "1px solid rgba(31,111,235,0.25)",
                                  fontWeight: 600,
                                }
                              : {
                                  border: "1px solid transparent",
                                }
                          }
                        >
                          {({ isActive }) => (
                            <>
                              <span
                                style={{ color: isActive ? "#388bfd" : "#484f58" }}
                                className="shrink-0"
                              >
                                {item.icon}
                              </span>
                              <span className="truncate">{item.label}</span>
                            </>
                          )}
                        </NavLink>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-0.5 pl-1">
                {group.items?.map((item) => (
                  <NavLink
                    key={item.label}
                    to={item.to}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-lg px-3 py-2 text-xs transition-all duration-200 no-underline ${
                        isActive
                          ? "text-white"
                          : "text-white/60 hover:text-white/90 hover:bg-white/[0.03]"
                      }`
                    }
                    style={({ isActive }) =>
                      isActive
                        ? {
                            background: "rgba(31,111,235,0.1)",
                            border: "1px solid rgba(31,111,235,0.25)",
                            fontWeight: 600,
                          }
                        : {
                            border: "1px solid transparent",
                          }
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <span
                          style={{ color: isActive ? "#388bfd" : "#484f58" }}
                          className="shrink-0"
                        >
                          {item.icon}
                        </span>
                        <span className="truncate">{item.label}</span>
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="shrink-0 p-3 space-y-2 bg-[#03060a]" style={{ borderTop: "1px solid #161b22" }}>
        {/* Connect platforms button */}
        <button
          onClick={onGoConnect}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all duration-200"
          style={{
            background: "#238636",
            color: "#fff",
            border: "1px solid rgba(255,255,255,0.05)",
          }}
          onMouseEnter={(e) => { (e.target as HTMLElement).style.background = "#2ea043"; }}
          onMouseLeave={(e) => { (e.target as HTMLElement).style.background = "#238636"; }}
        >
          <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current shrink-0">
            <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
          </svg>
          {connections.length > 0 ? `Connections (${connections.length})` : "Connect Platforms"}
        </button>

        {/* User profile */}
        <div
          className="flex items-center gap-2 rounded-lg p-2"
          style={{ background: "#0d1117", border: "1px solid #161b22" }}
        >
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold shadow-[0_0_10px_rgba(56,139,253,0.15)]"
            style={{
              background: "linear-gradient(135deg, #388bfd, #1f6feb)",
              color: "#fff",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-semibold" style={{ color: "#ffffff" }}>
              {user?.name || "Demo Client"}
            </p>
            <p className="truncate text-[10px]" style={{ color: "#6e7681" }}>
              {user?.email || "Pro Plan"}
            </p>
          </div>
          <button
            onClick={onOpenSettings}
            className="shrink-0 p-1.5 rounded-md hover:bg-white/5 transition-colors"
            title="Settings & Models"
            style={{ color: "#8b949e" }}
          >
            <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
              <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.17.311c.58.287.58 1.13 0 1.417l-.17.31c-.699 1.283.705 2.686 1.987 1.987l.311-.17a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.17-.311a1.464 1.464 0 0 1 0-1.417l.17-.31c.699-1.283-.705-2.686-1.987-1.987l-.311.17a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.86z"/>
            </svg>
          </button>
          <button
            onClick={onLogout}
            className="shrink-0 p-1.5 rounded-md hover:bg-white/5 transition-colors"
            title="Sign out"
            style={{ color: "#8b949e" }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = "#f85149"; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = "#8b949e"; }}
          >
            <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
              <path fillRule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2a1.5 1.5 0 0 0-1.5-1.5h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
              <path fillRule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
