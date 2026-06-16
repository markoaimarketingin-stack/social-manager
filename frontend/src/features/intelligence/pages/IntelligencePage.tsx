import { useState } from "react";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { StatusPill } from "../../../components/ui/StatusPill";
import { useWorkspaceContext } from "../../workspace/hooks/useWorkspaceContext";

interface TrendCard {
  id: number;
  title: string;
  source: string;
  score: string;
}

interface CompetitorCard {
  id: number;
  name: string;
  gap: string;
}

const INITIAL_TRENDS: TrendCard[] = [
  { id: 1, title: "Festive dressing edits", source: "Google Trends", score: "High match" },
  { id: 2, title: "Creator GRWM reels", source: "Instagram", score: "Rising" },
  { id: 3, title: "Work-to-weekend styling", source: "LinkedIn chatter", score: "Operator signal" },
];

const INITIAL_COMPETITORS: CompetitorCard[] = [
  { id: 1, name: "Ajio", gap: "Less premium storytelling around curated edits." },
  { id: 2, name: "Nykaa Fashion", gap: "Stronger occasion curation, weaker repeatable reel cadence." },
];

const SCANNED_TRENDS: TrendCard[] = [
  { id: 4, title: "Minimalist sustainable chic edits", source: "Instagram Reels", score: "High match" },
  { id: 5, title: "AI-powered creator economies discussion", source: "LinkedIn chatter", score: "Rising" },
  { id: 6, title: "90s nostalgia aesthetic wardrobes", source: "TikTok trend", score: "Viral" },
];

const SCANNED_COMPETITORS: CompetitorCard[] = [
  { id: 3, name: "Zara India", gap: "Highly responsive global trends, but localized engagement is sparse." },
  { id: 4, name: "Myntra", gap: "High volume influencer marketing, but brand voice is cluttered." },
];

