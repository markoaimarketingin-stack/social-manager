
import { useEffect, useState, useRef } from "react";

import { useAuth } from "../../../features/auth/AuthContext";
import { apiFetch, apiBaseUrl } from "../../../lib/api/client";
import { useWorkspaceChrome } from "../components/WorkspaceChromeContext";

type DashboardStats = {
  user: { id: number; email: string; name: string };
  connected_platforms: Array<{
    platform: string;
    account_name: string | null;
    account_id: string | null;
    connected_at: string | null;
  }>;
  stats: {
    total_posts: number;
    published: number;
    pending: number;
    failed: number;
  };
  recent_posts: Array<{
    id: number;
    content: string;
    created_at: string | null;
    platforms: Array<{ platform: string; status: string; error: string | null }>;
  }>;
};

type SupervisorAnalysis = {
  backend: "ok" | "error";
  database: string;
  workers: string;
  queuePending: number;
  providerSummary: string;
  knowledgeDocuments: number;
  recommendations: string[];
};

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return "Just now";
  const date = new Date(dateStr);
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return "Just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function formatPlatform(platform: string) {
  return platform === "x" ? "X" : platform.charAt(0).toUpperCase() + platform.slice(1);
}

export function WorkspaceOverviewPage() {
  const { token } = useAuth();
  const { pushToast } = useWorkspaceChrome();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [composeText, setComposeText] = useState("");
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<string | null>(null);
  const [, setRunningAnalysis] = useState(false);
  const [analysis, setAnalysis] = useState<SupervisorAnalysis | null>(null);

  // Kahani Ghar Live Data State
  const [kgData, setKgData] = useState<any | null>(null);
  const [kgLoading, setKgLoading] = useState(false);

  // New features state
  const [mediaFiles, setMediaFiles] = useState<Array<{ id: number; url: string; file_type: string; name: string }>>([]);
  const [uploading, setUploading] = useState(false);
  const [generatingHashtags, setGeneratingHashtags] = useState(false);
  const [previewPlatform, setPreviewPlatform] = useState<"instagram" | "facebook" | "linkedin">("instagram");
  const [activeCarouselIndex, setActiveCarouselIndex] = useState(0);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchStats = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await apiFetch("/api/dashboard/stats", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const payload = await res.json().catch(() => null);
        throw new Error(payload?.detail ?? "Failed to load dashboard stats");
      }
      const data = (await res.json()) as DashboardStats;
      setStats(data);
      setSelectedPlatforms(data.connected_platforms.map((platform) => platform.platform));
    } catch (error: any) {
      setStats(null);
      setSelectedPlatforms([]);
      setLoadError(error?.message ?? "Failed to load dashboard stats");
    } finally {
      setLoading(false);
    }
  };

  const fetchKgData = async () => {
    setKgLoading(true);
    try {
      const res = await apiFetch("/api/social_manager/kahanighar/data");
      if (res.ok) {
        const data = await res.json();
        setKgData(data);
      }
    } catch (err) {
      console.error("Failed to load Kahani Ghar data", err);
    } finally {
      setKgLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchKgData();
  }, [token]);

  useEffect(() => {
    const handleAutofill = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail) {
        if (customEvent.detail.content) {
          setComposeText(customEvent.detail.content);
        }
        if (customEvent.detail.platforms) {
          setSelectedPlatforms(customEvent.detail.platforms);
        }
        pushToast("Autofilled draft content into Quick Publisher!");
        const composeArea = document.getElementById("post-desc");
        if (composeArea) {
          composeArea.scrollIntoView({ behavior: "smooth", block: "center" });
          composeArea.focus();
        }
      }
    };
    window.addEventListener("autofill-compose", handleAutofill);
    return () => window.removeEventListener("autofill-compose", handleAutofill);
  }, [pushToast]);

  const togglePlatform = (platform: string) => {
    setSelectedPlatforms((current) =>
      current.includes(platform) ? current.filter((item) => item !== platform) : [...current, platform],
    );
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    if (mediaFiles.length + files.length > 10) {
      pushToast("Cannot upload more than 10 files (Instagram limit).");
      return;
    }

    const fileNames = Array.from(files).map((f) => f.name);

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    setUploading(true);
    try {
      const res = await apiFetch("/api/publishing/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const payload = await res.json().catch(() => null);
        throw new Error(payload?.detail ?? "Upload failed");
      }

      const data = await res.json();
      setMediaFiles((prev) => [
        ...prev,
        ...data.map((item: any, idx: number) => ({ ...item, name: fileNames[idx] })),
      ]);
      setActiveCarouselIndex(mediaFiles.length);
      pushToast(`Successfully uploaded ${data.length} files.`);
    } catch (err: any) {
      pushToast(`Upload error: ${err.message}`);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const removeMedia = (id: number) => {
    setMediaFiles((prev) => prev.filter((item) => item.id !== id));
    setActiveCarouselIndex(0);
  };

  const handleGenerateHashtags = async () => {
    if (!composeText.trim()) {
      pushToast("Please enter a description first.");
      return;
    }

    setGeneratingHashtags(true);
    try {
      const res = await apiFetch("/api/publishing/generate-hashtags", {
        method: "POST",
        body: JSON.stringify({
          description: composeText,
          platform: previewPlatform,
        }),
      });

      if (!res.ok) {
        const payload = await res.json().catch(() => null);
        throw new Error(payload?.detail ?? "Failed to generate hashtags");
      }

      const data = await res.json();
      if (data.hashtags && data.hashtags.length > 0) {
        const tagsString = " " + data.hashtags.join(" ");
        setComposeText((prev) => prev.trim() + tagsString);
        pushToast("Hashtags generated!");
      } else {
        pushToast("No hashtags generated. Try a different description.");
      }
    } catch (err: any) {
      pushToast(`Hashtag error: ${err.message}`);
    } finally {
      setGeneratingHashtags(false);
    }
  };

  const handleQuickPost = async () => {
    if (!composeText.trim() || selectedPlatforms.length === 0) {
      pushToast("Enter post content and select at least one platform.");
      return;
    }

    setPosting(true);
    setPostResult(null);
    try {
      const res = await apiFetch("/api/publishing/schedule", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          platforms: selectedPlatforms,
          content: composeText,
          scheduled_at: null,
          asset_ids: mediaFiles.map((m) => m.id),
        }),
      });

      if (!res.ok) {
        const payload = await res.json().catch(() => null);
        throw new Error(payload?.detail ?? "Publishing request failed");
      }

      setPostResult("✓ Post queued for publishing.");
      setComposeText("");
      setMediaFiles([]);
      setShowConfirmModal(false);
      pushToast("Post queued for publishing.");
      window.setTimeout(fetchStats, 1000);
    } catch (error: any) {
      setPostResult(`Error: ${error?.message ?? "Publishing failed"}`);
    } finally {
      setPosting(false);
    }
  };

  const handleRunAnalysis = async () => {
    setRunningAnalysis(true);
    setAnalysis(null);
    pushToast("Running supervisor readiness check...");

    try {
      const [systemRes, providersRes, documentsRes] = await Promise.all([
        apiFetch("/api/system/status"),
        apiFetch("/api/auth/providers"),
        apiFetch("/api/knowledge_base/documents"),
      ]);

      if (!systemRes.ok) throw new Error("System status check failed");
      if (!providersRes.ok) throw new Error("Provider readiness check failed");
      if (!documentsRes.ok) throw new Error("Knowledge base check failed");

      const system = await systemRes.json();
      const providers = await providersRes.json();
      const documents = await documentsRes.json();
      const providerList = providers.providers ?? [];
      const readyProviders = providerList.filter((provider: any) => provider.configured);
      const docs = Array.isArray(documents) ? documents : documents.documents ?? [];
      const failedJobs = stats?.stats.failed ?? 0;

      setAnalysis({
        backend: "ok",
        database: system.database ?? "unknown",
        workers: system.workers ?? "unknown",
        queuePending: Number(system.queue_pending ?? 0),
        providerSummary: `${readyProviders.length}/${providerList.length} providers ready`,
        knowledgeDocuments: docs.length,
        recommendations: [
          readyProviders.length === 0
            ? "Connect at least one platform before publishing."
            : `${readyProviders.length} platform${readyProviders.length === 1 ? "" : "s"} ready for publishing.`,
          docs.length === 0
            ? "Upload brand voice, audience, or campaign documents to improve supervisor recommendations."
            : `${docs.length} knowledge document${docs.length === 1 ? "" : "s"} available for strategy context.`,
          failedJobs > 0
            ? `${failedJobs} failed publishing job${failedJobs === 1 ? "" : "s"} need review.`
            : "No failed publishing jobs in the current dashboard state.",
        ],
      });
      pushToast("Supervisor readiness check completed.");
      await fetchStats();
    } catch (error: any) {
      setAnalysis({
        backend: "error",
        database: "unknown",
        workers: "unknown",
        queuePending: 0,
        providerSummary: "Unavailable",
        knowledgeDocuments: 0,
        recommendations: [error?.message ?? "Supervisor analysis failed."],
      });
      pushToast("Supervisor analysis failed.");
    } finally {
      setRunningAnalysis(false);
    }
  };

  useEffect(() => {
    if (token) {
      handleRunAnalysis();
    }
  }, [token]);

  const handlePrevMedia = () => {
    setActiveCarouselIndex((prev) => (prev > 0 ? prev - 1 : mediaFiles.length - 1));
  };

  const handleNextMedia = () => {
    setActiveCarouselIndex((prev) => (prev < mediaFiles.length - 1 ? prev + 1 : 0));
  };

  const renderPlatformPreview = (platform: "instagram" | "facebook" | "linkedin") => {
    const brandName = stats?.user?.name || "Your Brand";
    const brandHandle = brandName.toLowerCase().replace(/\s+/g, "");

    if (platform === "instagram") {
      const currentMedia = mediaFiles[activeCarouselIndex];
      const hasMedia = mediaFiles.length > 0;

      return (
        <div className="w-full max-w-[340px] rounded-xl border border-white/10 bg-[#000000] text-white overflow-hidden text-xs">
          {/* Header */}
          <div className="flex items-center justify-between p-3 border-b border-white/5">
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-full bg-gradient-to-tr from-yellow-500 to-purple-600 flex items-center justify-center font-bold text-[10px] text-white">
                M
              </div>
              <div>
                <p className="font-bold text-white leading-none">@{brandHandle}</p>
                <p className="text-[9px] text-white/40 mt-0.5">Sponsored</p>
              </div>
            </div>
            <span className="text-white/60 font-black text-sm">•••</span>
          </div>

          {/* Media View */}
          <div className="relative aspect-square w-full bg-neutral-950 flex items-center justify-center border-b border-white/5">
            {hasMedia && currentMedia ? (
              currentMedia.file_type === "video" ? (
                <video
                  src={`${apiBaseUrl}${currentMedia.url}`}
                  controls
                  className="h-full w-full object-cover"
                />
              ) : (
                <img
                  src={`${apiBaseUrl}${currentMedia.url}`}
                  alt="Preview"
                  className="h-full w-full object-cover"
                />
              )
            ) : (
              <div className="flex flex-col items-center justify-center p-6 text-center text-white/30 space-y-2">
                <span className="text-2xl">📸</span>
                <p className="font-semibold text-[11px]">No Media Attached</p>
                <p className="text-[10px] text-red-500/80 max-w-[200px]">
                  ⚠️ Instagram requires at least one image/video.
                </p>
              </div>
            )}

            {/* Carousel Navigation */}
            {mediaFiles.length > 1 && (
              <>
                <button
                  onClick={handlePrevMedia}
                  className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/60 hover:bg-black text-white h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs"
                >
                  ‹
                </button>
                <button
                  onClick={handleNextMedia}
                  className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/60 hover:bg-black text-white h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs"
                >
                  ›
                </button>
                <span className="absolute bottom-3 right-3 px-2 py-0.5 bg-black/75 rounded-full text-[9px] text-white">
                  {activeCarouselIndex + 1}/{mediaFiles.length}
                </span>
              </>
            )}
          </div>

          {/* Action Icons */}
          <div className="flex items-center justify-between p-3">
            <div className="flex items-center gap-3 text-lg">
              <span>♡</span>
              <span>💬</span>
              <span>⚡</span>
            </div>
            <span className="text-lg">📥</span>
          </div>

          {/* Likes & Caption */}
          <div className="px-3 pb-3 space-y-1 leading-relaxed">
            <p className="font-bold">1,482 likes</p>
            <p className="text-white/80">
              <span className="font-bold text-white mr-1.5">@{brandHandle}</span>
              {composeText || "Write a description..."}
            </p>
          </div>
        </div>
      );
    }

    if (platform === "facebook") {
      const firstMedia = mediaFiles[0];
      const hasMedia = mediaFiles.length > 0;

      return (
        <div className="w-full max-w-[360px] rounded-xl border border-white/10 bg-[#18191a] text-white p-4 text-xs space-y-3">
          {/* Header */}
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center font-bold text-sm text-white">
              F
            </div>
            <div>
              <h5 className="font-bold">{brandName}</h5>
              <p className="text-[10px] text-white/40 flex items-center gap-1">
                Just now · 🌎
              </p>
            </div>
          </div>

          {/* Caption */}
          <p className="text-white/95 leading-relaxed break-words whitespace-pre-wrap">
            {composeText || "Write a description..."}
          </p>

          {/* Media box */}
          {hasMedia && firstMedia ? (
            <div className="rounded-lg overflow-hidden border border-white/5 bg-black">
              {firstMedia.file_type === "video" ? (
                <video
                  src={`${apiBaseUrl}${firstMedia.url}`}
                  controls
                  className="w-full object-cover max-h-[200px]"
                />
              ) : (
                <img
                  src={`${apiBaseUrl}${firstMedia.url}`}
                  alt="Facebook attachment"
                  className="w-full object-cover max-h-[200px]"
                />
              )}
              {mediaFiles.length > 1 && (
                <div className="bg-white/5 px-3 py-2 text-[10px] text-white/50 border-t border-white/5 text-center">
                  + {mediaFiles.length - 1} more media files
                </div>
              )}
            </div>
          ) : null}

          {/* Footer Bar */}
          <div className="flex items-center justify-between text-white/40 border-t border-white/5 pt-2.5 text-[10px] font-bold">
            <span>👍 Like</span>
            <span>💬 Comment</span>
            <span>🔁 Share</span>
          </div>
        </div>
      );
    }

    if (platform === "linkedin") {
      const firstMedia = mediaFiles[0];
      const hasMedia = mediaFiles.length > 0;

      return (
        <div className="w-full max-w-[360px] rounded-xl border border-white/10 bg-[#1d2226] text-white p-4 text-xs space-y-3">
          {/* Header */}
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-sky-700 flex items-center justify-center font-bold text-sm text-white">
              L
            </div>
            <div>
              <h5 className="font-bold flex items-center gap-1">
                {brandName} <span className="text-[9px] text-white/30 font-normal">· 1st</span>
              </h5>
              <p className="text-[10px] text-white/40 leading-none mt-0.5">Marketing Specialist at Marko AI</p>
              <p className="text-[9px] text-white/40 mt-0.5">1m · Edited · 🌐</p>
            </div>
          </div>

          {/* Description */}
          <p className="text-white/90 leading-relaxed break-words whitespace-pre-wrap">
            {composeText || "Write a description..."}
          </p>

          {/* Media box */}
          {hasMedia && firstMedia ? (
            <div className="rounded-lg overflow-hidden border border-white/5 bg-[#000000]">
              {firstMedia.file_type === "video" ? (
                <video
                  src={`${apiBaseUrl}${firstMedia.url}`}
                  controls
                  className="w-full object-cover max-h-[180px]"
                />
              ) : (
                <img
                  src={`${apiBaseUrl}${firstMedia.url}`}
                  alt="LinkedIn media"
                  className="w-full object-cover max-h-[180px]"
                />
              )}
              {mediaFiles.length > 1 && (
                <div className="bg-white/5 px-3 py-1.5 text-[9px] text-white/50 border-t border-white/5">
                  Carousel ({mediaFiles.length} pages)
                </div>
              )}
            </div>
          ) : null}

          {/* Actions */}
          <div className="flex items-center justify-between border-t border-white/5 pt-2 text-[10px] text-white/50 font-semibold">
            <span>👍 Like</span>
            <span>💬 Comment</span>
            <span>🔁 Repost</span>
            <span>📤 Send</span>
          </div>
        </div>
      );
    }

    return null;
  };

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center" style={{ background: "#0a0a0a" }}>
        <div className="text-center space-y-2.5">
          <div className="h-5 w-5 animate-spin rounded-full border border-white/20 border-t-white/70 mx-auto" />
          <p className="text-xs" style={{ color: "rgba(255,255,255,0.3)" }}>Loading supervisor overview...</p>
        </div>
      </div>
    );
  }

  const connectedPlatforms = stats?.connected_platforms ?? [];
  const recentPosts = stats?.recent_posts ?? [];
  const statsList = [
    { label: "Total Posts", value: stats?.stats?.total_posts ?? 0, icon: "✍", color: "#388bfd", bg: "rgba(56,139,253,0.08)", border: "rgba(56,139,253,0.25)" },
    { label: "Published", value: stats?.stats?.published ?? 0, icon: "✓", color: "#3fb950", bg: "rgba(63,185,80,0.08)", border: "rgba(63,185,80,0.25)" },
    { label: "Pending", value: stats?.stats?.pending ?? 0, icon: "⌛", color: "#d29922", bg: "rgba(210,153,34,0.08)", border: "rgba(210,153,34,0.25)" },
    { label: "Failed", value: stats?.stats?.failed ?? 0, icon: "×", color: "#f85149", bg: "rgba(248,81,73,0.08)", border: "rgba(248,81,73,0.25)" },
  ];

  return (
    <div className="flex h-full w-full flex-col" style={{ background: "#0a0a0a", color: "#e2e8f0" }}>
      <div className="mx-auto flex w-full max-w-[940px] flex-1 flex-col space-y-6 overflow-y-auto px-6 py-8 scrollbar-thin">
        {loadError && (
          <div className="rounded-xl border border-red-500/25 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {loadError}
          </div>
        )}
 
        {/* Hero Section */}
        <section className="flex flex-col items-center justify-center py-16 text-center space-y-5">
          <div className="flex items-end gap-1 mb-2" style={{ color: "rgba(255,255,255,0.7)" }}>
            <div className="w-2 rounded-sm" style={{ height: "14px", background: "rgba(255,255,255,0.25)" }} />
            <div className="w-2 rounded-sm" style={{ height: "22px", background: "rgba(255,255,255,0.5)" }} />
            <div className="w-2 rounded-sm" style={{ height: "32px", background: "rgba(255,255,255,0.9)" }} />
            <div className="w-2 rounded-sm" style={{ height: "18px", background: "rgba(255,255,255,0.4)" }} />
            <div className="w-2 rounded-sm" style={{ height: "26px", background: "rgba(255,255,255,0.65)" }} />
          </div>
          <h1 className="text-2xl font-semibold text-white tracking-tight">
            I am your Social Media Supervisor
          </h1>
          <p className="max-w-[440px] text-sm leading-relaxed text-white/45">
            Specialized in orchestrating social strategy, audience insights, content direction, publishing workflows, and platform performance for unified, decision-ready growth.
          </p>
        </section>
 
        {/* Stats Grid */}
        <div className="grid gap-3 grid-cols-2 md:grid-cols-4">
          {statsList.map((stat, idx) => (
            <div
              key={stat.label}
              className={`p-4 rounded-xl border flex items-center justify-between glass-panel hover-glow animate-fade-up stagger-${idx + 1}`}
              style={{ boxShadow: "0 4px 30px rgba(0, 0, 0, 0.2)" }}
            >
              <div>
                <p className="text-[10px] font-semibold text-white/40 uppercase tracking-wider">{stat.label}</p>
                <h4 className="text-xl font-bold mt-1" style={{ color: stat.color }}>{stat.value}</h4>
              </div>
              <div
                className="h-8 w-8 rounded-lg flex items-center justify-center text-sm font-bold border"
                style={{ background: stat.bg, color: stat.color, borderColor: stat.border }}
              >
                {stat.icon}
              </div>
            </div>
          ))}
        </div>
 
        {analysis && (
          <section className="rounded-2xl p-5 border glass-panel hover-glow animate-fade-up stagger-1" style={{ borderColor: analysis.backend === "ok" ? "rgba(63,185,80,0.25)" : "rgba(248,81,73,0.35)", boxShadow: "0 4px 30px rgba(0, 0, 0, 0.2)" }}>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Supervisor Analysis</h4>
                <p className="mt-1 text-[10px] text-white/40">Live backend, provider, knowledge base, and queue readiness.</p>
              </div>
              <div className="flex flex-wrap gap-2 text-[10px] font-bold uppercase tracking-wider">
                <span className="rounded-full border border-white/10 px-2.5 py-1 text-white/70">DB {analysis.database}</span>
                <span className="rounded-full border border-white/10 px-2.5 py-1 text-white/70">Workers {analysis.workers}</span>
                <span className="rounded-full border border-white/10 px-2.5 py-1 text-white/70">Queue {analysis.queuePending}</span>
                <span className="rounded-full border border-white/10 px-2.5 py-1 text-white/70">{analysis.providerSummary}</span>
                <span className="rounded-full border border-white/10 px-2.5 py-1 text-white/70">KB {analysis.knowledgeDocuments}</span>
              </div>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {analysis.recommendations.map((item) => (
                <div key={item} className="rounded-xl border border-[rgba(255,255,255,0.04)] bg-[#000000]/40 p-3 text-xs leading-6 text-white/65">
                  {item}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Kahani Ghar Live Data Section */}
        {kgLoading && (
          <section className="p-6 rounded-2xl border glass-panel text-center space-y-3" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
            <div className="h-5 w-5 animate-spin rounded-full border border-white/20 border-t-white/70 mx-auto" />
            <p className="text-xs text-white/40">Fetching Kahani Ghar Meta Graph API & Ad Manager data...</p>
          </section>
        )}

        {!kgLoading && kgData && (
          <section
            className="rounded-2xl p-6 border space-y-6 glass-panel hover-glow animate-fade-up stagger-2"
            style={{ borderColor: "rgba(139, 92, 246, 0.25)", boxShadow: "0 8px 32px rgba(139, 92, 246, 0.05)" }}
          >
            <div className="flex items-center justify-between border-b border-white/5 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-purple-500 animate-pulse" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-white/75">Kahani Ghar Live Marketing Hub</h4>
                </div>
                <p className="text-[10px] text-white/45 mt-1">Organic Instagram Media Graph API & Paid Meta Ads Manager integration.</p>
              </div>
              <button
                onClick={fetchKgData}
                className="px-3 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-[10px] font-bold text-purple-300 transition-all"
              >
                🔄 Refresh Live API Data
              </button>
            </div>

            {/* Diagnostics Warnings */}
            {kgData.diagnostics && kgData.diagnostics.length > 0 && (
              <div className="p-4 rounded-xl border border-red-500/25 bg-red-500/10 text-xs text-red-200 space-y-1.5 leading-relaxed">
                <p className="font-bold flex items-center gap-1.5 text-red-400">
                  <span>⚠️</span> Meta Graph API Connections Diagnostic Warning
                </p>
                <p className="text-[10px] text-white/50 mb-2">
                  The following issues occurred while trying to fetch live data from Facebook and Instagram APIs. Ensure permissions are granted.
                </p>
                <ul className="list-disc pl-4 space-y-1 text-[10px] text-red-300/90">
                  {kgData.diagnostics.map((diag: string, idx: number) => (
                    <li key={idx}>{diag}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Live Campaign Insights Grid */}
            <div className="grid gap-3 grid-cols-2 md:grid-cols-4">
              <div className="p-3.5 rounded-xl border border-white/5 bg-black/40">
                <p className="text-[9px] font-semibold text-white/40 uppercase tracking-wider">Meta Ads Spend (30D)</p>
                <h5 className="text-base font-bold mt-1 text-purple-300">₹{kgData.summary.total_spend.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</h5>
              </div>
              <div className="p-3.5 rounded-xl border border-white/5 bg-black/40">
                <p className="text-[9px] font-semibold text-white/40 uppercase tracking-wider">Ad Impressions</p>
                <h5 className="text-base font-bold mt-1 text-sky-400">{kgData.summary.total_impressions.toLocaleString()}</h5>
              </div>
              <div className="p-3.5 rounded-xl border border-white/5 bg-black/40">
                <p className="text-[9px] font-semibold text-white/40 uppercase tracking-wider">Ad Click Volume</p>
                <h5 className="text-base font-bold mt-1 text-emerald-400">{kgData.summary.total_clicks.toLocaleString()}</h5>
              </div>
              <div className="p-3.5 rounded-xl border border-white/5 bg-black/40">
                <p className="text-[9px] font-semibold text-white/40 uppercase tracking-wider">Average CTR</p>
                <h5 className="text-base font-bold mt-1 text-yellow-400">{kgData.summary.avg_ctr.toFixed(2)}%</h5>
              </div>
            </div>

            {/* Carousel Deck & Campaigns List */}
            <div className="grid gap-6 lg:grid-cols-2">
              {/* Organic IG Posts */}
              <div className="space-y-3">
                <h5 className="text-[10px] font-bold uppercase tracking-wider text-white/50">Recent Organic Instagram Feed</h5>
                <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin max-h-[300px]">
                  {kgData.instagram_posts.map((post: any) => (
                    <div key={post.id} className="min-w-[200px] max-w-[200px] rounded-xl border border-white/5 bg-black/50 p-2.5 space-y-2">
                      <div className="aspect-square rounded-lg bg-neutral-900 overflow-hidden relative">
                        {post.media_url ? (
                          <img src={post.media_url} alt="IG Feed" className="h-full w-full object-cover" />
                        ) : (
                          <div className="h-full w-full flex items-center justify-center text-white/20">🎥 Reel</div>
                        )}
                        <span className="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-black/80 text-[8px] text-white/60">
                          {post.media_type === "VIDEO" ? "Reel" : "Post"}
                        </span>
                      </div>
                      <p className="text-[10px] text-white/70 line-clamp-2 leading-relaxed">{post.caption || "No caption"}</p>
                      <div className="flex justify-between items-center text-[9px] text-white/40">
                        <span>❤️ {post.like_count}</span>
                        <span>💬 {post.comments_count}</span>
                      </div>
                    </div>
                  ))}
                  {kgData.instagram_posts.length === 0 && (
                    <p className="text-xs text-white/40 py-6 text-center w-full">No live Instagram posts found.</p>
                  )}
                </div>
              </div>

              {/* Paid Meta Campaigns */}
              <div className="space-y-3">
                <h5 className="text-[10px] font-bold uppercase tracking-wider text-white/50">Meta Ads Manager Campaigns</h5>
                <div className="rounded-xl border border-white/5 bg-black/50 overflow-hidden max-h-[300px] overflow-y-auto scrollbar-thin">
                  <table className="w-full text-left text-[10px]">
                    <thead className="bg-white/5 text-white/40 font-bold uppercase tracking-wider">
                      <tr>
                        <th className="p-2.5">Name</th>
                        <th className="p-2.5">Status</th>
                        <th className="p-2.5">Spend</th>
                        <th className="p-2.5">Clicks</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 text-white/80">
                      {kgData.meta_campaigns.map((c: any) => (
                        <tr key={c.id} className="hover:bg-white/5">
                          <td className="p-2.5 font-semibold truncate max-w-[120px]">{c.name}</td>
                          <td className="p-2.5">
                            <span className={`px-1.5 py-0.5 rounded-full text-[8px] font-black uppercase ${c.status === "ACTIVE" ? "bg-green-500/10 text-green-400" : "bg-white/10 text-white/50"}`}>
                              {c.status}
                            </span>
                          </td>
                          <td className="p-2.5">₹{c.spend.toFixed(0)}</td>
                          <td className="p-2.5">{c.clicks}</td>
                        </tr>
                      ))}
                      {kgData.meta_campaigns.length === 0 && (
                        <tr>
                          <td colSpan={4} className="p-6 text-center text-white/40">No active Meta Ads campaigns found.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* LLM Audit Summary */}
            <div className="p-4 rounded-xl border border-purple-500/15 bg-purple-500/5 space-y-2">
              <h5 className="text-[10px] font-bold uppercase tracking-wider text-purple-300">Auditor AI Analysis</h5>
              <div className="text-xs leading-relaxed text-white/80 whitespace-pre-wrap font-sans">
                {kgData.review}
              </div>
            </div>
          </section>
        )}

        {/* Enhanced Publisher Section */}
        <section
          className="rounded-xl p-6 border space-y-6 glass-panel hover-glow animate-fade-up stagger-2"
          style={{ boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)" }}
        >
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Quick Post Publisher</h4>
            <p className="text-[10px] text-white/40">Draft, preview, and dispatch multi-media content with AI optimizations.</p>
          </div>

          <div className="grid gap-6 lg:grid-cols-12">
            {/* Left Column: Post Form */}
            <div className="lg:col-span-7 space-y-4 flex flex-col justify-between">
              <div className="space-y-4">
                {/* Text Description */}
                <div className="space-y-2">
                  <label htmlFor="post-desc" className="text-[10px] font-bold text-white/40 uppercase tracking-wider">
                    Post Description
                  </label>
                  <textarea
                    id="post-desc"
                    value={composeText}
                    onChange={(event) => setComposeText(event.target.value)}
                    disabled={posting}
                    placeholder="Enter post description here..."
                    className="w-full min-h-24 rounded-xl px-4 py-3 text-xs bg-[#000000] border border-[rgba(255,255,255,0.08)] focus:border-[#388bfd] focus:outline-none transition-colors outline-none resize-none"
                  />
                  <button
                    type="button"
                    onClick={handleGenerateHashtags}
                    disabled={generatingHashtags || !composeText.trim()}
                    className="rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-1.5 text-[10px] font-semibold text-white transition-colors disabled:opacity-40"
                  >
                    {generatingHashtags ? "Generating AI Hashtags..." : "⚡ Generate AI Hashtags"}
                  </button>
                </div>

                {/* File Attachments */}
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider block">
                    Media Attachments (Max 10)
                  </span>
                  <div className="flex items-center gap-3">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileUpload}
                      multiple
                      accept="image/*,video/*"
                      className="hidden"
                    />
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading || mediaFiles.length >= 10}
                      className="px-4 py-2 rounded-lg text-xs font-semibold bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-colors disabled:opacity-40"
                    >
                      {uploading ? "Uploading..." : "📁 Attach Photos/Videos"}
                    </button>
                    <span className="text-[10px] text-white/40">
                      {mediaFiles.length} / 10 attached
                    </span>
                  </div>

                  {mediaFiles.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {mediaFiles.map((media) => (
                        <div key={media.id} className="relative h-12 w-12 rounded-lg overflow-hidden border border-white/10 bg-black group">
                          {media.file_type === "video" ? (
                            <div className="h-full w-full flex items-center justify-center bg-white/5 text-[9px] text-white/60">
                              📹 video
                            </div>
                          ) : (
                            <img
                              src={`${apiBaseUrl}${media.url}`}
                              alt={media.name}
                              className="h-full w-full object-cover"
                            />
                          )}
                          <button
                            type="button"
                            onClick={() => removeMedia(media.id)}
                            className="absolute top-0.5 right-0.5 bg-black/60 hover:bg-black text-white rounded-full p-0.5 text-[8px] h-3.5 w-3.5 flex items-center justify-center transition-colors"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Target Platforms */}
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider block">
                    Target Platforms
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {connectedPlatforms.map((connection) => {
                      const selected = selectedPlatforms.includes(connection.platform);
                      return (
                        <button
                          key={connection.platform}
                          onClick={() => togglePlatform(connection.platform)}
                          className="px-3 py-1 rounded-full text-xs font-semibold transition-all border"
                          style={{
                            background: selected ? "rgba(56,139,253,0.08)" : "transparent",
                            color: selected ? "#388bfd" : "#8b949e",
                            borderColor: selected ? "rgba(56,139,253,0.25)" : "rgba(255,255,255,0.08)",
                          }}
                        >
                          {selected ? "✓ " : "+ "}{formatPlatform(connection.platform)}
                        </button>
                      );
                    })}
                    {connectedPlatforms.length === 0 && (
                      <span className="text-xs text-[#f85149]">No platforms connected. Connect a platform first.</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-[rgba(255,255,255,0.04)] mt-4">
                <span className="text-xs" style={{ color: postResult?.startsWith("✓") ? "#3fb950" : "#f85149" }}>{postResult}</span>
                <button
                  onClick={() => setShowConfirmModal(true)}
                  disabled={posting || !composeText.trim() || selectedPlatforms.length === 0}
                  className="px-5 py-2.5 rounded-lg text-xs font-bold transition-all disabled:opacity-40 shadow-[0_4px_12px_rgba(35,134,54,0.2)]"
                  style={{ background: "#238636", color: "#fff", border: "1px solid rgba(255,255,255,0.05)" }}
                >
                  Publish Post
                </button>
              </div>
            </div>

            {/* Right Column: Platform Preview */}
            <div className="lg:col-span-5 border-t lg:border-t-0 lg:border-l border-white/5 pt-6 lg:pt-0 lg:pl-6 flex flex-col space-y-4">
              <div>
                <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider block">
                  Platform Feed Preview
                </span>
                <p className="text-[9px] text-white/30 mt-0.5">Toggle preview matching selected platforms.</p>
              </div>

              {/* Preview Platform Tabs */}
              <div className="flex gap-1.5 border-b border-white/5 pb-2">
                {(["instagram", "facebook", "linkedin"] as const).map((plat) => (
                  <button
                    key={plat}
                    onClick={() => {
                      setPreviewPlatform(plat);
                      setActiveCarouselIndex(0);
                    }}
                    className={`px-3 py-1 rounded-md text-[10px] font-semibold border transition-all ${
                      previewPlatform === plat
                        ? "bg-white/5 border-white/10 text-white"
                        : "border-transparent text-white/40 hover:text-white/70"
                    }`}
                  >
                    {plat === "instagram" ? "Instagram" : plat === "facebook" ? "Facebook" : "LinkedIn"}
                  </button>
                ))}
              </div>

              {/* Render Preview Frame */}
              <div className="flex-1 flex items-center justify-center p-2 rounded-xl bg-black/40 min-h-[300px]">
                {renderPlatformPreview(previewPlatform)}
              </div>
            </div>
          </div>
        </section>

        {/* Recent Operations */}
        <section
          className="rounded-xl p-5 border flex flex-col"
          style={{ background: "rgba(255,255,255,0.02)", borderColor: "rgba(255,255,255,0.06)" }}
        >
          <div className="space-y-4">
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Recent Operations</h4>
              <p className="text-[10px] text-white/40">Audit trail of generated, scheduled, and published posts.</p>
            </div>
            <div className="space-y-3 max-h-[300px] overflow-y-auto scrollbar-thin pr-1">
              {recentPosts.map((post) => (
                <div key={post.id} className="p-3 rounded-xl bg-[#000000] border border-[rgba(255,255,255,0.04)] space-y-2.5 hover:border-[#388bfd]/30 transition-all duration-200">
                  <p className="text-xs leading-relaxed text-white/80 line-clamp-2">{post.content || "Untitled post"}</p>
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex flex-wrap gap-1">
                      {post.platforms?.map((platform) => (
                        <span key={`${post.id}-${platform.platform}`} className="px-2 py-0.5 rounded-full text-[9px] font-bold border capitalize" style={{ background: "rgba(56,139,253,0.06)", color: "#388bfd", borderColor: "rgba(56,139,253,0.2)" }}>
                          {formatPlatform(platform.platform)} · {platform.status}
                        </span>
                      ))}
                    </div>
                    <span className="text-[10px] text-white/30 shrink-0">{timeAgo(post.created_at)}</span>
                  </div>
                </div>
              ))}
              {recentPosts.length === 0 && (
                <p className="text-xs text-white/40 text-center py-6">No recent operations yet.</p>
              )}
            </div>
          </div>
        </section>
      </div>

      {/* Confirmation Modal overlay */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-sm p-4">
          <div className="w-full max-w-[440px] rounded-2xl border border-white/10 bg-[#0c0c0c] p-6 shadow-2xl space-y-5">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Review & Confirm Post</h3>
              <p className="text-[10px] text-white/40 mt-1">Check post mockup and target platforms before scheduling.</p>
            </div>

            {/* Simulated Live Preview */}
            <div className="flex items-center justify-center py-4 bg-black/60 border border-white/5 rounded-xl">
              {renderPlatformPreview(previewPlatform)}
            </div>

            {/* Validation checks */}
            {selectedPlatforms.includes("instagram") && mediaFiles.length === 0 ? (
              <div className="p-3 rounded-xl border border-red-500/25 bg-red-500/10 text-[10px] text-red-200 leading-relaxed">
                ⚠️ **Instagram posting limit**: Instagram requires at least one image or video attachment to publish. Please close this window, select a media file, and try again.
              </div>
            ) : (
              <div className="p-3 rounded-xl border border-green-500/25 bg-green-500/10 text-[10px] text-green-200 leading-relaxed">
                ✓ Post format is valid for selected platforms. Ready to post.
              </div>
            )}

            <div className="flex items-center justify-between pt-4 border-t border-white/5 text-[10px]">
              <span className="text-white/40 font-bold uppercase tracking-wider">
                Platforms: {selectedPlatforms.map(formatPlatform).join(", ")}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowConfirmModal(false)}
                  className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 font-bold text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleQuickPost}
                  disabled={posting || (selectedPlatforms.includes("instagram") && mediaFiles.length === 0)}
                  className="px-4 py-2 rounded-lg bg-green-600 hover:bg-green-700 disabled:opacity-40 font-bold text-white transition-colors shadow-lg shadow-green-600/20"
                >
                  {posting ? "Publishing..." : "Confirm & Post"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
