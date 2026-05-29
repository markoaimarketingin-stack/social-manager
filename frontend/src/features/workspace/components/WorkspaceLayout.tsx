import { useEffect, useState } from "react";
import { Outlet, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../../features/auth/AuthContext";
import { AssistantPanel } from "../../../components/layout/AssistantPanel";
import { Sidebar } from "../../../components/layout/Sidebar";
import { ToastViewport, type ToastItem } from "../../../components/ui/ToastViewport";
import { WorkspaceChromeProvider } from "./WorkspaceChromeContext";
import { apiBaseUrl } from "../../../lib/api/client";

// Import modals
import { TrainModelModal } from "../../../components/modals/TrainModelModal";
import { KnowledgeBaseModal } from "../../../components/modals/KnowledgeBaseModal";
import { SettingsModal } from "../../../components/modals/SettingsModal";

export function WorkspaceLayout() {
  const { workspaceId = "" } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [assistantCollapsed, setAssistantCollapsed] = useState(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [connections, setConnections] = useState<Array<{platform: string; account_name: string}>>([]);
  
  // Modals state
  const [trainOpen, setTrainOpen] = useState(false);
  const [kbOpen, setKbOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const isDemoFallback = localStorage.getItem("demo_mode_fallback") === "true";

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

  useEffect(() => {
    const handleOpenSettings = () => setSettingsOpen(true);
    window.addEventListener("open-settings-modal", handleOpenSettings);
    return () => window.removeEventListener("open-settings-modal", handleOpenSettings);
  }, []);

  const handleLogout = () => {
    logout();
  };

  return (
    <WorkspaceChromeProvider
      value={{
        assistantCollapsed,
        openAssistant: () => setAssistantCollapsed(false),
        toggleAssistant: () => setAssistantCollapsed((c) => !c),
        openKnowledgeBase: () => setKbOpen(true),
        openTrainModal: () => setTrainOpen(true),
        openNotifications: () => {},
        pushToast,
      }}
    >
      <div className="flex h-screen w-screen flex-col overflow-hidden" style={{ background: "#06090e" }}>
        
        {/* Offline Demo Mode Banner */}
        {isDemoFallback && (
          <div
            className="flex items-center justify-between px-5 py-2 text-xs text-white/90 bg-[#238636]/90 backdrop-blur shrink-0 z-40 border-b border-[#21262d]"
          >
            <span>⚠️ Running in **Offline Demo Mode** (local backend port 8088 was unreachable). Simulated data is active.</span>
            <button
              onClick={() => {
                localStorage.removeItem("demo_mode_fallback");
                window.location.reload();
              }}
              className="px-2.5 py-0.5 rounded bg-white/20 hover:bg-white/30 text-white font-semibold transition-colors"
            >
              Reconnect to Backend
            </button>
          </div>
        )}

        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <aside
            className="hidden h-full shrink-0 lg:flex"
            style={{ width: "240px", background: "#06090e", borderRight: "1px solid #161b22" }}
          >
            <Sidebar
              workspaceId={workspaceId}
              user={user}
              connections={connections}
              onLogout={handleLogout}
              onGoConnect={() => navigate("/connect")}
              onOpenSettings={() => setSettingsOpen(true)}
            />
          </aside>

          {/* Main content */}
          <div className="relative flex h-full min-w-0 flex-1">
            <main className="flex min-h-0 flex-1">
              <section className="flex min-w-0 flex-1 flex-col overflow-hidden">
                {/* Top bar */}
                <div
                  className="flex h-12 shrink-0 items-center justify-between px-5 bg-[#06090e]"
                  style={{ borderBottom: "1px solid #161b22" }}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium" style={{ color: "#484f58" }}>
                      Workspace
                    </span>
                    <span className="text-xs" style={{ color: "#161b22" }}>/</span>
                    <span className="text-xs font-semibold" style={{ color: "#e6edf3" }}>
                      {user?.name || user?.email || "Dashboard"}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    {connections.length > 0 && (
                      <div className="flex items-center gap-1.5">
                        {connections.slice(0, 3).map((c) => (
                          <span
                            key={c.platform}
                            className="px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider"
                            style={{
                              background: "rgba(56,139,253,0.08)",
                              color: "#388bfd",
                              border: "1px solid rgba(56,139,253,0.15)",
                            }}
                          >
                            {c.platform}
                          </span>
                        ))}
                      </div>
                    )}
                    {/* Knowledge Base Button */}
                    <button
                      onClick={() => setKbOpen(true)}
                      className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all duration-200"
                      style={{ color: "#8b949e", border: "1px solid #21262d", background: "#0d1117" }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLElement).style.color = "#ffffff";
                        (e.currentTarget as HTMLElement).style.borderColor = "#30363d";
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLElement).style.color = "#8b949e";
                        (e.currentTarget as HTMLElement).style.borderColor = "#21262d";
                      }}
                    >
                      📚 Knowledge Base
                    </button>

                    {/* Train Model Button */}
                    <button
                      onClick={() => setTrainOpen(true)}
                      className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all duration-200"
                      style={{ color: "#8b949e", border: "1px solid #21262d", background: "#0d1117" }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLElement).style.color = "#ffffff";
                        (e.currentTarget as HTMLElement).style.borderColor = "#30363d";
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLElement).style.color = "#8b949e";
                        (e.currentTarget as HTMLElement).style.borderColor = "#21262d";
                      }}
                    >
                      🧠 Train Model
                    </button>

                    <button
                      onClick={() => setAssistantCollapsed((c) => !c)}
                      className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all duration-200"
                      style={{ color: "#8b949e", border: "1px solid #21262d", background: "#0d1117" }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLElement).style.color = "#ffffff";
                        (e.currentTarget as HTMLElement).style.borderColor = "#30363d";
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLElement).style.color = "#8b949e";
                        (e.currentTarget as HTMLElement).style.borderColor = "#21262d";
                      }}
                    >
                      <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current">
                        <path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2.5a1 1 0 0 0-.8.4L.5 14.5A.5.5 0 0 1 0 14V2z"/>
                      </svg>
                      AI Chat
                    </button>
                  </div>
                </div>

                <div className="shell-scroll flex-1 overflow-y-auto overflow-x-hidden" style={{ background: "#0d1117" }}>
                  <Outlet context={{ workspaceId }} />
                </div>
              </section>

              {/* Assistant panel */}
              {!assistantCollapsed && (
                <aside
                  className="hidden h-full shrink-0 xl:flex"
                  style={{ width: "320px", background: "#06090e", borderLeft: "1px solid #161b22" }}
                >
                  <AssistantPanel workspaceId={workspaceId} />
                </aside>
              )}
            </main>
          </div>

          {/* Collapsed assistant button */}
          {assistantCollapsed && (
            <div className="fixed bottom-5 right-5 z-40 animate-scaleIn">
              <button
                onClick={() => setAssistantCollapsed(false)}
                className="flex items-center gap-2 rounded-full px-4 py-2.5 text-sm font-semibold transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_4px_20px_rgba(31,111,235,0.4)]"
                style={{
                  background: "#1f6feb",
                  color: "#fff",
                  border: "1px solid rgba(255,255,255,0.1)",
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
      </div>

      {/* Global Modals */}
      <TrainModelModal isOpen={trainOpen} onClose={() => setTrainOpen(false)} />
      <KnowledgeBaseModal isOpen={kbOpen} onClose={() => setKbOpen(false)} />
      <SettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />

      <ToastViewport items={toasts} />
    </WorkspaceChromeProvider>
  );
}
