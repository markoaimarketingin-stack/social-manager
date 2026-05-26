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
    <div className="mx-auto flex min-h-full w-full max-w-5xl flex-col px-5 py-6 lg:px-7">
      <section className="flex min-h-[calc(100vh-8rem)] flex-col items-center justify-center pb-12 text-center">
        <div className="mb-8 flex h-24 w-24 animate-float items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.025] shadow-[0_22px_90px_rgba(255,255,255,0.035)]">
          <div className="flex gap-2">
            <span className="h-10 w-3 rounded-full bg-white" />
            <span className="mt-[-10px] h-14 w-3 rounded-full bg-white" />
            <span className="mt-[-18px] h-[4.5rem] w-3 rounded-full bg-white" />
          </div>
        </div>

        <h2 className="mx-auto max-w-4xl text-[2.65rem] font-bold leading-[0.98] text-white md:text-[3.45rem]">
          Social Operations Command
        </h2>
        <p className="mx-auto mt-5 max-w-3xl text-[0.95rem] leading-7 text-white/56 md:text-[1rem]">
          The central hub for strategy, planning, and publishing operations. 
          Manage multi-channel campaigns with automated intelligence, continuous workflow tracking, 
          and human-in-the-loop review queues. Everything synchronized continuously.
        </p>

        <div className="mx-auto mt-8 flex max-w-3xl flex-wrap items-center justify-center gap-2">
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
