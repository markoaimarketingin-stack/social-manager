type StatusPillProps = {
  label: string;
  tone?: "neutral" | "success" | "warning";
};

const toneClasses: Record<NonNullable<StatusPillProps["tone"]>, string> = {
  neutral: "border-white/10 bg-white/5 text-white/80",
  success: "border-emerald-400/20 bg-emerald-400/10 text-emerald-100",
  warning: "border-amber-400/20 bg-amber-400/10 text-amber-100",
};

export function StatusPill({ label, tone = "neutral" }: StatusPillProps) {
  return (
    <span className={`rounded-full border px-3 py-1 text-[11px] font-medium ${toneClasses[tone]}`}>
      {label}
    </span>
  );
}
