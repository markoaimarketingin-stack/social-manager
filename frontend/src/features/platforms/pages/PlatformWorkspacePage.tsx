import { Link, Navigate, useParams } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { apiFetch } from "../../../lib/api/client";
import { getPlatformWorkspace } from "../platformWorkspaces";

type Connection = {
  platform: string;
  account_name?: string | null;
  account_id?: string | null;
  connected_at?: string | null;
};

type Provider = {
  platform: string;
  label?: string;
  configured?: boolean;
  env_token_configured?: boolean;
  requirements?: string[];
};

type QueueItem = {
  id: number;
  content?: string;
  scheduled_at?: string | null;
  jobs?: Array<{ platform: string; status: string; error?: string | null }>;
};

type DashboardStats = {
  connected_platforms?: Connection[];
  recent_posts?: Array<{
    id: number;
    content?: string;
    created_at?: string | null;
    platforms?: Array<{ platform: string; status: string; error?: string | null }>;
  }>;
  stats?: {
    total_posts: number;
    published: number;
    pending: number;
    failed: number;
  };
};

function Panel({
  title,
  eyebrow,
  children,
  className = "",
}: {
  title: string;
  eyebrow?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-2xl border border-white/10 bg-[#000000] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] ${className}`}>
      {eyebrow && <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/40">{eyebrow}</p>}
      <h2 className="mt-1 text-base font-bold text-white">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function formatDate(value?: string | null) {
  if (!value) return "Not scheduled";
  return new Date(value).toLocaleString();
}

function formatStatus(status?: string) {
  if (!status) return "Unknown";
  return status.replace(/_/g, " ");
}

export function PlatformWorkspacePage() {
  const { platformSlug, workspaceId } = useParams();
  const platform = getPlatformWorkspace(platformSlug);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [dashboard, setDashboard] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadPlatformData() {
      setLoading(true);
      setError(null);
      try {
        const [connectionsRes, providersRes, queueRes, dashboardRes] = await Promise.all([
          apiFetch("/api/auth/connections"),
          apiFetch("/api/auth/providers"),
          apiFetch("/api/publishing/queue"),
          apiFetch("/api/dashboard/stats"),
        ]);

        const nextConnections = connectionsRes.ok ? await connectionsRes.json() : [];
        const providerPayload = providersRes.ok ? await providersRes.json() : { providers: [] };
        const nextQueue = queueRes.ok ? await queueRes.json() : [];
        const nextDashboard = dashboardRes.ok ? await dashboardRes.json() : null;

        if (!cancelled) {
          setConnections(Array.isArray(nextConnections) ? nextConnections : []);
          setProviders(providerPayload.providers ?? []);
          setQueue(Array.isArray(nextQueue) ? nextQueue : []);
          setDashboard(nextDashboard);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Could not load platform workspace data.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadPlatformData();
    return () => {
      cancelled = true;
    };
  }, []);

  const platformQueue = useMemo(() => {
    if (!platform) return [];
    return queue.filter((item) => item.jobs?.some((job) => job.platform === platform.key));
  }, [platform, queue]);

  const recentActivity = useMemo(() => {
    if (!platform) return [];
    return (dashboard?.recent_posts ?? []).filter((post) =>
      post.platforms?.some((postPlatform) => postPlatform.platform === platform.key),
    );
  }, [dashboard, platform]);

  if (!platform) {
    return <Navigate replace to={`/workspaces/${workspaceId}/dashboard`} />;
  }

  const connection = connections.find((item) => item.platform === platform.key);
  const provider = providers.find((item) => item.platform === platform.key);
  const isConnected = Boolean(connection);
  const isProviderReady = Boolean(provider?.configured || provider?.env_token_configured);
  const platformJobs = platformQueue.flatMap((item) => item.jobs?.filter((job) => job.platform === platform.key) ?? []);
  const published = platformJobs.filter((job) => job.status === "published").length;
  const failed = platformJobs.filter((job) => job.status === "failed").length;
  const pending = platformJobs.filter((job) => ["pending", "scheduled", "processing"].includes(job.status)).length;

  return (
    <div className="min-h-full bg-black p-6 text-white">
      <div className="mx-auto max-w-7xl space-y-6">
        <header
          className="overflow-hidden rounded-3xl border border-white/10 bg-[#000000] p-6 shadow-[0_24px_80px_rgba(0,0,0,0.35)]"
          style={{ boxShadow: `0 0 0 1px ${platform.accent}22, 0 24px 80px rgba(0,0,0,0.35)` }}
        >
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-[11px] font-black uppercase tracking-[0.28em]" style={{ color: platform.accent }}>
                Channel Workspace
              </p>
              <h1 className="mt-2 text-3xl font-black tracking-tight">{platform.label}</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-white/60">{platform.description}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Link
                to="/connect"
                className="rounded-xl border border-white/10 bg-[#000000] px-4 py-2 text-xs font-bold text-white no-underline hover:bg-white/[0.08]"
              >
                {isConnected ? "Manage Connection" : "Connect Account"}
              </Link>
              <Link
                to={`/workspaces/${workspaceId}/publishing`}
                className="rounded-xl px-4 py-2 text-xs font-bold text-black no-underline"
                style={{ background: platform.accent }}
              >
                Open Publisher
              </Link>
            </div>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ["Connection", isConnected ? "Connected" : "Not connected"],
              ["Provider", isProviderReady ? "Ready" : "Needs keys"],
              ["Queue", `${platformQueue.length} posts`],
              ["Failures", `${failed} failed`],
            ].map(([label, value]) => (
              <div key={label} className="rounded-2xl border border-white/10 bg-black/30 p-4">
                <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/35">{label}</p>
                <p className="mt-2 text-lg font-black">{value}</p>
              </div>
            ))}
          </div>
        </header>

        {error && (
          <div className="rounded-2xl border border-red-500/25 bg-red-500/10 p-4 text-sm text-red-200">
            {error}
          </div>
        )}

        <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
          <Panel title="Platform Overview" eyebrow="Operating Focus">
            <p className="text-sm leading-6 text-white/65">{platform.publishingFocus}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {platform.contentFormats.map((format) => (
                <span key={format} className="rounded-full border border-white/10 bg-[#000000] px-3 py-1 text-xs text-white/70">
                  {format}
                </span>
              ))}
            </div>
          </Panel>

          <Panel title="Connected Account" eyebrow="Identity">
            {loading ? (
              <p className="text-sm text-white/50">Checking connection...</p>
            ) : isConnected ? (
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between gap-3 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3">
                  <span className="font-semibold text-emerald-200">{connection?.account_name || platform.label}</span>
                  <span className="text-xs text-emerald-300">Active</span>
                </div>
                <p className="text-white/50">Account ID: {connection?.account_id || "Not returned by provider"}</p>
                <p className="text-white/50">Connected: {formatDate(connection?.connected_at)}</p>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-white/60">No account connected yet. Connect this channel to publish from MarkoAI.</p>
                <Link to="/connect" className="inline-flex rounded-xl bg-[#238636] px-4 py-2 text-xs font-bold text-white no-underline">
                  Connect {platform.label}
                </Link>
              </div>
            )}
          </Panel>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          <Panel title="Publishing Status" eyebrow="Queue Health">
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="rounded-xl border border-white/10 bg-[#000000] p-3">
                <p className="text-xl font-black text-emerald-400">{published}</p>
                <p className="text-[10px] uppercase tracking-wider text-white/35">Published</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-[#000000] p-3">
                <p className="text-xl font-black text-amber-400">{pending}</p>
                <p className="text-[10px] uppercase tracking-wider text-white/35">Pending</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-[#000000] p-3">
                <p className="text-xl font-black text-red-400">{failed}</p>
                <p className="text-[10px] uppercase tracking-wider text-white/35">Failed</p>
              </div>
            </div>
          </Panel>

          <Panel title="Scheduled Content" eyebrow="Calendar">
            {platformQueue.length > 0 ? (
              <div className="space-y-3">
                {platformQueue.slice(0, 3).map((item) => (
                  <div key={item.id} className="rounded-xl border border-white/10 bg-[#000000] p-3">
                    <p className="line-clamp-2 text-xs text-white/75">{item.content || "Untitled post"}</p>
                    <p className="mt-2 text-[10px] uppercase tracking-wider text-white/35">{formatDate(item.scheduled_at)}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-white/50">No scheduled {platform.label} content yet. Use Publisher or Supervisor to create one.</p>
            )}
          </Panel>

          <Panel title="Draft Queue" eyebrow="Creation Pipeline">
            <p className="text-sm text-white/55">
              Drafts are created through Supervisor, Copywriter, Planning, or Publisher. Platform-specific draft persistence is ready for a backend draft endpoint.
            </p>
          </Panel>
        </div>

        <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
          <Panel title="Recent Activity" eyebrow="Operations">
            {recentActivity.length > 0 ? (
              <div className="space-y-3">
                {recentActivity.slice(0, 5).map((post) => {
                  const status = post.platforms?.find((item) => item.platform === platform.key)?.status;
                  return (
                    <div key={post.id} className="rounded-xl border border-white/10 bg-[#000000] p-3">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-xs font-bold text-white/80">Post #{post.id}</p>
                        <span className="rounded-full border border-white/10 px-2 py-0.5 text-[10px] capitalize text-white/55">
                          {formatStatus(status)}
                        </span>
                      </div>
                      <p className="mt-2 line-clamp-2 text-xs text-white/55">{post.content || "No content preview"}</p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-white/50">No recent {platform.label} operations yet.</p>
            )}
          </Panel>

          <Panel title="Platform Insights" eyebrow="Readiness">
            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-xl border border-white/10 bg-[#000000] p-4">
                <p className="text-xs font-bold text-white/70">API readiness</p>
                <p className="mt-2 text-sm text-white/55">
                  {isProviderReady
                    ? "Provider configuration is available for connection or publishing."
                    : "Provider keys/scopes are not configured yet. Use backend .env values before production testing."}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-[#000000] p-4">
                <p className="text-xs font-bold text-white/70">Metrics ingestion</p>
                <p className="mt-2 text-sm text-white/55">
                  Placeholder panel for future reach, engagement, saves, clicks, comments, and post-level performance endpoints.
                </p>
              </div>
            </div>
          </Panel>
        </div>

        <Panel title="Platform-Specific Notes" eyebrow="Implementation">
          <ul className="grid gap-3 md:grid-cols-3">
            {platform.operatingNotes.map((note) => (
              <li key={note} className="rounded-xl border border-white/10 bg-[#000000] p-4 text-sm leading-6 text-white/60">
                {note}
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </div>
  );
}
