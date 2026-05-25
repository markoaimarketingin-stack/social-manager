import { Panel } from "../../../components/ui/Panel";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { StatusPill } from "../../../components/ui/StatusPill";
import { useWorkspaceContext } from "../../workspace/hooks/useWorkspaceContext";

const trendCards = [
  { title: "Festive dressing edits", source: "Google Trends", score: "High match" },
  { title: "Creator GRWM reels", source: "Instagram", score: "Rising" },
  { title: "Work-to-weekend styling", source: "LinkedIn chatter", score: "Operator signal" },
];

const competitorCards = [
  { name: "Ajio", gap: "Less premium storytelling around curated edits." },
  { name: "Nykaa Fashion", gap: "Stronger occasion curation, weaker repeatable reel cadence." },
];

export function IntelligencePage() {
  const { latestStrategyQuery, activitySummaryQuery } = useWorkspaceContext();
  const strategy = latestStrategyQuery.data ?? null;

  return (
    <div className="mx-auto flex min-h-full w-full max-w-6xl flex-col px-5 py-10 lg:px-8">
      <SectionHeading
        eyebrow="Intelligence hub"
        title="Specialist signal surface"
        description="A restrained view of what matters now: one clear signal stack, one strategic anchor, and minimal noise."
      />

      <div className="mt-10 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Panel eyebrow="Signal stack" title="What is moving right now">
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {trendCards.map((card) => (
              <div key={card.title} className="rounded-3xl border border-line bg-white/5 p-5">
                <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">{card.source}</p>
                <p className="mt-3 text-lg font-semibold text-white">{card.title}</p>
                <div className="mt-3">
                  <StatusPill label={card.score} tone="success" />
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel eyebrow="Operator context" title="Strategic anchor">
          <div className="mt-6 space-y-4">
            <div className="rounded-3xl border border-line bg-white/5 p-5">
              <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Active strategy</p>
              <p className="mt-3 text-lg font-semibold">{strategy?.title ?? "No strategy yet"}</p>
              <p className="mt-3 text-sm leading-7 text-white/60">
                {strategy?.summary ??
                  "Generate a strategy first so intelligence and planning feel connected."}
              </p>
            </div>
            <p className="px-1 text-sm leading-7 text-white/58">
              {activitySummaryQuery.data?.latest_summary ??
                "Signals stay intentionally sparse so the main composition remains calm and readable."}
            </p>
          </div>
        </Panel>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel eyebrow="Competitor focus" title="What to watch">
          <div className="mt-6 space-y-4">
            {competitorCards.map((card) => (
              <div key={card.name} className="rounded-3xl border border-line bg-white/5 p-5">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold">{card.name}</h3>
                  <StatusPill label="Tracked" tone="neutral" />
                </div>
                <p className="mt-3 text-sm leading-7 text-white/65">{card.gap}</p>
              </div>
            ))}
          </div>
        </Panel>

        <Panel eyebrow="Copy cue" title="One focused prompt set">
          <div className="mt-6 space-y-4">
            {[
              "Use stronger first-frame contrast between product and lifestyle scene.",
              "Turn the best reel hook into a LinkedIn operator memo for cross-surface continuity.",
            ].map((item) => (
              <div key={item} className="rounded-3xl border border-line bg-white/5 p-4 text-sm text-white/75">
                {item}
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
