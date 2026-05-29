import { NavLink } from "react-router-dom";

type SidebarProps = {
  workspaceId: string;
  user: { id: number; email: string; name: string } | null;
  connections: Array<{ platform: string; account_name: string }>;
  onLogout: () => void;
  onGoConnect: () => void;
};

const PLATFORM_COLORS: Record<string, string> = {
  linkedin: "#0077b5",
  instagram: "#e1306c",
  facebook: "#1877f2",
  x: "#555",
};

const NAV_GROUPS = (workspaceId: string) => [
  {
    title: "Overview",
    items: [
      {
        label: "Dashboard",
        to: `/workspaces/${workspaceId}/dashboard`,
        icon: (
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
            <path d="M0 1.5A1.5 1.5 0 0 1 1.5 0h2A1.5 1.5 0 0 1 5 1.5v2A1.5 1.5 0 0 1 3.5 5h-2A1.5 1.5 0 0 1 0 3.5v-2zm5.5 0A1.5 1.5 0 0 1 7 0h2a1.5 1.5 0 0 1 1.5 1.5v2A1.5 1.5 0 0 1 9 5H7a1.5 1.5 0 0 1-1.5-1.5v-2zm5.5 0A1.5 1.5 0 0 1 12.5 0h2A1.5 1.5 0 0 1 16 1.5v2A1.5 1.5 0 0 1 14.5 5h-2A1.5 1.5 0 0 1 11 3.5v-2zM0 7a1.5 1.5 0 0 1 1.5-1.5h2A1.5 1.5 0 0 1 5 7v2A1.5 1.5 0 0 1 3.5 10.5h-2A1.5 1.5 0 0 1 0 9V7zm5.5 0A1.5 1.5 0 0 1 7 5.5h2A1.5 1.5 0 0 1 10.5 7v2A1.5 1.5 0 0 1 9 10.5H7A1.5 1.5 0 0 1 5.5 9V7zm5.5 0A1.5 1.5 0 0 1 12.5 5.5h2A1.5 1.5 0 0 1 16 7v2a1.5 1.5 0 0 1-1.5 1.5h-2A1.5 1.5 0 0 1 11 9V7zM0 12.5A1.5 1.5 0 0 1 1.5 11h2A1.5 1.5 0 0 1 5 12.5v2A1.5 1.5 0 0 1 3.5 16h-2A1.5 1.5 0 0 1 0 14.5v-2zm5.5 0A1.5 1.5 0 0 1 7 11h2a1.5 1.5 0 0 1 1.5 1.5v2A1.5 1.5 0 0 1 9 16H7a1.5 1.5 0 0 1-1.5-1.5v-2zm5.5 0A1.5 1.5 0 0 1 12.5 11h2a1.5 1.5 0 0 1 1.5 1.5v2a1.5 1.5 0 0 1-1.5 1.5h-2a1.5 1.5 0 0 1-1.5-1.5v-2z"/>
          </svg>
        ),
      },
    ],
  },
  {
    title: "Specialist Agents",
    items: [
      {
        label: "Trends",
        to: `/workspaces/${workspaceId}/trends`,
        icon: (
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
            <path d="M0 0h1v15h15v1H0V0zm10 3.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-1 0V4.9l-3.613 4.417a.5.5 0 0 1-.74.037L7.06 6.767l-3.656 5.027a.5.5 0 0 1-.808-.588l4-5.5a.5.5 0 0 1 .758-.06l2.609 2.61L13.445 4H10.5a.5.5 0 0 1-.5-.5z"/>
          </svg>
        ),
      },
      {
        label: "Competitors",
        to: `/workspaces/${workspaceId}/competitors`,
        icon: (
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
            <path d="M4.285 9.567a.5.5 0 0 1 .683.183A3.498 3.498 0 0 0 8 11.5a3.498 3.498 0 0 0 3.032-1.75.5.5 0 1 1 .866.5A4.498 4.498 0 0 1 8 12.5a4.498 4.498 0 0 1-3.898-2.25.5.5 0 0 1 .183-.683zM7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5zm4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5z"/>
          </svg>
        ),
      },
      {
        label: "Audience",
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
        label: "Brand Profile",
        to: `/workspaces/${workspaceId}/brand-profile`,
        icon: (
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
            <path d="M8 0C3.58 0 0 3.58 0 8s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zm0 14a6 6 0 1 1 0-12A6 6 0 0 1 8 14zm1-9H7v4h2V5zm0 5H7v2h2v-2z"/>
          </svg>
        ),
      },
      {
        label: "Copywriter",
        to: `/workspaces/${workspaceId}/copywriter`,
        icon: (
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
            <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
            <path fillRule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>
          </svg>
        ),
      },
      {
        label: "A/B Testing",
        to: `/workspaces/${workspaceId}/ab-copy-tester`,
        icon: (
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
            <path d="M5.5 0a.5.5 0 0 1 .5.5v8.5a1 1 0 0 0 1 1h7a.5.5 0 0 1 0 1h-7A2 2 0 0 1 5 8.5V.5a.5.5 0 0 1 .5-.5z"/>
            <path d="M2.5 3A2.5 2.5 0 0 0 0 5.5v8A2.5 2.5 0 0 0 2.5 16h8A2.5 2.5 0 0 0 13 13.5v-8A2.5 2.5 0 0 0 10.5 3h-8z"/>
          </svg>
        ),
      },
      {
        label: "Community",
        to: `/workspaces/${workspaceId}/community`,
        icon: (
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
            <path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2.5a1 1 0 0 0-.8.4L.5 14.5A.5.5 0 0 1 0 14V2z"/>
          </svg>
        ),
      },
    ],
  },
  {
    title: "Analysis",
    items: [
      {
        label: "Post History",
        to: `/workspaces/${workspaceId}/execution-history`,
        icon: (
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
            <path d="M8.515 1.019A7 7 0 0 0 8 1V0a8 8 0 0 1 .589.022l-.074.997zm2.004.45a7.003 7.003 0 0 0-.985-.299l.219-.976c.383.086.76.2 1.126.342l-.36.933zm1.37.71a7.01 7.01 0 0 0-.439-.27l.493-.87a8.025 8.025 0 0 1 .979.654l-.615.789a6.996 6.996 0 0 0-.418-.302zm1.834 1.79a6.99 6.99 0 0 0-.653-.796l.724-.69c.27.285.52.59.747.91l-.818.576zm.744 1.352a7.08 7.08 0 0 0-.214-.468l.893-.45a7.976 7.976 0 0 1 .45 1.088l-.95.313a7.023 7.023 0 0 0-.179-.483zm.53 2.507a6.991 6.991 0 0 0-.1-1.025l.985-.17c.067.386.106.778.116 1.17l-1 .025zm-.131 1.538c.033-.17.06-.339.081-.51l.993.123a7.957 7.957 0 0 1-.23 1.155l-.964-.267c.046-.165.086-.332.12-.501zm-.952 2.379c.184-.29.346-.594.486-.908l.914.405c-.16.36-.345.706-.555 1.038l-.845-.535zm-.964 1.205c.122-.122.239-.248.35-.378l.758.653a8.073 8.073 0 0 1-.401.432l-.707-.707z"/>
            <path d="M8 1a7 7 0 1 0 4.95 11.95l.707.707A8.001 8.001 0 1 1 8 0v1z"/>
            <path d="M7.5 3a.5.5 0 0 1 .5.5v5.21l3.248 1.856a.5.5 0 0 1-.496.868l-3.5-2A.5.5 0 0 1 7 9V3.5a.5.5 0 0 1 .5-.5z"/>
          </svg>
        ),
      },
    ],
  },
];

