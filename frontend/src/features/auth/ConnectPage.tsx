import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { apiBaseUrl, apiFetch } from "../../lib/api/client";

type Connection = {
  platform: string;
  account_name: string | null;
  account_id: string | null;
  connected: boolean;
  connected_at: string | null;
};

type ProviderStatus = {
  platform: string;
  label: string;
  configured: boolean;
  required_env: string[];
};

const PLATFORMS = [
  {
    id: "linkedin",
    name: "LinkedIn",
    requirement: "Personal profile with LinkedIn Share API access",
    gradient: "linear-gradient(135deg, #0077b5, #005885)",
    glyph: "in",
  },
  {
    id: "instagram",
    name: "Instagram",
    requirement: "Instagram Business account linked to a Facebook Page",
    gradient: "linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045)",
    glyph: "◎",
  },
  {
    id: "facebook",
    name: "Facebook Page",
    requirement: "Facebook Page with Meta app permissions",
    gradient: "linear-gradient(135deg, #1877f2, #0d5bbf)",
    glyph: "f",
  },
  {
    id: "x",
    name: "X (Twitter)",
    requirement: "X Developer app with OAuth 2.0 user-context permissions",
    gradient: "linear-gradient(135deg, #1a1a1a, #333)",
    glyph: "𝕏",
  },
  {
    id: "youtube",
    name: "YouTube",
    requirement: "Google OAuth app with YouTube Data API enabled",
    gradient: "linear-gradient(135deg, #ff0033, #cc0000)",
    glyph: "▶",
  },
];

