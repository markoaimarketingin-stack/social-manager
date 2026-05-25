import { useEffect, useState } from "react";
import { Outlet, useParams } from "react-router-dom";

import { AssistantPanel } from "../../../components/layout/AssistantPanel";
import { AppShell } from "../../../components/layout/AppShell";
import { Sidebar } from "../../../components/layout/Sidebar";
import { TopBar } from "../../../components/layout/TopBar";
import { OverlayModal } from "../../../components/ui/OverlayModal";
import { ToastViewport, type ToastItem } from "../../../components/ui/ToastViewport";
import { WorkspaceChromeProvider } from "./WorkspaceChromeContext";

const knowledgeBaseDocs = [
  { name: "brand_voice_guidelines.txt", category: "Brand voice", type: "TXT", uploaded: "2 days ago" },
  { name: "campaign_brief_festival_launch.pdf", category: "Campaign brief", type: "PDF", uploaded: "Yesterday" },
  { name: "audience_segments.csv", category: "Audience", type: "CSV", uploaded: "Today" },
];

const notificationItems = [
  "1 strategy revision was approved and is ready for planning.",
  "1 draft moved into the publish-ready queue with a scheduled timestamp.",
  "Knowledge base contains 3 founder-demo support files in demo mode.",
];

export function WorkspaceLayout() {
  const { workspaceId = "" } = useParams();
  const [assistantCollapsed, setAssistantCollapsed] = useState(false);
  const [showKnowledgeBase, setShowKnowledgeBase] = useState(false);
  const [showTrainModel, setShowTrainModel] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const pushToast = (message: string) => {
    const nextToast = { id: `${Date.now()}-${Math.random()}`, message };
    setToasts((current) => [...current, nextToast]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((item) => item.id !== nextToast.id));
    }, 2800);
  };

  useEffect(() => {
    setAssistantCollapsed(false);
  }, [workspaceId]);

  return (
    <WorkspaceChromeProvider
      value={{
        assistantCollapsed,
        openAssistant: () => setAssistantCollapsed(false),
        toggleAssistant: () => setAssistantCollapsed((current) => !current),
        openKnowledgeBase: () => setShowKnowledgeBase(true),
        openTrainModal: () => setShowTrainModel(true),
        openNotifications: () => setShowNotifications(true),
        pushToast,
      }}
    >
      <AppShell
        sidebar={<Sidebar workspaceId={workspaceId} />}
        topbar={<TopBar />}
        assistant={<AssistantPanel workspaceId={workspaceId} />}
        assistantCollapsed={assistantCollapsed}
        onOpenAssistant={() => setAssistantCollapsed(false)}
      >
        <Outlet context={{ workspaceId }} />
      </AppShell>

      <OverlayModal
        open={showKnowledgeBase}
        onClose={() => setShowKnowledgeBase(false)}
        title="Knowledge Base"
        description="Documents and context artifacts referenced across the founder demo flow."
        footer={
          <button
            type="button"
            onClick={() => {
              pushToast("Knowledge base synced in demo mode.");
              setShowKnowledgeBase(false);
            }}
            className="w-full rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-black transition hover:bg-white/90"
          >
            Sync demo documents
          </button>
        }
      >
        <div className="space-y-3">
          {knowledgeBaseDocs.map((doc) => (
            <div key={doc.name} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-white">{doc.name}</p>
                  <p className="mt-1 text-xs text-white/45">{doc.category}</p>
                </div>
                <span className="rounded-full border border-white/10 bg-black/40 px-3 py-1 text-[11px] text-white/65">
                  {doc.type}
                </span>
              </div>
              <p className="mt-3 text-sm text-white/55">Uploaded {doc.uploaded}</p>
            </div>
          ))}
        </div>
      </OverlayModal>

      <OverlayModal
        open={showTrainModel}
        onClose={() => setShowTrainModel(false)}
        title="Train Model"
        description="Deployment-safe training placeholder that preserves the founder workflow without needing provider integrations."
        maxWidthClassName="max-w-xl"
        footer={
          <button
            type="button"
            onClick={() => {
              pushToast("Training request queued in demo mode.");
              setShowTrainModel(false);
            }}
            className="w-full rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-black transition hover:bg-white/90"
          >
            Queue training request
          </button>
        }
      >
        <label className="flex cursor-pointer flex-col items-center justify-center rounded-[1.75rem] border-2 border-dashed border-white/15 bg-white/5 px-6 py-12 text-center transition hover:bg-white/8">
          <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-black/50 text-white">
            #
          </span>
          <span className="text-sm font-semibold text-white">Upload briefs, voice guides, or audience files</span>
          <span className="mt-2 text-xs text-white/45">PDF, DOCX, TXT, CSV. Demo mode keeps this local and non-destructive.</span>
        </label>
      </OverlayModal>

      <OverlayModal
        open={showNotifications}
        onClose={() => setShowNotifications(false)}
        title="Operational Notifications"
        description="A founder-facing view of what changed recently across the workflow."
        maxWidthClassName="max-w-2xl"
      >
        <div className="space-y-3">
          {notificationItems.map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/80">
              {item}
            </div>
          ))}
        </div>
      </OverlayModal>

      <ToastViewport items={toasts} />
    </WorkspaceChromeProvider>
  );
}
