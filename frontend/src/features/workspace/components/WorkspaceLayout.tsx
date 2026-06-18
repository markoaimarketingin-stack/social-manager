import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../../features/auth/AuthContext";
import { AssistantPanel } from "../../../components/layout/AssistantPanel";
import { Sidebar } from "../../../components/layout/Sidebar";
import { ToastViewport, type ToastItem } from "../../../components/ui/ToastViewport";
import { WorkspaceChromeProvider } from "./WorkspaceChromeContext";
import { apiFetch } from "../../../lib/api/client";

import { TrainModelModal } from "../../../components/modals/TrainModelModal";
import { KnowledgeBaseModal } from "../../../components/modals/KnowledgeBaseModal";
import { SettingsModal } from "../../../components/modals/SettingsModal";

const PAGE_TITLES: Record<string, { title: string; subtitle: string; icon: string }> = {
  dashboard: { title: "Social Supervisor", subtitle: "Orchestrator", icon: "♜" },
  publishing: { title: "Dashboard", subtitle: "Command Center", icon: "⌂" },
  trends: { title: "Trends", subtitle: "Agent", icon: "⌁" },
  competitors: { title: "Competitors", subtitle: "Agent", icon: "⌙" },
  segments: { title: "Audience Segments", subtitle: "Agent", icon: "♟" },
  positioning: { title: "Positioning", subtitle: "Agent", icon: "◎" },
  "brand-profile": { title: "Brand Profile", subtitle: "Agent", icon: "ⓘ" },
  copywriter: { title: "Copywriter", subtitle: "Agent", icon: "✎" },
  "ab-copy-tester": { title: "A/B Copy Tester", subtitle: "Agent", icon: "⚗" },
  community: { title: "Community", subtitle: "Agent", icon: "☁" },
  "execution-history": { title: "Execution History", subtitle: "Analysis", icon: "▥" },
  instagram: { title: "Instagram", subtitle: "Channel Workspace", icon: "IG" },
  facebook: { title: "Facebook Page", subtitle: "Channel Workspace", icon: "FB" },
  linkedin: { title: "LinkedIn", subtitle: "Channel Workspace", icon: "IN" },
  x: { title: "X / Twitter", subtitle: "Channel Workspace", icon: "X" },
  youtube: { title: "YouTube", subtitle: "Channel Workspace", icon: "YT" },
};

const SIDEBAR_MIN_WIDTH = 200;
const SIDEBAR_MAX_WIDTH = 380;
const ASSISTANT_MIN_WIDTH = 300;
const ASSISTANT_MAX_WIDTH = 520;

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function getStoredWidth(key: string, fallback: number, min: number, max: number) {
  const stored = Number(localStorage.getItem(key));
  return Number.isFinite(stored) && stored > 0 ? clamp(stored, min, max) : fallback;
}

