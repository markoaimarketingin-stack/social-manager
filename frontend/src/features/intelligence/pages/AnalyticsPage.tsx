import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../../../lib/api/client";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { Panel } from "../../../components/ui/Panel";
import { StatusPill } from "../../../components/ui/StatusPill";

interface PerformanceMetric {
  platform: string;
  likes: number;
  comments: number;
  shares: number;
  engagementRate: number;
  reach: number;
  growth: number;
}

const PLATFORMS_CONFIG = [
  { key: "instagram", name: "Instagram" },
  { key: "facebook", name: "Facebook" },
  { key: "linkedin", name: "LinkedIn" },
  { key: "x", name: "X" },
  { key: "youtube", name: "YouTube" },
];

export function AnalyticsPage() {
  const [selectedPlatform, setSelectedPlatform] = useState<string>("All");

  const { data: metricsData, isLoading } = useQuery({
    queryKey: ["realMetricsComparison"],
    queryFn: () => apiGet<{ platforms: Record<string, any> }>("/api/real/metrics/comparison"),
  });

  if (isLoading) {
    return (
      <div className="mx-auto flex h-64 w-full max-w-6xl items-center justify-center bg-[#000000] text-white animate-pulse">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-blue-400" />
      </div>
    );
  }

  const platformsMap = metricsData?.platforms || {};
  const metricsList: PerformanceMetric[] = PLATFORMS_CONFIG.map((p) => {
    const platData = platformsMap[p.key] || {};
    return {
      platform: p.name,
      likes: platData.total_likes || 0,
      comments: platData.total_comments || 0,
      shares: platData.total_shares || 0,
      engagementRate: platData.average_engagement_rate || 0.0,
      reach: platData.total_reach || 0,
      growth: platData.follower_growth || 0,
    };
  });

  const filteredMetrics = selectedPlatform === "All"
    ? metricsList
    : metricsList.filter((m) => m.platform === selectedPlatform);

  const totalReach = filteredMetrics.reduce((acc, curr) => acc + curr.reach, 0);
  const avgEngagement = filteredMetrics.length > 0
    ? Number((filteredMetrics.reduce((acc, curr) => acc + curr.engagementRate, 0) / filteredMetrics.length).toFixed(1))
    : 0;
  const avgGrowth = filteredMetrics.length > 0
    ? Number((filteredMetrics.reduce((acc, curr) => acc + curr.growth, 0) / filteredMetrics.length).toFixed(1))
    : 0;

  return (
    <div className="mx-auto flex min-h-full w-full max-w-6xl flex-col px-6 py-8 bg-[#000000] text-white">
      <div className="flex items-center justify-between flex-wrap gap-4 shrink-0 pb-4 border-b border-[rgba(255,255,255,0.08)] mb-6">
        <SectionHeading
          eyebrow="Analytics Center"
          title="Performance & Learning Loop"
          description="Measure campaign effectiveness, platform engagement variations, and target audience responses."
        />
        
        <div className="flex gap-2">
          {["All", "Instagram", "LinkedIn", "Facebook", "X", "YouTube"].map((plat) => (
            <button
              key={plat}
              onClick={() => setSelectedPlatform(plat)}
              className="px-3.5 py-1.5 rounded-full text-xs font-bold transition-all border"
              style={{
                background: selectedPlatform === plat ? "rgba(255, 255, 255, 0.08)" : "transparent",
                borderColor: selectedPlatform === plat ? "rgba(255, 255, 255, 0.15)" : "rgba(255, 255, 255, 0.05)",
                color: selectedPlatform === plat ? "#ffffff" : "rgba(255, 255, 255, 0.5)",
              }}
            >
              {plat}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-3 mb-6">
        <div className="rounded-2xl border border-white/5 bg-[#050505] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
          <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Total Tracked Reach</p>
          <p className="mt-2 text-3xl font-semibold text-white">{totalReach.toLocaleString()}</p>
          <p className="mt-2 text-xs text-emerald-400">↑ 8.4% from last period</p>
        </div>
        <div className="rounded-2xl border border-white/5 bg-[#050505] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
          <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Average Engagement</p>
          <p className="mt-2 text-3xl font-semibold text-white">{avgEngagement}%</p>
          <p className="mt-2 text-xs text-emerald-400">↑ 1.2% above benchmark</p>
        </div>
        <div className="rounded-2xl border border-white/5 bg-[#050505] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]">
          <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Follower Growth Rate</p>
          <p className="mt-2 text-3xl font-semibold text-white">+{avgGrowth}%</p>
          <p className="mt-2 text-xs text-emerald-400">↑ Steady audience expansion</p>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        {/* Table/Chart Overview */}
        <Panel eyebrow="Platform Analytics" title="Comparisons Across Surfaces" className="overflow-hidden">
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs text-white/60">
              <thead>
                <tr className="border-b border-white/5 text-[10px] uppercase tracking-wider text-white/30">
                  <th className="py-3 pr-4">Platform</th>
                  <th className="py-3 px-4">Reach</th>
                  <th className="py-3 px-4">Engagement</th>
                  <th className="py-3 px-4">Likes</th>
                  <th className="py-3 px-4">Growth</th>
                </tr>
              </thead>
              <tbody>
                {filteredMetrics.map((row) => (
                  <tr key={row.platform} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-4 pr-4 font-bold text-white">{row.platform}</td>
                    <td className="py-4 px-4 font-mono">{row.reach.toLocaleString()}</td>
                    <td className="py-4 px-4 font-mono">{row.engagementRate}%</td>
                    <td className="py-4 px-4 font-mono">{row.likes.toLocaleString()}</td>
                    <td className="py-4 px-4 text-emerald-400 font-mono">+{row.growth}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        {/* AI Recommendations */}
        <Panel eyebrow="Analytics Agent Insights" title="AI Strategic Recommendations">
          <div className="mt-4 space-y-3">
            {[
              {
                title: "Boost Video cadences on Instagram",
                description: "Reels sharing styling breakdowns have a 35% higher comment count than static carousel guides.",
                label: "High Impact"
              },
              {
                title: "Engage with LinkedIn comments within 1h",
                description: "Fast responses in comments increase second-degree impressions by 4.2x within the LinkedIn algorithm.",
                label: "Engagement"
              },
              {
                title: "Avoid promotional CTAs on Tuesdays",
                description: "Tuesday audience segments show high click drop-offs on 'Shop Now' CTAs; focus on educational content instead.",
                label: "Optimization"
              }
            ].map((rec, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-white/5 bg-[#050505] p-4 space-y-2 hover:border-[#388bfd]/30 transition-all duration-200"
              >
                <div className="flex items-center justify-between gap-3">
                  <h4 className="text-xs font-bold text-white/90">{rec.title}</h4>
                  <StatusPill label={rec.label} tone="neutral" />
                </div>
                <p className="text-[11px] leading-relaxed text-white/50">{rec.description}</p>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
