import { StatusPill } from "../../../components/ui/StatusPill";
import { useWorkspaceContext } from "../hooks/useWorkspaceContext";

const formatTimestamp = (value: string | null | undefined) =>
  value
    ? new Date(value).toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      })
    : "No activity yet";

const workflowTone = (status: string) =>
  status === "completed" ? "success" : status === "failed" ? "warning" : "neutral";

export function WorkspaceOverviewPage() {
  const {
    brandProfileQuery,
    workflowRunsQuery,
    activitySummaryQuery,
  } = useWorkspaceContext();

  const latestRun = workflowRunsQuery.data?.[0] ?? null;

  return (
    <div className="mx-auto flex min-h-full w-full max-w-6xl flex-col px-5 py-8 lg:px-8">
      <section className="mt-12 rounded-[2rem] border border-white/8 bg-white/[0.03] p-7 shadow-shell">
        <div className="mx-auto mb-7 flex h-20 w-20 animate-float items-center justify-center rounded-full border border-white/8 bg-white/[0.03] shadow-[0_0_0_1px_rgba(255,255,255,0.03)]">
          <div className="flex gap-1.5">
            <span className="h-8 w-2.5 rounded-full bg-white" />
            <span className="mt-[-8px] h-10 w-2.5 rounded-full bg-white" />
            <span className="mt-[-14px] h-14 w-2.5 rounded-full bg-white" />
            <span className="mt-[-8px] h-10 w-2.5 rounded-full bg-white" />
          </div>
        </div>

        <h2 className="mx-auto max-w-4xl text-center text-3xl font-black leading-tight tracking-tight text-white md:text-5xl">
          I am your Social Community Manager
        </h2>
        <p className="mx-auto mt-5 max-w-3xl text-center text-sm leading-7 text-white/60 md:text-base">
          Specialized in managing social communities through audience engagement, content
          coordination, trend monitoring, moderation, sentiment analysis, and growth-driven
          interaction strategies for impactful brand presence and loyal community building.
        </p>

        <div className="mx-auto mt-10 flex max-w-3xl flex-wrap items-center justify-center gap-2">
          <StatusPill
            label={`Workflow ${latestRun?.status ?? "idle"}`}
            tone={workflowTone(latestRun?.status ?? "idle")}
          />
          <StatusPill
            label={brandProfileQuery.data ? "Brand profile ready" : "Brand profile missing"}
            tone={brandProfileQuery.data ? "success" : "warning"}
          />
          <StatusPill
            label={`Last event ${formatTimestamp(activitySummaryQuery.data?.latest_event_at)}`}
            tone="neutral"
          />
        </div>
      </section>
    </div>
  );
}
