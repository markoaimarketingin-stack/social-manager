import { useEffect, useState } from "react";

import { useAuth } from "../../../features/auth/AuthContext";
import { apiFetch } from "../../../lib/api/client";
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
  const [runningAnalysis, setRunningAnalysis] = useState(false);
  const [analysis, setAnalysis] = useState<SupervisorAnalysis | null>(null);

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

  useEffect(() => {
    fetchStats();
  }, [token]);

  const togglePlatform = (platform: string) => {
    setSelectedPlatforms((current) =>
      current.includes(platform) ? current.filter((item) => item !== platform) : [...current, platform],
    );
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
        }),
      });

      if (!res.ok) {
        const payload = await res.json().catch(() => null);
        throw new Error(payload?.detail ?? "Publishing request failed");
      }

      setPostResult("✓ Post queued for publishing.");
      setComposeText("");
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

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-[#0d1117]">
        <div className="text-center space-y-2.5">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-white/20 border-t-blue-400 mx-auto" />
          <p className="text-xs text-white/40">Loading supervisor overview...</p>
        </div>
      </div>
    );
  }

  const connectedPlatforms = stats?.connected_platforms ?? [];
  const recentPosts = stats?.recent_posts ?? [];
  const statsList = [
    { label: "Total Posts", value: stats?.stats.total_posts ?? 0, icon: "✍", color: "#388bfd", bg: "rgba(56,139,253,0.08)", border: "rgba(56,139,253,0.25)" },
    { label: "Published", value: stats?.stats.published ?? 0, icon: "✓", color: "#3fb950", bg: "rgba(63,185,80,0.08)", border: "rgba(63,185,80,0.25)" },
    { label: "Pending", value: stats?.stats.pending ?? 0, icon: "⌛", color: "#d29922", bg: "rgba(210,153,34,0.08)", border: "rgba(210,153,34,0.25)" },
    { label: "Failed", value: stats?.stats.failed ?? 0, icon: "×", color: "#f85149", bg: "rgba(248,81,73,0.08)", border: "rgba(248,81,73,0.25)" },
  ];

  return (
    <div className="flex h-full w-full flex-col bg-black text-white">
      <div className="mx-auto flex w-full max-w-[980px] flex-1 flex-col space-y-6 overflow-y-auto px-6 py-8 scrollbar-thin">
        <div className="flex justify-end">
          <button
            onClick={handleRunAnalysis}
            disabled={runningAnalysis}
            className="rounded-lg border border-white/15 bg-white/[0.04] px-4 py-2 text-xs font-bold text-white/80 transition hover:bg-white/[0.08] disabled:opacity-50"
          >
            {runningAnalysis ? "Analyzing..." : "Run Analysis"}
          </button>
        </div>
        {loadError && (
          <div className="rounded-xl border border-red-500/25 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {loadError}
          </div>
        )}
        <section className="rounded-2xl p-8 text-center space-y-4 border relative overflow-hidden" style={{ background: "radial-gradient(circle at top, rgba(31,111,235,0.06), transparent), #161b22", borderColor: "#30363d" }}>
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full relative shadow-[0_0_35px_rgba(56,139,253,0.15)] border-2 border-white/5" style={{ background: "#0d1117" }}>
            <div className="absolute inset-0.5 rounded-full border border-dashed border-[#388bfd]/30 animate-[spin_60s_linear_infinite]" />
            <svg viewBox="0 0 24 24" className="h-10 w-10 text-[#388bfd] fill-none stroke-current" strokeWidth="1.5">
              <circle cx="12" cy="12" r="10" />
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
            </svg>
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-bold tracking-wide">I am your Social Media Supervisor</h3>
            <p className="text-xs text-white/50 max-w-md mx-auto leading-relaxed">
              Monitoring platform connections, publishing queue health, knowledge context, and operational readiness.
            </p>
          </div>
        </section>

        <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
          {statsList.map((stat) => (
            <div key={stat.label} className="p-4 rounded-xl border flex items-center justify-between" style={{ background: "#161b22", borderColor: "#30363d" }}>
              <div>
                <p className="text-[10px] font-bold text-white/40 uppercase tracking-wider">{stat.label}</p>
                <h4 className="text-xl font-bold mt-1" style={{ color: stat.color }}>{stat.value}</h4>
              </div>
              <div className="h-8 w-8 rounded-lg flex items-center justify-center text-sm font-bold border" style={{ background: stat.bg, color: stat.color, borderColor: stat.border }}>
                {stat.icon}
              </div>
            </div>
          ))}
        </div>

        {analysis && (
          <section className="rounded-2xl p-5 border" style={{ background: "#161b22", borderColor: analysis.backend === "ok" ? "rgba(63,185,80,0.25)" : "rgba(248,81,73,0.35)" }}>
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
                <div key={item} className="rounded-xl border border-[#21262d] bg-[#0d1117] p-3 text-xs leading-6 text-white/65">
                  {item}
                </div>
              ))}
            </div>
          </section>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl p-5 border flex flex-col justify-between" style={{ background: "#161b22", borderColor: "#30363d" }}>
            <div className="space-y-4">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Quick Post Publisher</h4>
                <p className="text-[10px] text-white/40">Draft and dispatch content to connected platforms.</p>
              </div>
              <textarea
                value={composeText}
                onChange={(event) => setComposeText(event.target.value)}
                disabled={posting}
                placeholder="What would you like to post?"
                className="w-full min-h-24 rounded-xl px-4 py-3 text-xs bg-[#0d1117] border border-[#30363d] focus:border-[#388bfd] focus:outline-none transition-colors outline-none resize-none"
              />
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider block">Target Platforms</span>
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
                          borderColor: selected ? "rgba(56,139,253,0.25)" : "#30363d",
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
            <div className="flex items-center justify-between pt-4 border-t border-[#21262d] mt-4">
              <span className="text-xs" style={{ color: postResult?.startsWith("✓") ? "#3fb950" : "#f85149" }}>{postResult}</span>
              <button
                onClick={handleQuickPost}
                disabled={posting || !composeText.trim() || selectedPlatforms.length === 0}
                className="px-4 py-2 rounded-lg text-xs font-bold transition-all disabled:opacity-40 shadow-[0_4px_12px_rgba(35,134,54,0.2)]"
                style={{ background: "#238636", color: "#fff", border: "1px solid rgba(255,255,255,0.05)" }}
              >
                {posting ? "Publishing..." : "Publish Post"}
              </button>
            </div>
          </div>

          <div className="rounded-2xl p-5 border flex flex-col" style={{ background: "#161b22", borderColor: "#30363d" }}>
            <div className="space-y-4">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Recent Operations</h4>
                <p className="text-[10px] text-white/40">Audit trail of generated, scheduled, and published posts.</p>
              </div>
              <div className="space-y-3 max-h-[300px] overflow-y-auto scrollbar-thin pr-1">
                {recentPosts.map((post) => (
                  <div key={post.id} className="p-3 rounded-xl bg-[#0d1117] border border-[#21262d] space-y-2.5 hover:border-[#388bfd]/30 transition-all duration-200">
                    <p className="text-xs leading-relaxed text-white/80 line-clamp-2">{post.content || "Untitled post"}</p>
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex flex-wrap gap-1">
                        {post.platforms.map((platform) => (
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
          </div>
        </div>
      </div>
    </div>
  );
}


