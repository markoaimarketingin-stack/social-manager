import { useEffect, useRef, useState } from "react";
import { Outlet, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../../features/auth/AuthContext";
import { AssistantPanel } from "../../../components/layout/AssistantPanel";
import { Sidebar } from "../../../components/layout/Sidebar";
import { ToastViewport, type ToastItem } from "../../../components/ui/ToastViewport";
import { WorkspaceChromeProvider } from "./WorkspaceChromeContext";
import { apiBaseUrl } from "../../../lib/api/client";

export function WorkspaceLayout() {
  const { workspaceId = "" } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [assistantCollapsed, setAssistantCollapsed] = useState(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [connections, setConnections] = useState<Array<{platform: string; account_name: string}>>([]);

  // Fetch user's connected platforms
  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) return;
    fetch(`${apiBaseUrl}/api/auth/connections`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.ok ? r.json() : [])
      .then(setConnections)
      .catch(console.error);
  }, []);

  const pushToast = (message: string) => {
    const nextToast = { id: `${Date.now()}-${Math.random()}`, message };
    setToasts((current) => [...current, nextToast]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((item) => item.id !== nextToast.id));
    }, 3000);
  };

  useEffect(() => {
    setAssistantCollapsed(false);
  }, [workspaceId]);

  const handleLogout = () => {
    logout();
  };

  return (
    <WorkspaceChromeProvider
      value={{
        assistantCollapsed,
        openAssistant: () => setAssistantCollapsed(false),
        toggleAssistant: () => setAssistantCollapsed((c) => !c),
        openKnowledgeBase: () => {},
        openTrainModal: () => {},
        openNotifications: () => {},
        pushToast,
      }}
    >
      <div className="relative flex h-screen overflow-hidden" style={{ background: "#0d1117" }}>
        {/* Sidebar */}
        <aside
          className="hidden h-full shrink-0 lg:flex"
          style={{ width: "240px", background: "#161b22", borderRight: "1px solid #21262d" }}
        >
          <Sidebar
            workspaceId={workspaceId}
            user={user}
            connections={connections}
            onLogout={handleLogout}
            onGoConnect={() => navigate("/connect")}
          />
        </aside>

        {/* Main content */}
        <div className="relative flex h-full min-w-0 flex-1">
          <main className="flex min-h-0 flex-1">
            <section className="flex min-w-0 flex-1 flex-col overflow-hidden">
              {/* Top bar */}
              <div
                className="flex h-10 shrink-0 items-center justify-between px-4"
                style={{ borderBottom: "1px solid #21262d", background: "#161b22" }}
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium" style={{ color: "#6e7681" }}>
                    Workspace
                  </span>
                  <span className="text-xs" style={{ color: "#30363d" }}>/</span>
                  <span className="text-xs font-medium" style={{ color: "#8b949e" }}>
                    {user?.name || user?.email || "Dashboard"}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  {connections.length > 0 && (
                    <div className="flex items-center gap-1.5">
                      {connections.slice(0, 3).map((c) => (
                        <span
                          key={c.platform}
                          className="px-2 py-0.5 rounded-full text-xs font-medium"
                          style={{
                            background: "rgba(56,139,253,0.1)",
                            color: "#388bfd",
                            border: "1px solid rgba(56,139,253,0.2)",
                          }}
                        >
                          {c.platform}
                        </span>
                      ))}
                    </div>
                  )}
                  <button
                    onClick={() => setAssistantCollapsed((c) => !c)}
                    className="flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-colors"
                    style={{ color: "#6e7681", border: "1px solid #21262d" }}
                    onMouseEnter={(e) => { (e.target as HTMLElement).style.color = "#8b949e"; }}
                    onMouseLeave={(e) => { (e.target as HTMLElement).style.color = "#6e7681"; }}
                  >
                    <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current">
                      <path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2.5a1 1 0 0 0-.8.4L.5 14.5A.5.5 0 0 1 0 14V2z"/>
                    </svg>
                    AI Chat
                  </button>
                </div>
              </div>

              <div className="shell-scroll flex-1 overflow-y-auto overflow-x-hidden">
                <Outlet context={{ workspaceId }} />
              </div>
            </section>

            {/* Assistant panel */}
            {!assistantCollapsed && (
              <aside
                className="hidden h-full shrink-0 xl:flex"
                style={{ width: "320px", background: "#161b22", borderLeft: "1px solid #21262d" }}
              >
                <AssistantPanel workspaceId={workspaceId} />
              </aside>
            )}
          </main>
        </div>

        {/* Collapsed assistant button */}
        {assistantCollapsed && (
          <div className="fixed bottom-5 right-5 z-40">
            <button
              onClick={() => setAssistantCollapsed(false)}
              className="flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all"
              style={{
                background: "#1f6feb",
                color: "#fff",
                boxShadow: "0 4px 20px rgba(31,111,235,0.4)",
              }}
            >
              <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
                <path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2.5a1 1 0 0 0-.8.4L.5 14.5A.5.5 0 0 1 0 14V2z"/>
              </svg>
              AI Agent
            </button>
          </div>
        )}
      </div>

      <ToastViewport items={toasts} />
    </WorkspaceChromeProvider>
  );
}
