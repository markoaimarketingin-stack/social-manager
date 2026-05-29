import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../../features/auth/AuthContext";
import { apiBaseUrl } from "../../../lib/api/client";

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
    platforms: Array<{ platform: string; status: string; error?: string }>;
  }>;
}

const PLATFORM_COLORS: Record<string, { bg: string; text: string; border: string; icon: string }> = {
  linkedin: { bg: "rgba(0,119,181,0.15)", text: "#58a6ff", border: "rgba(0,119,181,0.3)", icon: "IN" },
  instagram: { bg: "rgba(225,48,108,0.15)", text: "#f78166", border: "rgba(225,48,108,0.3)", icon: "IG" },
  facebook: { bg: "rgba(24,119,242,0.15)", text: "#79c0ff", border: "rgba(24,119,242,0.3)", icon: "FB" },
  x: { bg: "rgba(255,255,255,0.08)", text: "#e6edf3", border: "rgba(255,255,255,0.15)", icon: "X" },
};

const STATUS_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  published: { bg: "rgba(35,134,54,0.15)", text: "#3fb950", border: "rgba(35,134,54,0.3)" },
  pending: { bg: "rgba(218,104,32,0.15)", text: "#f0883e", border: "rgba(218,104,32,0.3)" },
  processing: { bg: "rgba(56,139,253,0.15)", text: "#58a6ff", border: "rgba(56,139,253,0.3)" },
  scheduled: { bg: "rgba(56,139,253,0.15)", text: "#58a6ff", border: "rgba(56,139,253,0.3)" },
  failed: { bg: "rgba(218,54,51,0.15)", text: "#f85149", border: "rgba(218,54,51,0.3)" },
};

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function WorkspaceOverviewPage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [composeText, setComposeText] = useState("");
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBaseUrl}/api/dashboard/stats`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to load dashboard");
      const data = await res.json();
      setStats(data);
      // Pre-select all connected platforms
      setSelectedPlatforms(data.connected_platforms.map((p: any) => p.platform));
    } catch (e: any) {
      setError(e.message || "Failed to load dashboard stats");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPost = async () => {
    if (!composeText.trim() || selectedPlatforms.length === 0) return;
    setPosting(true);
    setPostResult(null);
    try {
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
        setTimeout(fetchStats, 1500);
      } else {
        const err = await res.json();
        setPostResult(`✗ Failed: ${err.detail || "Unknown error"}`);
      }
    } catch (e: any) {
      setPostResult(`✗ Error: ${e.message}`);
    } finally {
      setPosting(false);
    }
  };

  const togglePlatform = (platform: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platform) ? prev.filter((p) => p !== platform) : [...prev, platform]
    );
  };

  const cardStyle = {
    background: "#161b22",
    border: "1px solid #21262d",
    borderRadius: "8px",
  };

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <div className="text-center">
          <div
            className="mx-auto h-8 w-8 rounded-full border-2 border-t-blue-400 animate-spin mb-3"
            style={{ borderColor: "#21262d", borderTopColor: "#388bfd" }}
          />
          <p className="text-sm" style={{ color: "#6e7681" }}>Loading dashboard…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full w-full items-center justify-center p-8">
        <div className="text-center max-w-sm">
          <div className="text-4xl mb-4">⚠️</div>
          <p className="font-semibold mb-2" style={{ color: "#e6edf3" }}>Dashboard unavailable</p>
          <p className="text-sm mb-4" style={{ color: "#6e7681" }}>{error}</p>
          <button
            onClick={fetchStats}
            className="px-4 py-2 rounded-md text-sm font-medium"
            style={{ background: "#238636", color: "#fff" }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const hasConnections = (stats?.connected_platforms?.length ?? 0) > 0;

  return (
    <div
      className="min-h-full p-5 space-y-5"
      style={{ maxWidth: "1024px", margin: "0 auto" }}
    >
      {/* Welcome header */}
      <div>
        <h1 className="text-xl font-bold" style={{ color: "#e6edf3" }}>
          Welcome back{user?.name ? `, ${user.name.split(" ")[0]}` : ""}! 👋
        </h1>
        <p className="text-sm mt-1" style={{ color: "#6e7681" }}>
          {hasConnections
            ? `Managing ${stats!.connected_platforms.length} connected platform${stats!.connected_platforms.length > 1 ? "s" : ""}`
            : "Connect platforms to start posting"}
        </p>
      </div>

      {/* No connections CTA */}
      {!hasConnections && (
        <div
          className="rounded-lg p-6 text-center"
          style={{ background: "rgba(31,111,235,0.08)", border: "1px solid rgba(31,111,235,0.2)" }}
        >
          <div className="text-4xl mb-3">🔗</div>
          <h2 className="font-semibold mb-2" style={{ color: "#e6edf3" }}>No platforms connected yet</h2>
          <p className="text-sm mb-4" style={{ color: "#8b949e" }}>
            Connect LinkedIn, Instagram, Facebook, or X to start publishing content.
          </p>
          <button
            onClick={() => navigate("/connect")}
            className="px-5 py-2 rounded-md font-semibold text-sm"
            style={{ background: "#1f6feb", color: "#fff" }}
          >
            Connect Platforms →
          </button>
        </div>
      )}

      {/* Stats row */}
      {stats && (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {[
            { label: "Total Posts", value: stats.stats.total_posts, icon: "📝", color: "#388bfd" },
            { label: "Published", value: stats.stats.published, icon: "✅", color: "#3fb950" },
            { label: "Pending", value: stats.stats.pending, icon: "⏳", color: "#f0883e" },
            { label: "Failed", value: stats.stats.failed, icon: "❌", color: "#f85149" },
          ].map((stat) => (
            <div key={stat.label} style={cardStyle} className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">{stat.icon}</span>
                <span className="text-xs font-medium" style={{ color: "#6e7681" }}>{stat.label}</span>
              </div>
              <p className="text-2xl font-bold" style={{ color: stat.color }}>
                {stat.value}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Quick Compose */}
        {hasConnections && (
          <div style={cardStyle} className="p-4">
            <h2 className="font-semibold text-sm mb-3" style={{ color: "#e6edf3" }}>
              Quick Compose
            </h2>

            {/* Platform selector */}
            <div className="flex flex-wrap gap-2 mb-3">
              {stats!.connected_platforms.map((cp) => {
                const style = PLATFORM_COLORS[cp.platform] || PLATFORM_COLORS.x;
                const selected = selectedPlatforms.includes(cp.platform);
                return (
                  <button
                    key={cp.platform}
                    onClick={() => togglePlatform(cp.platform)}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium transition-all"
                    style={{
                      background: selected ? style.bg : "transparent",
                      color: selected ? style.text : "#484f58",
                      border: `1px solid ${selected ? style.border : "#30363d"}`,
                    }}
                  >
                    <span className="font-bold">{style.icon}</span>
                    <span className="capitalize">{cp.platform}</span>
                    {cp.account_name && (
                      <span style={{ color: selected ? style.text : "#484f58", opacity: 0.7 }}>
                        @{cp.account_name}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            <textarea
              value={composeText}
              onChange={(e) => setComposeText(e.target.value)}
              placeholder="Write your post content here… (or use the AI chat on the right)"
              rows={4}
              className="w-full rounded-md px-3 py-2 text-sm resize-none outline-none"
              style={{
                background: "#0d1117",
                border: "1px solid #21262d",
                color: "#e6edf3",
                fontFamily: "inherit",
              }}
              onFocus={(e) => { e.target.style.borderColor = "#388bfd"; }}
              onBlur={(e) => { e.target.style.borderColor = "#21262d"; }}
            />

            {postResult && (
              <p
                className="text-xs mt-2 px-3 py-2 rounded"
                style={{
                  background: postResult.startsWith("✓") ? "rgba(35,134,54,0.15)" : "rgba(218,54,51,0.15)",
                  color: postResult.startsWith("✓") ? "#3fb950" : "#f85149",
                  border: `1px solid ${postResult.startsWith("✓") ? "rgba(35,134,54,0.3)" : "rgba(218,54,51,0.3)"}`,
                }}
              >
                {postResult}
              </p>
            )}

            <div className="mt-3 flex items-center justify-between">
              <span className="text-xs" style={{ color: "#484f58" }}>
                {composeText.length} characters · {selectedPlatforms.length} platform{selectedPlatforms.length !== 1 ? "s" : ""} selected
              </span>
              <button
                onClick={handleQuickPost}
                disabled={posting || !composeText.trim() || selectedPlatforms.length === 0}
                className="flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-semibold transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                style={{ background: "#238636", color: "#fff" }}
                onMouseEnter={(e) => !posting && ((e.target as HTMLElement).style.background = "#2ea043")}
                onMouseLeave={(e) => !posting && ((e.target as HTMLElement).style.background = "#238636")}
              >
                {posting ? (
                  <>
                    <div className="h-3 w-3 animate-spin rounded-full border border-white/40 border-t-white" />
                    Posting…
                  </>
                ) : (
                  <>
                    <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current">
                      <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576 6.636 10.07Zm6.787-8.201L1.591 6.602l4.339 2.76 7.494-7.493Z"/>
                    </svg>
                    Post Now
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Connected Platforms */}
        <div style={cardStyle} className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-sm" style={{ color: "#e6edf3" }}>
              Connected Platforms
            </h2>
            <button
              onClick={() => navigate("/connect")}
              className="text-xs transition-colors"
              style={{ color: "#388bfd" }}
            >
              Manage →
            </button>
          </div>
          {hasConnections ? (
            <div className="space-y-2">
              {stats!.connected_platforms.map((cp) => {
                const style = PLATFORM_COLORS[cp.platform] || PLATFORM_COLORS.x;
                return (
                  <div
                    key={cp.platform}
                    className="flex items-center gap-3 rounded-md p-3"
                    style={{ background: "#0d1117", border: "1px solid #21262d" }}
                  >
                    <div
                      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-xs font-bold"
                      style={{ background: style.bg, color: style.text, border: `1px solid ${style.border}` }}
                    >
                      {style.icon}
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-sm capitalize" style={{ color: "#e6edf3" }}>
                        {cp.platform}
                      </p>
                      {cp.account_name && (
                        <p className="text-xs" style={{ color: "#6e7681" }}>
                          @{cp.account_name}
                        </p>
                      )}
                    </div>
                    <span
                      className="ml-auto px-2 py-0.5 rounded-full text-xs font-medium"
                      style={{ background: "rgba(35,134,54,0.15)", color: "#3fb950", border: "1px solid rgba(35,134,54,0.3)" }}
                    >
                      Active
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-6">
              <p className="text-sm mb-3" style={{ color: "#484f58" }}>No platforms connected</p>
              <button
                onClick={() => navigate("/connect")}
                className="px-4 py-2 rounded-md text-sm font-medium"
                style={{ background: "#1f6feb", color: "#fff" }}
              >
                Connect Now
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Recent Posts */}
      {stats && stats.recent_posts.length > 0 && (
        <div style={cardStyle} className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-sm" style={{ color: "#e6edf3" }}>
              Recent Posts
            </h2>
            <button
              onClick={fetchStats}
              className="text-xs transition-colors"
              style={{ color: "#388bfd" }}
            >
              Refresh
            </button>
          </div>
          <div className="space-y-2">
            {stats.recent_posts.map((post) => (
              <div
                key={post.id}
                className="rounded-md p-3"
                style={{ background: "#0d1117", border: "1px solid #21262d" }}
              >
                <div className="flex items-start justify-between gap-3">
                  <p
                    className="text-sm flex-1 min-w-0"
                    style={{ color: "#c9d1d9", lineHeight: "1.5", overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" }}
                  >
                    {post.content || "(no content)"}
                  </p>
                  <span className="text-xs shrink-0" style={{ color: "#484f58" }}>
                    {timeAgo(post.created_at)}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {post.platforms.map((pj) => {
                    const s = STATUS_STYLES[pj.status] || STATUS_STYLES.pending;
                    const pc = PLATFORM_COLORS[pj.platform] || PLATFORM_COLORS.x;
                    return (
                      <span
                        key={pj.platform}
                        className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs"
                        style={{ background: s.bg, color: s.text, border: `1px solid ${s.border}` }}
                        title={pj.error || ""}
                      >
                        <span style={{ color: pc.text }}>{pc.icon}</span>
                        {pj.status}
                        {pj.error && " ⚠"}
                      </span>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state for recent posts */}
      {stats && stats.recent_posts.length === 0 && hasConnections && (
        <div
          className="rounded-lg p-6 text-center"
          style={{ background: "#161b22", border: "1px solid #21262d" }}
        >
          <div className="text-3xl mb-3">📭</div>
          <p className="font-medium mb-1" style={{ color: "#e6edf3" }}>No posts yet</p>
          <p className="text-sm" style={{ color: "#6e7681" }}>
            Use Quick Compose above or talk to the AI assistant to create your first post.
          </p>
        </div>
      )}
    </div>
  );
}