export default function ConnectPage() {
  const { token, user, logout } = useAuth();
  const [connections, setConnections] = useState<Connection[]>([]);
  const [providers, setProviders] = useState<Record<string, ProviderStatus>>({});
  const [loading, setLoading] = useState(true);
  const [disconnecting, setDisconnecting] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get("success") === "true") {
      setMessage({ type: "success", text: `✓ Successfully connected ${params.get("connected")}!` });
    } else if (params.get("error")) {
      setMessage({
        type: "error",
        text: `Connection failed: ${params.get("description") || params.get("error")}`,
      });
    }

    setLoading(true);
    Promise.all([fetchProviders(), fetchConnections()]).finally(() => setLoading(false));
  }, [location.search, token]);

  const fetchProviders = async () => {
    try {
      const res = await apiFetch("/api/auth/providers");
      if (!res.ok) return;
      const data = await res.json();
      const providerMap = (data.providers ?? []).reduce(
        (acc: Record<string, ProviderStatus>, provider: ProviderStatus) => {
          acc[provider.platform] = provider;
          return acc;
        },
        {},
      );
      setProviders(providerMap);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchConnections = async () => {
    if (!token) return;
    try {
      const res = await apiFetch("/api/auth/connections", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setConnections(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  const isConnected = (platform: string) => connections.some((connection) => connection.platform === platform);
  const getConnection = (platform: string) => connections.find((connection) => connection.platform === platform);

  const handleConnect = (platform: string) => {
    if (!token) {
      setMessage({ type: "error", text: "Please sign in before connecting a platform." });
      return;
    }
    window.location.href = `${apiBaseUrl}/api/auth/${platform}/connect?user_id=${token}&sandbox=true`;
  };

  const handleDisconnect = async (platform: string) => {
    if (!window.confirm(`Disconnect ${platform}? This will stop posting to this platform.`)) return;
    setDisconnecting(platform);
    try {
      const res = await apiFetch(`/api/auth/${platform}/disconnect`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setConnections((current) => current.filter((connection) => connection.platform !== platform));
        setMessage({ type: "success", text: `Disconnected ${platform}` });
      } else {
        const data = await res.json().catch(() => null);
        setMessage({ type: "error", text: data?.detail ?? `Could not disconnect ${platform}` });
      }
    } catch (err) {
      setMessage({ type: "error", text: err instanceof Error ? err.message : "Disconnect failed" });
    } finally {
      setDisconnecting(null);
    }
  };

  const goDashboard = () => navigate(`/workspaces/${user?.id ?? 1}/dashboard`);
  const hasAnyConnection = connections.length > 0;

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ background: "#000000", color: "#ffffff", fontFamily: '"Plus Jakarta Sans", "Segoe UI", system-ui, sans-serif' }}
    >
      <header
        className="px-6 py-4 flex items-center justify-between"
        style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", background: "#000000" }}
      >
        <div className="flex items-center gap-3">
          <img
            src="/marko%20ai.png"
            alt="Marko AI"
            className="h-8 w-8 object-contain"
          />
          <span className="font-bold text-[1.05rem] tracking-tight text-white">Marko AI</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs mr-2" style={{ color: "#8b949e" }}>
            {user?.email}
          </span>
          <button
            onClick={logout}
            className="px-3 py-1.5 rounded-md text-xs font-medium transition-colors hover:text-white"
            style={{ background: "rgba(255,255,255,0.04)", color: "#8b949e", border: "1px solid rgba(255,255,255,0.08)" }}
          >
            Sign out
          </button>
        </div>
      </header>

      <div className="flex-1 flex flex-col items-center justify-start py-10 px-4">
        <div className="w-full max-w-2xl">
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-widest mb-2" style={{ color: "rgba(255,255,255,0.42)" }}>
              Platform Connections
            </p>
            <h1 className="text-2xl font-bold mb-2">Connect your social accounts</h1>
            <p className="text-sm" style={{ color: "#8b949e" }}>
              Link your social media platforms to start publishing content from Social Manager.
            </p>
          </div>

          {message && (
            <div
              className="mb-6 px-4 py-3 rounded-lg text-sm"
              style={{
                background: message.type === "success" ? "rgba(35,134,54,0.15)" : "rgba(218,54,51,0.15)",
                border: `1px solid ${message.type === "success" ? "rgba(35,134,54,0.3)" : "rgba(218,54,51,0.3)"}`,
                color: message.type === "success" ? "#3fb950" : "#f85149",
              }}
            >
              {message.text}
            </div>
          )}

          {hasAnyConnection && (
            <div
              className="mb-6 px-4 py-4 rounded-lg flex items-center justify-between"
              style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)" }}
            >
              <div>
                <p className="font-semibold text-sm text-white">
                  🎉 {connections.length} platform{connections.length > 1 ? "s" : ""} connected!
                </p>
                <p className="text-xs mt-0.5" style={{ color: "#8b949e" }}>
                  You're ready to manage and post to your social accounts.
                </p>
              </div>
              <button
                onClick={goDashboard}
                className="px-4 py-2.5 rounded-full text-xs font-bold transition-all hover:-translate-y-0.5 active:translate-y-0 hover:shadow-[0_12px_24px_rgba(255,255,255,0.12)] flex items-center gap-2 ml-4 shrink-0 btn-press"
                style={{ background: "#ffffff", color: "#000000" }}
              >
                Go to Dashboard →
              </button>
            </div>
          )}

          <div className="space-y-3">
            {PLATFORMS.map((platform) => {
              const connected = isConnected(platform.id);
              const conn = getConnection(platform.id);
              const provider = providers[platform.id];
              const configured = provider?.configured ?? true;
              const isDisconnecting = disconnecting === platform.id;

              return (
                <div
                  key={platform.id}
                  className="rounded-lg p-4 flex items-center justify-between transition-colors"
                  style={{
                    background: "#000000",
                    border: connected
                      ? "1px solid rgba(35,134,54,0.35)"
                      : configured
                        ? "1px solid rgba(255,255,255,0.04)"
                        : "1px solid rgba(210,153,34,0.35)",
                  }}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className="flex h-10 w-10 items-center justify-center rounded-lg shrink-0 text-lg font-black"
                      style={{ background: platform.gradient }}
                    >
                      {platform.glyph}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-sm">{platform.name}</h3>
                        {connected && (
                          <span
                            className="px-2 py-0.5 rounded-full text-xs font-medium"
                            style={{
                              background: "rgba(35,134,54,0.2)",
                              color: "#3fb950",
                              border: "1px solid rgba(35,134,54,0.3)",
                            }}
                          >
                            Connected
                          </span>
                        )}
                      </div>
                      {connected && conn ? (
                        <p className="text-xs mt-0.5" style={{ color: "#3fb950" }}>
                          @{conn.account_name || conn.account_id}
                        </p>
                      ) : !configured && provider ? (
                        <p className="text-xs mt-0.5" style={{ color: "#d29922" }}>
                          Missing backend env: {provider.required_env.join(", ")}
                        </p>
                      ) : (
                        <p className="text-xs mt-0.5" style={{ color: "#6e7681" }}>
                          {platform.requirement}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="shrink-0 ml-4">
                    {connected ? (
                      <button
                        onClick={() => handleDisconnect(platform.id)}
                        disabled={isDisconnecting}
                        className="px-3 py-1.5 rounded-md text-xs font-medium transition-colors disabled:opacity-50"
                        style={{
                          background: "rgba(218,54,51,0.1)",
                          color: "#f85149",
                          border: "1px solid rgba(218,54,51,0.25)",
                        }}
                      >
                        {isDisconnecting ? "Disconnecting…" : "Disconnect"}
                      </button>
                    ) : (
                      <button
                        onClick={() => handleConnect(platform.id)}
                        disabled={!configured}
                        className="px-3 py-1.5 rounded-md text-xs font-semibold transition-colors disabled:opacity-70 btn-press"
                        style={{
                          background: configured ? "#ffffff" : "rgba(255,255,255,0.08)",
                          color: configured ? "#000000" : "#8b949e",
                          border: configured ? "1px solid rgba(255,255,255,0.1)" : "1px solid #484f58",
                          cursor: configured ? "pointer" : "not-allowed",
                        }}
                      >
                        {configured ? "Connect" : "Needs keys"}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {loading && (
            <div className="mt-6 flex justify-center">
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-white/20 border-t-blue-400" />
            </div>
          )}

          {!hasAnyConnection && (
            <div className="mt-6 text-center">
              <button onClick={goDashboard} className="text-sm transition-colors hover:text-white" style={{ color: "#6e7681" }}>
                Skip for now — go to dashboard →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