export function Sidebar({ workspaceId, user, connections, onLogout, onGoConnect }: SidebarProps) {
  const initials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : user?.email?.[0]?.toUpperCase() ?? "?";

  return (
    <div
      className="flex h-full w-full flex-col"
      style={{ color: "#e6edf3" }}
    >
      {/* Brand header */}
      <div
        className="flex items-center gap-3 px-4 py-3 shrink-0"
        style={{ borderBottom: "1px solid #21262d" }}
      >
        <div
          className="flex h-8 w-8 items-center justify-center rounded-md text-white text-xs font-bold shrink-0"
          style={{ background: "linear-gradient(135deg, #1f6feb, #388bfd)" }}
        >
          SM
        </div>
        <div>
          <p className="font-semibold text-sm" style={{ color: "#e6edf3", lineHeight: 1.2 }}>
            Social Manager
          </p>
          <p className="text-xs" style={{ color: "#388bfd" }}>AI-Powered</p>
        </div>
      </div>

      {/* Connected platforms strip */}
      {connections.length > 0 && (
        <div
          className="px-4 py-2 flex flex-wrap gap-1 shrink-0"
          style={{ borderBottom: "1px solid #21262d" }}
        >
          {connections.map((c) => (
            <span
              key={c.platform}
              className="px-2 py-0.5 rounded-full text-xs font-medium"
              style={{
                background: `${PLATFORM_COLORS[c.platform] || "#555"}22`,
                color: PLATFORM_COLORS[c.platform] || "#8b949e",
                border: `1px solid ${PLATFORM_COLORS[c.platform] || "#555"}44`,
              }}
            >
              {c.platform}
            </span>
          ))}
        </div>
      )}

      {/* Navigation */}
      <nav className="scrollbar-thin flex-1 overflow-y-auto py-2 px-2">
        {NAV_GROUPS(workspaceId).map((group) => (
          <div key={group.title} className="mb-4">
            <p
              className="px-2 pb-1 text-xs font-semibold uppercase tracking-wider"
              style={{ color: "#484f58" }}
            >
              {group.title}
            </p>
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.label}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-sm transition-colors no-underline ${
                      isActive
                        ? "text-blue-400"
                        : "text-gray-400 hover:text-gray-200 hover:bg-white/5"
                    }`
                  }
                  style={({ isActive }) =>
                    isActive
                      ? { background: "rgba(31,111,235,0.15)", color: "#388bfd" }
                      : {}
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
                      <span className="truncate font-medium">{item.label}</span>
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="shrink-0 p-3 space-y-2" style={{ borderTop: "1px solid #21262d" }}>
        {/* Connect platforms button */}
        <button
          onClick={onGoConnect}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium transition-colors"
          style={{ background: "#238636", color: "#fff" }}
          onMouseEnter={(e) => { (e.target as HTMLElement).style.background = "#2ea043"; }}
          onMouseLeave={(e) => { (e.target as HTMLElement).style.background = "#238636"; }}
        >
          <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current shrink-0">
            <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
          </svg>
          {connections.length > 0 ? `Manage Connections (${connections.length})` : "Connect Platforms"}
        </button>

        {/* User profile */}
        <div
          className="flex items-center gap-3 rounded-md px-3 py-2"
          style={{ background: "#21262d" }}
        >
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold"
            style={{ background: "#388bfd", color: "#fff" }}
          >
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium" style={{ color: "#e6edf3" }}>
              {user?.name || "User"}
            </p>
            <p className="truncate text-xs" style={{ color: "#484f58" }}>
              {user?.email}
            </p>
          </div>
          <button
            onClick={onLogout}
            className="shrink-0 p-1 rounded transition-colors"
            title="Sign out"
            style={{ color: "#484f58" }}
            onMouseEnter={(e) => { (e.target as HTMLElement).style.color = "#f85149"; }}
            onMouseLeave={(e) => { (e.target as HTMLElement).style.color = "#484f58"; }}
          >
            <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
              <path fillRule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
              <path fillRule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