export function WorkspaceLayout() {
  const { workspaceId = "" } = useParams();
  const location = useLocation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [assistantCollapsed, setAssistantCollapsed] = useState(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [connections, setConnections] = useState<Array<{ platform: string; account_name: string }>>([]);
  const [trainOpen, setTrainOpen] = useState(false);
  const [kbOpen, setKbOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(() =>
    getStoredWidth("marko_sidebar_width", 230, SIDEBAR_MIN_WIDTH, SIDEBAR_MAX_WIDTH),
  );
  const [assistantWidth, setAssistantWidth] = useState(() =>
    getStoredWidth("marko_assistant_width", 340, ASSISTANT_MIN_WIDTH, ASSISTANT_MAX_WIDTH),
  );

  const currentSegment = location.pathname.split("/").filter(Boolean).at(-1) ?? "dashboard";
  const page = PAGE_TITLES[currentSegment] ?? PAGE_TITLES.dashboard;

  useEffect(() => {
    apiFetch("/api/auth/connections")
      .then((response) => (response.ok ? response.json() : []))
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

  const startSidebarResize = (event: React.PointerEvent<HTMLDivElement>) => {
    event.preventDefault();
    const startX = event.clientX;
    const startWidth = sidebarWidth;
    let finalWidth = startWidth;

    const handleMove = (moveEvent: PointerEvent) => {
      const nextWidth = clamp(startWidth + moveEvent.clientX - startX, SIDEBAR_MIN_WIDTH, SIDEBAR_MAX_WIDTH);
      finalWidth = nextWidth;
      setSidebarWidth(nextWidth);
    };

    const handleUp = () => {
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      window.removeEventListener("pointermove", handleMove);
      window.removeEventListener("pointerup", handleUp);
      localStorage.setItem("marko_sidebar_width", String(finalWidth));
    };

    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    window.addEventListener("pointermove", handleMove);
    window.addEventListener("pointerup", handleUp);
  };

  const startAssistantResize = (event: React.PointerEvent<HTMLDivElement>) => {
    event.preventDefault();
    const startX = event.clientX;
    const startWidth = assistantWidth;
    let finalWidth = startWidth;

    const handleMove = (moveEvent: PointerEvent) => {
      const nextWidth = clamp(startWidth + startX - moveEvent.clientX, ASSISTANT_MIN_WIDTH, ASSISTANT_MAX_WIDTH);
      finalWidth = nextWidth;
      setAssistantWidth(nextWidth);
    };

    const handleUp = () => {
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      window.removeEventListener("pointermove", handleMove);
      window.removeEventListener("pointerup", handleUp);
      localStorage.setItem("marko_assistant_width", String(finalWidth));
    };

    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    window.addEventListener("pointermove", handleMove);
    window.addEventListener("pointerup", handleUp);
  };

  return (
    <WorkspaceChromeProvider
      value={{
        assistantCollapsed,
        openAssistant: () => setAssistantCollapsed(false),
        toggleAssistant: () => setAssistantCollapsed((collapsed) => !collapsed),
        openKnowledgeBase: () => setKbOpen(true),
        openTrainModal: () => setTrainOpen(true),
        openNotifications: () => {},
        pushToast,
      }}
    >
      <div className="flex h-screen w-screen overflow-hidden text-white" style={{ background: "#000000" }}>
        <aside className="hidden h-full shrink-0 lg:flex" style={{ width: sidebarWidth, background: "#050505", borderRight: "1px solid rgba(255,255,255,0.08)" }}>
          <Sidebar
            workspaceId={workspaceId}
            user={user}
            connections={connections}
            onLogout={logout}
            onGoConnect={() => navigate("/connect")}
            onOpenSettings={() => setSettingsOpen(true)}
          />
        </aside>

        <div
          role="separator"
          aria-label="Resize sidebar"
          aria-orientation="vertical"
          onPointerDown={startSidebarResize}
          className="group hidden h-full w-2 shrink-0 cursor-col-resize items-stretch justify-center bg-black lg:flex"
          title="Drag to resize sidebar"
        >
          <div className="h-full w-px bg-[#000000] transition group-hover:w-1 group-hover:bg-[#388bfd]" />
        </div>

        <section className="flex min-w-0 flex-1 flex-col overflow-hidden" style={{ background: "#000000" }}>
          {/* TopBar — matches Performance Marketer style exactly */}
          <header
            className="flex min-h-[88px] shrink-0 items-center justify-between gap-4 border-b border-[rgba(255,255,255,0.08)] bg-[#000000] pl-[24px] pr-[24px]"
          >
            {/* Left: page title and symbol icon */}
            <div className="flex min-w-0 items-center gap-[14px]">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center">
                <img
                  src="/symboll.png"
                  alt="Supervisor"
                  className="h-[22px] w-[22px] object-contain opacity-100"
                />
              </div>
              <div className="flex min-w-0 flex-col leading-tight">
                <h2
                  style={{
                    fontSize: "24px",
                    lineHeight: "28px",
                    fontWeight: 800,
                    color: "#ffffff",
                    letterSpacing: "-0.035em",
                  }}
                >
                  {page.title}
                </h2>
                <p
                  style={{
                    fontSize: "15px",
                    lineHeight: "18px",
                    fontWeight: 400,
                    color: "rgba(255,255,255,0.62)",
                    marginTop: "3px",
                  }}
                >
                  {page.subtitle}
                </p>
              </div>
            </div>

            {/* Right: pill action buttons matching PM agent-top-bar */}
            <div className="hidden items-center gap-4 lg:flex">
              <div className="ml-auto flex items-center justify-end gap-[18px]">
                <button
                  type="button"
                  className="flex h-[31px] items-center gap-[7px] whitespace-nowrap rounded-full border border-[rgba(255,255,255,0.08)] bg-[#000000] px-[12px] text-[13px] font-semibold leading-[16px] text-white transition hover:bg-[rgba(255,255,255,0.05)] btn-press"
                  onClick={() => setKbOpen(true)}
                >
                  <svg className="h-[15px] w-[15px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  Knowledge Base
                </button>

                <button
                  type="button"
                  className="flex h-[31px] items-center gap-[7px] whitespace-nowrap rounded-full border border-[rgba(255,255,255,0.08)] bg-[#000000] px-[12px] text-[13px] font-semibold leading-[16px] text-white transition hover:bg-[rgba(255,255,255,0.05)] btn-press"
                  onClick={() => setTrainOpen(true)}
                >
                  <svg className="h-[15px] w-[15px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  Train Model
                </button>



                <button
                  type="button"
                  className="flex h-[34px] items-center gap-[8px] rounded-full border border-[rgba(255,255,255,0.08)] bg-[#000000] px-[14px] text-[14px] font-semibold leading-[18px] text-white transition hover:bg-[rgba(255,255,255,0.05)] btn-press"
                  onClick={() => navigate(`/workspaces/${workspaceId}/dashboard`)}
                >
                  <svg
                    className="h-[15px] w-[15px]"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path d="M5 3l14 9-14 9V3z" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  Run Analysis
                </button>
              </div>
            </div>
          </header>

          <div className="shell-scroll flex-1 overflow-y-auto overflow-x-hidden" style={{ background: "#000000" }}>
            <Outlet context={{ workspaceId }} />
          </div>
        </section>

        {!assistantCollapsed && (
          <>
            <div
              role="separator"
              aria-label="Resize assistant"
              aria-orientation="vertical"
              onPointerDown={startAssistantResize}
              className="group hidden h-full w-2 shrink-0 cursor-col-resize items-stretch justify-center bg-black xl:flex"
              title="Drag to resize assistant"
            >
              <div className="h-full w-px bg-[#000000] transition group-hover:w-1 group-hover:bg-[#388bfd]" />
            </div>
            <aside className="hidden h-full shrink-0 bg-black xl:flex" style={{ width: assistantWidth }}>
              <AssistantPanel workspaceId={workspaceId} />
            </aside>
          </>
        )}

        {assistantCollapsed && (
          <div className="fixed bottom-5 right-5 z-40">
            <button
              onClick={() => setAssistantCollapsed(false)}
              className="rounded-full border border-white/10 bg-[#000000] px-5 py-3 text-sm font-semibold text-white shadow-[0_20px_60px_rgba(0,0,0,0.45)] hover:scale-[1.02] hover:bg-[#050505] active:scale-95 transition-all duration-150"
            >
              Open Assistant
            </button>
          </div>
        )}
      </div>

      <TrainModelModal
        isOpen={trainOpen}
        onClose={() => setTrainOpen(false)}
        onSuccess={() => {
          pushToast("Model trained successfully with new document!");
          window.dispatchEvent(new Event("document-uploaded"));
        }}
      />
      <KnowledgeBaseModal isOpen={kbOpen} onClose={() => setKbOpen(false)} />
      <SettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
      <ToastViewport items={toasts} />
    </WorkspaceChromeProvider>
  );
}
