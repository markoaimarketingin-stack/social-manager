import { useWorkspaceContext } from "../../workspace/hooks/useWorkspaceContext";
import { Panel } from "../../../components/ui/Panel";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { StatusPill } from "../../../components/ui/StatusPill";

const platformHealth = [
  { platform: "Instagram", state: "Connected", tone: "success" as const },
  { platform: "LinkedIn", state: "Mock queue", tone: "neutral" as const },
  { platform: "X", state: "Not linked", tone: "warning" as const },
];

export function PublishingPage() {
  const { publishingQueueQuery, activityQuery } = useWorkspaceContext();
  const publishingQueue = publishingQueueQuery.data ?? [];
  const recentPublishActivity = (activityQuery.data ?? []).filter((item) =>
    ["publish_ready", "published"].includes(item.event_type),
  );

  return (
    <div className="mx-auto flex min-h-full w-full max-w-7xl flex-col px-5 py-10 lg:px-8">
      <SectionHeading
        eyebrow="Publishing queue"
        title="Stage publish-ready work like the deployed product"
        description="This is a visual parity surface first: scheduled drafts, platform health, and publishing receipts feel operational even while provider integrations remain intentionally deferred."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        <Panel eyebrow="Queue" title="Ready to schedule or publish">
          <div className="mt-5 space-y-4">
            {publishingQueue.map((draft) => (
              <div key={draft.id} className="rounded-3xl border border-line bg-white/5 p-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-lg font-semibold text-white">{draft.title}</p>
                    <p className="mt-2 text-sm text-white/55">
                      {draft.scheduled_publish_at
                        ? `Scheduled for ${new Date(draft.scheduled_publish_at).toLocaleString()}`
                        : "Waiting for a scheduled slot"}
                    </p>
                  </div>
                  <StatusPill label={draft.review_status.replace(/_/g, " ")} tone="success" />
                </div>
                <p className="mt-4 rounded-2xl border border-white/10 bg-black/35 p-4 text-sm leading-7 text-white/70">
                  {draft.caption}
                </p>
              </div>
            ))}
            {!publishingQueue.length ? (
              <div className="rounded-3xl border border-dashed border-line p-6 text-sm text-white/55">
                No publish-ready drafts yet. Approve one in the review queue to populate this surface.
              </div>
            ) : null}
          </div>
        </Panel>

        <Panel eyebrow="Platform status" title="Publishing posture">
          <div className="mt-5 space-y-4">
            {platformHealth.map((item) => (
              <div key={item.platform} className="rounded-3xl border border-line bg-white/5 p-5">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-lg font-semibold">{item.platform}</p>
                  <StatusPill label={item.state} tone={item.tone} />
                </div>
                <p className="mt-3 text-sm text-white/60">
                  {item.platform === "Instagram"
                    ? "Founder-demo ready with mock publishing receipts and scheduled queue visuals."
                    : item.platform === "LinkedIn"
                      ? "Visible in the queue, using typed mock publishing until provider setup lands."
                      : "Placeholder status preserved for parity without adding OAuth complexity."}
                </p>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel eyebrow="Timeline" title="Recent publish actions">
          <div className="mt-5 space-y-3">
            {recentPublishActivity.slice(0, 6).map((event) => (
              <div key={event.id} className="rounded-3xl border border-line bg-white/5 p-5">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-white">{event.summary}</p>
                  <StatusPill label={event.event_type.replace(/_/g, " ")} tone="neutral" />
                </div>
                <p className="mt-2 text-xs uppercase tracking-[0.25em] text-white/35">
                  {new Date(event.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </Panel>

        <Panel eyebrow="Receipts" title="Mock publishing confirmations">
          <div className="mt-5 space-y-4">
            {publishingQueue.map((draft) => (
              <div key={draft.id} className="rounded-3xl border border-line bg-white/5 p-5">
                <p className="text-[10px] uppercase tracking-[0.35em] text-white/35">Receipt preview</p>
                <p className="mt-3 text-sm leading-7 text-white/70">
                  {draft.mock_publishing_receipt
                    ? JSON.stringify(draft.mock_publishing_receipt)
                    : "A mock receipt appears after publish action so the product feels complete for demo."}
                </p>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
