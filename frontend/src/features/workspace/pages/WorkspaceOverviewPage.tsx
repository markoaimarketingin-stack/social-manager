import { useEffect, useState } from "react";
import { useAuth } from "../../../features/auth/AuthContext";
import { useWorkspaceChrome } from "../components/WorkspaceChromeContext";
import { apiBaseUrl } from "../../../lib/api/client";
import { isDemoModeEnabled } from "../../../lib/api/mock";

interface DashboardStats {
  user: { id: number; email: string; name: string };
  connected_platforms: Array<{
    platform: string;
    account_name: string;
    account_id: string;
    connected_at: string;
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
    created_at: string;
    platforms: Array<{ platform: string; status: string; error: string | null }>;
  }>;
}

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return "Just now";
  const date = new Date(dateStr);
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
  if (seconds < 60) return "Just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function WorkspaceOverviewPage() {
  const { token } = useAuth();
  const { openKnowledgeBase, openTrainModal, pushToast } = useWorkspaceChrome();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [backendOffline, setBackendOffline] = useState(false);
  const [composeText, setComposeText] = useState("");
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<string | null>(null);
  const [runningAnalysis, setRunningAnalysis] = useState(false);
  const [customBackendInput, setCustomBackendInput] = useState(localStorage.getItem("custom_backend_url") || "");

  const handleSaveBackendUrl = () => {
    localStorage.setItem("custom_backend_url", customBackendInput.trim());
    pushToast("Backend URL updated! Retrying connection...");
    window.location.reload();
  };

  const togglePlatform = (platform: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platform) ? prev.filter((p) => p !== platform) : [...prev, platform]
    );
  };

  const fetchStats = async () => {
    setLoading(true);
    setBackendOffline(false);
    try {
      const res = await fetch(`${apiBaseUrl}/api/dashboard/stats`, {
        headers: { Authorization: `Bearer ${token}` },

      });
      if (!res.ok) throw new Error("Failed to load dashboard stats");
      const data = await res.json();
      setStats(data);
      setSelectedPlatforms(data.connected_platforms.map((p: any) => p.platform));
    } catch (e: any) {
      console.error("Dashboard stats fetch error:", e);
      if (isDemoModeEnabled()) {
        // Safe mock fallback for demo mode
        const mockData: DashboardStats = {
          user: { id: 1, email: "demo@markoai.com", name: "Demo Client" },
          connected_platforms: [
            { platform: "linkedin", account_name: "Demo Professional", account_id: "li_1", connected_at: new Date().toISOString() },
            { platform: "instagram", account_name: "@demosocial", account_id: "ig_1", connected_at: new Date().toISOString() },
          ],
          stats: { total_posts: 12, published: 8, pending: 3, failed: 1 },
          recent_posts: [
            {
              id: 1,
              content: "🚀 We are excited to announce our brand new social operations interface, built for speed and complete operational clarity. #saas #socialmarketing",
              created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
              platforms: [{ platform: "linkedin", status: "published", error: null }, { platform: "instagram", status: "published", error: null }]
            },
            {
              id: 2,
              content: "💡 Monday Tip: Authenticity builds audience loyalty faster than perfect production. Share behind-the-scenes stories today!",
              created_at: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
              platforms: [{ platform: "linkedin", status: "published", error: null }]
            },
            {
              id: 3,
              content: "How do you manage your weekly social strategy planning workflows? Tell us below!",
              created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
              platforms: [{ platform: "instagram", status: "published", error: null }]
            }
          ]
        };
        setStats(mockData);
        setSelectedPlatforms(mockData.connected_platforms.map((p) => p.platform));
      } else {
        // Flag backend offline so we can show a gorgeous prompt to run the backend or select demo mode
        setBackendOffline(true);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [token]);

  const handleQuickPost = async () => {
    if (!composeText.trim() || selectedPlatforms.length === 0) {
      pushToast("Please enter post content and select at least one platform.");
      return;
    }
    setPosting(true);
    setPostResult(null);
    try {
      if (isDemoModeEnabled()) {
        await new Promise((r) => setTimeout(r, 1000));
        
        // Add to local stats
        if (stats) {
          const newPost = {
            id: Date.now(),
            content: composeText,
            created_at: new Date().toISOString(),
            platforms: selectedPlatforms.map((p) => ({ platform: p, status: "published", error: null })),
          };
          setStats({
            ...stats,
            stats: {
              ...stats.stats,
              total_posts: stats.stats.total_posts + 1,
              published: stats.stats.published + selectedPlatforms.length,
            },
            recent_posts: [newPost, ...stats.recent_posts],
          });
        }
        
        setPostResult("✓ Post published successfully (Demo Mode)!");
        setComposeText("");
        pushToast("Post successfully published!");
      } else {
        const res = await fetch(`${apiBaseUrl}/api/publishing/schedule`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            platforms: selectedPlatforms,
            content: composeText,
          }),
        });
        if (res.ok) {
          setPostResult("✓ Post published successfully!");
          setComposeText("");
          pushToast("Post successfully published!");
          setTimeout(fetchStats, 1000);
        } else {
          const err = await res.json();
          setPostResult(`✗ Failed: ${err.detail || "Unknown error"}`);
        }
      }
    } catch (e: any) {
      setPostResult(`✗ Error: ${e.message}`);
    } finally {
      setPosting(false);
    }
  };

  const handleRunAnalysis = async () => {
    setRunningAnalysis(true);
    pushToast("Running workspace strategy refresh...");
    try {
      await new Promise((r) => setTimeout(r, 2000));
      pushToast("Analysis run completed successfully!");
    } catch (e) {
      pushToast("Failed to run analysis.");
    } finally {
      setRunningAnalysis(false);
    }
  };

  const handleEnableDemoMode = () => {
    localStorage.setItem("demo_mode_fallback", "true");
    window.location.reload();
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

  if (backendOffline) {
    const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

    return (
      <div className="flex h-full w-full items-center justify-center bg-[#0d1117] p-5 animate-fadeIn">
        <div
          className="w-full max-w-lg rounded-2xl p-6 text-white text-center space-y-6 animate-scaleIn"
          style={{
            background: "#161b22",
            border: "1px solid #30363d",
            boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
          }}
        >
          <div className="space-y-2">
            <span className="text-4xl">🔌</span>
            <h3 className="text-lg font-bold">
              {isLocalhost ? "Local Backend Offline" : "Backend Connection Offline"}
            </h3>
            <p className="text-xs text-white/40 max-w-sm mx-auto leading-relaxed">
              {isLocalhost
                ? "We couldn't establish a network connection to your local FastAPI backend server on port 8088."
                : "We couldn't connect to your FastAPI backend API server. If your server is hosted elsewhere, configure its URL below."}
            </p>
          </div>

          {/* Backend URL Input Section */}
          <div className="p-4 rounded-xl bg-[#0d1117] border border-[#21262d] text-left space-y-3">
            <label className="block">
              <span className="block text-[10px] uppercase font-bold text-white/50 tracking-wider mb-1.5">
                Deployed Backend API URL
              </span>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="https://your-backend-api.onrender.com"
                  value={customBackendInput}
                  onChange={(e) => setCustomBackendInput(e.target.value)}
                  className="flex-1 rounded-lg px-3.5 py-2 text-xs bg-[#161b22] border border-[#30363d] focus:border-[#388bfd] focus:outline-none transition-colors text-white"
                />
                <button
                  onClick={handleSaveBackendUrl}
                  className="px-4 py-2 rounded-lg text-xs font-bold bg-[#1f6feb] border border-white/5 text-white hover:bg-[#388bfd] transition-colors shrink-0"
                >
                  Save & Connect
                </button>
              </div>
              <span className="text-[9px] text-white/30 mt-1.5 block">
                Stores your production API base URL locally (e.g. Render, Railway, AWS). Leave blank to use localhost:8088.
              </span>
            </label>
          </div>

          {/* Localhost startup command instruction */}
          {isLocalhost && (
            <div className="p-4 rounded-xl bg-[#0d1117] border border-[#21262d] text-left space-y-2">
              <p className="text-[10px] uppercase font-bold text-white/50 tracking-wider">How to start backend locally:</p>
              <code className="block text-[11px] font-mono text-blue-400 bg-black/40 p-2.5 rounded-lg select-all overflow-x-auto">
                cd backend &amp;&amp; uvicorn app.main:app --reload --host 127.0.0.1 --port 8088
              </code>
            </div>
          )}

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={fetchStats}
              className="w-full sm:w-auto px-5 py-2.5 rounded-lg text-xs font-bold transition-all border border-[#30363d] hover:bg-white/5"
            >
              🔄 Retry Connection
            </button>
            <button
              onClick={handleEnableDemoMode}
              className="w-full sm:w-auto px-5 py-2.5 rounded-lg text-xs font-bold transition-all shadow-[0_4px_12px_rgba(31,111,235,0.2)]"
              style={{
                background: "#1f6feb",
                color: "#fff",
                border: "1px solid rgba(255,255,255,0.1)",
              }}
            >
              🚀 Explore in Demo Mode
            </button>
          </div>
        </div>
      </div>
    );
  }

  const statsList = [
    { label: "Total Posts", value: stats?.stats.total_posts ?? 0, icon: "📝", color: "#388bfd", bg: "rgba(56,139,253,0.08)", border: "rgba(56,139,253,0.25)" },
    { label: "Published", value: stats?.stats.published ?? 0, icon: "✓", color: "#3fb950", bg: "rgba(56,139,253,0.08)", border: "rgba(63,185,80,0.25)" },
    { label: "Pending", value: stats?.stats.pending ?? 0, icon: "⏳", color: "#d29922", bg: "rgba(210,153,34,0.08)", border: "rgba(210,153,34,0.25)" },
    { label: "Failed", value: stats?.stats.failed ?? 0, icon: "❌", color: "#f85149", bg: "rgba(248,81,73,0.08)", border: "rgba(248,81,73,0.25)" },
  ];

  return (
    <div className="flex flex-col h-full w-full bg-[#0d1117] text-white">
      
      {/* Premium Dashboard Header */}
      <header
        className="flex items-center justify-between px-6 py-4 shrink-0 bg-[#06090e]/60 backdrop-blur"
        style={{ borderBottom: "1px solid #161b22" }}
      >
        <div className="flex items-center gap-3">
          <div
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/5 border border-white/10 text-white/80 shadow-[0_0_15px_rgba(255,255,255,0.03)]"
          >
            📊
          </div>
          <div>
            <h2 className="text-sm font-bold tracking-wide">Supervisor</h2>
            <p className="text-[9px] uppercase tracking-[0.25em]" style={{ color: "#388bfd" }}>Orchestrator</p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={openKnowledgeBase}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-[#30363d] hover:bg-white/5 transition-all text-white/80"
          >
            📖 Knowledge Base
          </button>
          <button
            onClick={openTrainModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-[#30363d] hover:bg-white/5 transition-all text-white/80"
          >
            + Train Model
          </button>
          <button
            onClick={handleRunAnalysis}
            disabled={runningAnalysis}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-[0_4px_12px_rgba(31,111,235,0.25)] disabled:opacity-50"
            style={{
              background: "linear-gradient(135deg, #1f6feb, #388bfd)",
              color: "#fff",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            ▶ {runningAnalysis ? "Analyzing..." : "Run Analysis"}
          </button>
        </div>
      </header>

      {/* Main Overview Body */}
      <div className="flex-1 overflow-y-auto p-6 scrollbar-thin space-y-6">
        
        {/* Supervisor Welcome Center */}
        <section
          className="rounded-2xl p-8 text-center space-y-4 border relative overflow-hidden"
          style={{
            background: "radial-gradient(circle at top, rgba(31,111,235,0.06), transparent), #161b22",
            borderColor: "#30363d",
          }}
        >
          {/* Glowing orbital compass */}
          <div
            className="mx-auto flex h-20 w-20 items-center justify-center rounded-full relative shadow-[0_0_35px_rgba(56,139,253,0.15)] border-2 border-white/5 cursor-pointer hover:scale-105 active:scale-95 transition-transform"
            style={{ background: "#0d1117" }}
          >
            <div className="absolute inset-0.5 rounded-full border border-dashed border-[#388bfd]/30 animate-[spin_60s_linear_infinite]" />
            <svg viewBox="0 0 24 24" className="h-10 w-10 text-[#388bfd] fill-none stroke-current" strokeWidth="1.5">
              <circle cx="12" cy="12" r="10" />
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
            </svg>
          </div>

          <div className="space-y-1">
            <h3 className="text-lg font-bold tracking-wide">I am your Social Media Supervisor</h3>
            <p className="text-xs text-white/50 max-w-md mx-auto leading-relaxed">
              Specialized in brand strategy, audience engagement, copywriting, A/B testing, and cross-platform publishing.
            </p>
          </div>
        </section>

        {/* Stats Section */}
        <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
          {statsList.map((stat) => (
            <div
              key={stat.label}
              className="p-4 rounded-xl border flex items-center justify-between"
              style={{ background: "#161b22", borderColor: "#30363d" }}
            >
              <div>
                <p className="text-[10px] font-bold text-white/40 uppercase tracking-wider">{stat.label}</p>
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

        {/* Main Work Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Quick Publish / Compose */}
          <div
            className="rounded-2xl p-5 border flex flex-col justify-between"
            style={{ background: "#161b22", borderColor: "#30363d" }}
          >
            <div className="space-y-4">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Quick Post Publisher</h4>
                <p className="text-[10px] text-white/40">Craft and publish content directly from the supervisor board.</p>
              </div>

              {/* Compose Textarea */}
              <textarea
                value={composeText}
                onChange={(e) => setComposeText(e.target.value)}
                disabled={posting}
                placeholder="What would you like to post? e.g. Share an industry tip or product launch update..."
                className="w-full min-h-24 rounded-xl px-4.5 py-3 text-xs bg-[#0d1117] border border-[#30363d] focus:border-[#388bfd] focus:outline-none transition-colors outline-none resize-none"
              />

              {/* Platform selection */}
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider block">Target Platforms</span>
                <div className="flex flex-wrap gap-2">
                  {stats?.connected_platforms.map((cp) => {
                    const selected = selectedPlatforms.includes(cp.platform);
                    return (
                      <button
                        key={cp.platform}
                        onClick={() => togglePlatform(cp.platform)}
                        className="px-3 py-1 rounded-full text-xs font-semibold transition-all border"
                        style={{
                          background: selected ? "rgba(56,139,253,0.08)" : "transparent",
                          color: selected ? "#388bfd" : "#8b949e",
                          borderColor: selected ? "rgba(56,139,253,0.25)" : "#30363d",
                        }}
                      >
                        {cp.platform.charAt(0).toUpperCase() + cp.platform.slice(1)}
                      </button>
                    );
                  })}
                  {stats?.connected_platforms.length === 0 && (
                    <span className="text-xs text-[#f85149]">No platforms connected. Please connect platforms first.</span>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-[#21262d] mt-4">
              <span className="text-xs" style={{ color: postResult?.startsWith("✓") ? "#3fb950" : "#f85149" }}>
                {postResult}
              </span>
              <button
                onClick={handleQuickPost}
                disabled={posting || !composeText.trim() || selectedPlatforms.length === 0}
                className="px-4 py-2 rounded-lg text-xs font-bold transition-all disabled:opacity-40 shadow-[0_4px_12px_rgba(35,134,54,0.2)]"
                style={{
                  background: "#238636",
                  color: "#fff",
                  border: "1px solid rgba(255,255,255,0.05)",
                }}
              >
                {posting ? "Publishing..." : "Publish Post"}
              </button>
            </div>
          </div>

          {/* Recent Operations log */}
          <div
            className="rounded-2xl p-5 border flex flex-col"
            style={{ background: "#161b22", borderColor: "#30363d" }}
          >
            <div className="space-y-4">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-white/60">Recent Operations</h4>
                <p className="text-[10px] text-white/40">Audit trail of posts generated and scheduled by this workspace.</p>
              </div>

              {/* Operations List */}
              <div className="space-y-3 max-h-[300px] overflow-y-auto scrollbar-thin pr-1">
                {stats?.recent_posts.map((post) => (
                  <div
                    key={post.id}
                    className="p-3 rounded-xl bg-[#0d1117] border border-[#21262d] space-y-2.5 hover:border-[#388bfd]/30 transition-all duration-200"
                  >
                    <p className="text-xs leading-relaxed text-white/80 line-clamp-2">{post.content}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex gap-1">
                        {post.platforms.map((p) => (
                          <span
                            key={p.platform}
                            className="px-2 py-0.5 rounded-full text-[9px] font-bold border capitalize"
                            style={{
                              background: "rgba(56,139,253,0.06)",
                              color: "#388bfd",
                              borderColor: "rgba(56,139,253,0.2)",
                            }}
                          >
                            {p.platform}
                          </span>
                        ))}
                      </div>
                      <span className="text-[10px] text-white/30">{timeAgo(post.created_at)}</span>
                    </div>
                  </div>
                ))}
                {stats?.recent_posts.length === 0 && (
                  <p className="text-xs text-white/40 text-center py-6">No recent operations found.</p>
                )}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
