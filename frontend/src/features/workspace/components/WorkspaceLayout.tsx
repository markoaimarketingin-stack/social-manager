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

const SIDEBAR_MIN_WIDTH = 280;
const SIDEBAR_MAX_WIDTH = 460;
const ASSISTANT_MIN_WIDTH = 320;
const ASSISTANT_MAX_WIDTH = 560;

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
    getStoredWidth("marko_sidebar_width", 340, SIDEBAR_MIN_WIDTH, SIDEBAR_MAX_WIDTH),
  );
  const [assistantWidth, setAssistantWidth] = useState(() =>
    getStoredWidth("marko_assistant_width", 400, ASSISTANT_MIN_WIDTH, ASSISTANT_MAX_WIDTH),
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
      <div className="flex h-screen w-screen overflow-hidden bg-black text-white">
        <aside className="hidden h-full shrink-0 bg-black lg:flex" style={{ width: sidebarWidth }}>
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
          <div className="h-full w-px bg-[#111827] transition group-hover:w-1 group-hover:bg-[#388bfd]" />
        </div>

        <section className="flex min-w-0 flex-1 flex-col overflow-hidden bg-black">
          <header className="flex h-20 shrink-0 items-center justify-between border-b border-[#080808] bg-black px-7">
            <div className="flex w-[260px] shrink-0 items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white text-lg font-black text-black">
                {page.icon}
              </div>
              <div className="min-w-0">
                <h1 className="truncate whitespace-nowrap text-xl font-black leading-none text-white">{page.title}</h1>
                <p className="mt-1 text-sm text-white/55">{page.subtitle}</p>
              </div>
            </div>

            <div className="flex min-w-0 items-center gap-2">
              <button
                onClick={() => navigate(`/workspaces/${workspaceId}/dashboard`)}
                className="rounded-lg bg-white px-5 py-3 text-sm font-bold text-black transition hover:bg-white/90"
              >
                + New run
              </button>
              <button
                onClick={() => setKbOpen(true)}
                className="rounded-lg border-2 border-white bg-black px-4 py-3 text-sm font-bold text-white transition hover:bg-white hover:text-black"
              >
                ▣ Knowledge base
              </button>
              <button
                onClick={() => setTrainOpen(true)}
                className="rounded-lg border border-white/70 bg-black px-4 py-3 text-sm font-bold text-white transition hover:border-white hover:bg-white/10"
              >
                + Train model
              </button>
              <button
                onClick={() => pushToast("Approval requests will appear here when review workflows are enabled.")}
                className="rounded-lg border border-white bg-black px-4 py-3 text-sm font-bold text-white transition hover:bg-white/10"
              >
                ✓ Request Approvals
              </button>
              <span className="ml-1 hidden items-center gap-2 text-sm text-white/70 2xl:flex">
                <span className="h-2.5 w-2.5 rounded-full bg-white" /> Online
              </span>
            </div>
          </header>

          <div className="shell-scroll flex-1 overflow-y-auto overflow-x-hidden bg-black">
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
              <div className="h-full w-px bg-[#111827] transition group-hover:w-1 group-hover:bg-[#388bfd]" />
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
              className="rounded-full border border-white/10 bg-white px-4 py-3 text-sm font-black text-black shadow-[0_12px_40px_rgba(0,0,0,0.45)]"
            >
              Open Assistant
            </button>
          </div>
        )}
      </div>

      <TrainModelModal isOpen={trainOpen} onClose={() => setTrainOpen(false)} />
      <KnowledgeBaseModal isOpen={kbOpen} onClose={() => setKbOpen(false)} />
      <SettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
      <ToastViewport items={toasts} />
    </WorkspaceChromeProvider>
  );
}