export function IntelligencePage() {
  const { latestStrategyQuery, activitySummaryQuery } = useWorkspaceContext();
  const strategy = latestStrategyQuery.data ?? null;
  
  const [trends, setTrends] = useState<TrendCard[]>(INITIAL_TRENDS);
  const [competitors, setCompetitors] = useState<CompetitorCard[]>(INITIAL_COMPETITORS);
  const [isScanning, setIsScanning] = useState(false);
  const [scannedCount, setScannedCount] = useState(0);

  const handleScanSignals = async () => {
    setIsScanning(true);
    await new Promise((r) => setTimeout(r, 1500));
    
    // Add scanned trends and competitors
    if (scannedCount === 0) {
      setTrends((prev) => [...SCANNED_TRENDS, ...prev]);
      setCompetitors((prev) => [...SCANNED_COMPETITORS, ...prev]);
      setScannedCount(1);
    } else {
      const extraTrend = {
        id: Date.now(),
        title: "Occasion-based curated lookbooks",
        source: "Pinterest Search",
        score: "Rising",
      };
      setTrends((prev) => [extraTrend, ...prev]);
    }
    setIsScanning(false);
  };

  return (
    <div className="mx-auto flex min-h-full w-full max-w-6xl flex-col px-6 py-8 bg-[#000000] text-white">
      <div className="flex items-center justify-between flex-wrap gap-4 shrink-0 pb-4 border-b border-[rgba(255,255,255,0.08)] mb-6">
        <SectionHeading
          eyebrow="Intelligence Hub"
          title="Demand & Market Specialist"
          description="A real-time signal tracker scanning global social search chatter and competitor positioning gaps."
        />
        <button
          onClick={handleScanSignals}
          disabled={isScanning}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all shadow-[0_4px_12px_rgba(31,111,235,0.25)] disabled:opacity-50"
          style={{
            background: "linear-gradient(135deg, #1f6feb, #388bfd)",
            color: "#fff",
            border: "1px solid rgba(255,255,255,0.1)",
          }}
        >
          {isScanning ? (
            <>
              <div className="h-3 w-3 rounded-full border border-t-transparent animate-spin border-white" />
              Scanning Chatter...
            </>
          ) : (
            "⚡ Scan Market Signals"
          )}
        </button>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div
          className="rounded-2xl border p-5 text-white flex flex-col justify-between"
          style={{ background: "#000000", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-white/60 mb-1">Signal Stack</h4>
            <p className="text-[10px] text-white/40 mb-4">What trends and content pillars are moving right now.</p>
            <div className="grid gap-4 md:grid-cols-2">
              {trends.map((card) => (
                <div
                  key={card.id}
                  className="rounded-xl border p-4 bg-[#000000]/60 flex flex-col justify-between space-y-3 hover:border-[#388bfd]/30 transition-all duration-200"
                  style={{ borderColor: "rgba(255,255,255,0.04)" }}
                >
                  <div>
                    <span className="text-[9px] uppercase tracking-wider text-white/30 font-bold">{card.source}</span>
                    <p className="mt-1 text-xs font-semibold text-white/90">{card.title}</p>
                  </div>
                  <div>
                    <StatusPill label={card.score} tone={card.score === "Viral" ? "success" : "neutral"} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div
          className="rounded-2xl border p-5 text-white flex flex-col justify-between"
          style={{ background: "#000000", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-white/60 mb-1">Strategic Anchor</h4>
            <p className="text-[10px] text-white/40 mb-4">Operator strategic context and guidance summary.</p>
            <div className="space-y-4 text-xs">
              <div className="rounded-xl border p-4 bg-[#000000]/40 space-y-1.5" style={{ borderColor: "rgba(255,255,255,0.04)" }}>
                <span className="text-[9px] uppercase tracking-wider text-white/30 font-bold">Active Strategy</span>
                <p className="font-bold">{strategy?.title ?? "Standard Social Media Strategy"}</p>
                <p className="text-white/50 leading-relaxed">
                  {strategy?.summary ??
                    "Curated occasions and premium positioning aligned to lifestyle reels."}
                </p>
              </div>
              <p className="text-white/45 leading-relaxed pl-1">
                {activitySummaryQuery.data?.latest_summary ??
                  "Signals stay intentionally focused so the strategy remains concise and easily actioned."}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div
          className="rounded-2xl border p-5 text-white flex flex-col"
          style={{ background: "#000000", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <h4 className="text-xs font-bold uppercase tracking-wider text-white/60 mb-1">Competitor Signals</h4>
          <p className="text-[10px] text-white/40 mb-4">Positioning vulnerabilities identified in direct competitors.</p>
          <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1 scrollbar-thin">
            {competitors.map((card) => (
              <div
                key={card.id}
                className="rounded-xl border p-4 bg-[#000000]/60 space-y-2 hover:border-[#388bfd]/30 transition-all duration-200"
                style={{ borderColor: "rgba(255,255,255,0.04)" }}
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-xs font-bold text-white/90">{card.name}</h3>
                  <StatusPill label="Tracked Gaps" tone="neutral" />
                </div>
                <p className="text-[11px] leading-relaxed text-white/50">{card.gap}</p>
              </div>
            ))}
          </div>
        </div>

        <div
          className="rounded-2xl border p-5 text-white flex flex-col justify-between"
          style={{ background: "#000000", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-white/60 mb-1">AI Writing Cues</h4>
            <p className="text-[10px] text-white/40 mb-4">Focused prompts to inherit for copywriting drafts.</p>
            <div className="space-y-2">
              {[
                "Use stronger first-frame contrast between product and lifestyle scene.",
                "Turn the best reel hook into a LinkedIn operator memo for cross-surface continuity.",
                "Leverage the rising occasion-based Pinterest interest in sustainable styling guides.",
              ].map((item) => (
                <div
                  key={item}
                  className="rounded-xl border p-3.5 text-xs text-white/70 leading-relaxed bg-[#000000]/40"
                  style={{ borderColor: "rgba(255,255,255,0.04)" }}
                >
                  💡 {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
