import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Outlet, useParams } from "react-router-dom";

import { AssistantPanel } from "../../../components/layout/AssistantPanel";
import { AppShell } from "../../../components/layout/AppShell";
import { Sidebar } from "../../../components/layout/Sidebar";
import { TopBar } from "../../../components/layout/TopBar";
import { OverlayModal } from "../../../components/ui/OverlayModal";
import { ToastViewport, type ToastItem } from "../../../components/ui/ToastViewport";
import { apiGet, apiPost } from "../../../lib/api/client";
import type { KnowledgeBaseDocument, TrainingJob } from "../../../lib/api/types/domain";
import type {
  QueueTrainingRequest,
  UploadKnowledgeBaseDocumentRequest,
} from "../../../lib/api/types/requests";
import { queryKeys } from "../../../lib/query/keys";
import { WorkspaceChromeProvider } from "./WorkspaceChromeContext";

const notificationItems = [
  "1 strategy revision was approved and is ready for planning.",
  "1 draft moved into the publish-ready queue with a scheduled timestamp.",
  "Knowledge base contains 3 founder-demo support files in demo mode.",
];

export function WorkspaceLayout() {
  const { workspaceId = "" } = useParams();
  const queryClient = useQueryClient();
  const kbInputRef = useRef<HTMLInputElement | null>(null);
  const trainInputRef = useRef<HTMLInputElement | null>(null);
  const [assistantCollapsed, setAssistantCollapsed] = useState(false);
  const [showKnowledgeBase, setShowKnowledgeBase] = useState(false);
  const [showTrainModel, setShowTrainModel] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAccountSettings, setShowAccountSettings] = useState(false);
  const [currentRole, setCurrentRole] = useState("Manager");
  const [selectedTrainingCategory, setSelectedTrainingCategory] =
    useState<UploadKnowledgeBaseDocumentRequest["category"]>("brand_voice");
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const documentsQuery = useQuery({
    queryKey: queryKeys.knowledgeBaseDocuments(workspaceId),
    queryFn: () =>
      apiGet<KnowledgeBaseDocument[]>(`/api/v1/workspaces/${workspaceId}/knowledge-base/documents`),
    enabled: workspaceId.length > 0,
  });

  const trainingJobsQuery = useQuery({
    queryKey: queryKeys.trainingJobs(workspaceId),
    queryFn: () => apiGet<TrainingJob[]>(`/api/v1/workspaces/${workspaceId}/training-jobs`),
    enabled: workspaceId.length > 0,
  });

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

  const uploadDocumentMutation = useMutation({
    mutationFn: (payload: UploadKnowledgeBaseDocumentRequest) =>
      apiPost<KnowledgeBaseDocument, UploadKnowledgeBaseDocumentRequest>(
        `/api/v1/workspaces/${workspaceId}/knowledge-base/documents`,
        payload,
      ),
    onSuccess: async (document) => {
      pushToast(`${document.file_name} uploaded and indexed.`);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.knowledgeBaseDocuments(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
      ]);
    },
    onError: (error) => {
      pushToast(error instanceof Error ? error.message : "Document upload failed.");
    },
  });

  const trainingMutation = useMutation({
    mutationFn: (payload: QueueTrainingRequest) =>
      apiPost<TrainingJob, QueueTrainingRequest>(
        `/api/v1/workspaces/${workspaceId}/training-jobs`,
        payload,
      ),
    onSuccess: async (job) => {
      pushToast(`Training job completed with ${job.document_ids.length} document${job.document_ids.length === 1 ? "" : "s"}.`);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.trainingJobs(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activity(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.activitySummary(workspaceId) }),
      ]);
    },
    onError: (error) => {
      pushToast(error instanceof Error ? error.message : "Training request failed.");
    },
  });

  const uploadFiles = (files: FileList | File[], category: UploadKnowledgeBaseDocumentRequest["category"]) => {
    Array.from(files).forEach((file) => {
      uploadDocumentMutation.mutate({
        file_name: file.name,
        category,
        mime_type: file.type || "application/octet-stream",
        size_bytes: file.size,
        uploaded_by_member_id: null,
      });
    });
  };

  const documents = documentsQuery.data ?? [];
  const latestTrainingJob = trainingJobsQuery.data?.[0] ?? null;

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
        sidebar={
          <Sidebar
            workspaceId={workspaceId}
            currentRole={currentRole}
            onToggleRole={() => {
              setCurrentRole((role) => (role === "Manager" ? "Reviewer" : "Manager"));
              pushToast("Demo role switched.");
            }}
            onOpenAccountSettings={() => setShowAccountSettings(true)}
            onLogout={() => {
              window.localStorage.removeItem("user_token");
              window.localStorage.removeItem("current_user");
              pushToast("Signed out of the demo session.");
            }}
          />
        }
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
              queryClient.invalidateQueries({ queryKey: queryKeys.knowledgeBaseDocuments(workspaceId) });
              pushToast("Knowledge base synced.");
              setShowKnowledgeBase(false);
            }}
            className="w-full rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-black transition hover:bg-white/90"
          >
            Sync demo documents
          </button>
        }
      >
        <div
          className="space-y-3"
          onDragOver={(event) => event.preventDefault()}
          onDrop={(event) => {
            event.preventDefault();
            uploadFiles(event.dataTransfer.files, "campaign_brief");
          }}
        >
          <input
            ref={kbInputRef}
            type="file"
            multiple
            className="hidden"
            accept=".pdf,.docx,.txt,.csv,.md,.png,.jpg,.jpeg"
            onChange={(event) => {
              if (event.target.files) {
                uploadFiles(event.target.files, "campaign_brief");
                event.target.value = "";
              }
            }}
          />
          <button
            type="button"
            onClick={() => kbInputRef.current?.click()}
            className="w-full rounded-2xl border border-dashed border-white/15 bg-white/5 px-4 py-5 text-left transition hover:bg-white/8"
          >
            <span className="block text-sm font-semibold text-white">
              {uploadDocumentMutation.isPending ? "Indexing upload..." : "Upload or drop documents"}
            </span>
            <span className="mt-1 block text-xs text-white/45">PDF, DOCX, TXT, CSV, MD, PNG, JPG.</span>
          </button>

          {documents.map((doc) => (
            <div key={doc.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-white">{doc.file_name}</p>
                  <p className="mt-1 text-xs text-white/45">{doc.category.replace(/_/g, " ")}</p>
                </div>
                <span className="rounded-full border border-white/10 bg-black/40 px-3 py-1 text-[11px] text-white/65">
                  {doc.ingestion_status}
                </span>
              </div>
              <p className="mt-3 text-sm text-white/55">
                {(doc.size_bytes / 1024).toFixed(1)} KB | {new Date(doc.created_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      </OverlayModal>

      <OverlayModal
        open={showTrainModel}
        onClose={() => setShowTrainModel(false)}
        title="Train Model"
        description="Queue document context for the model training pipeline."
        maxWidthClassName="max-w-xl"
        footer={
          <button
            type="button"
            onClick={() => {
              trainingMutation.mutate({
                category: selectedTrainingCategory,
                document_ids: documents.map((doc) => doc.id),
                requested_by_member_id: null,
              });
              setShowTrainModel(false);
            }}
            disabled={trainingMutation.isPending || documents.length === 0}
            className="w-full rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-black transition hover:bg-white/90"
          >
            {trainingMutation.isPending ? "Queueing..." : "Queue training request"}
          </button>
        }
      >
        <input
          ref={trainInputRef}
          type="file"
          multiple
          className="hidden"
          accept=".pdf,.docx,.txt,.csv,.md"
          onChange={(event) => {
            if (event.target.files) {
              uploadFiles(event.target.files, selectedTrainingCategory);
              event.target.value = "";
            }
          }}
        />
        <label className="mb-4 block">
          <span className="mb-2 block text-sm font-medium text-white">Training category</span>
          <select
            value={selectedTrainingCategory}
            onChange={(event) =>
              setSelectedTrainingCategory(event.target.value as UploadKnowledgeBaseDocumentRequest["category"])
            }
            className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
          >
            {["brand_voice", "social_strategy", "audience", "competitors", "campaign_brief"].map((category) => (
              <option key={category} value={category}>
                {category.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={() => trainInputRef.current?.click()}
          className="flex w-full cursor-pointer flex-col items-center justify-center rounded-[1.75rem] border-2 border-dashed border-white/15 bg-white/5 px-6 py-12 text-center transition hover:bg-white/8"
        >
          <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-black/50 text-white">
            #
          </span>
          <span className="text-sm font-semibold text-white">Upload briefs, voice guides, or audience files</span>
          <span className="mt-2 text-xs text-white/45">PDF, DOCX, TXT, CSV. Demo mode keeps this local and non-destructive.</span>
        </button>
        <p className="mt-4 text-xs text-white/45">
          {latestTrainingJob
            ? `Latest job: ${latestTrainingJob.status} with ${latestTrainingJob.document_ids.length} document${latestTrainingJob.document_ids.length === 1 ? "" : "s"}.`
            : `${documents.length} document${documents.length === 1 ? "" : "s"} ready for training.`}
        </p>
      </OverlayModal>

      <OverlayModal
        open={showAccountSettings}
        onClose={() => setShowAccountSettings(false)}
        title="Account Settings"
        description="Demo account controls for handoff and role testing."
        maxWidthClassName="max-w-md"
      >
        <div className="space-y-3">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-sm font-semibold text-white">Guest User</p>
            <p className="mt-1 text-xs text-white/45">Free Plan | Role: {currentRole}</p>
          </div>
          <button
            type="button"
            onClick={() => {
              setCurrentRole((role) => (role === "Manager" ? "Reviewer" : "Manager"));
              pushToast("Demo role switched.");
            }}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
          >
            Switch demo role
          </button>
        </div>
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
