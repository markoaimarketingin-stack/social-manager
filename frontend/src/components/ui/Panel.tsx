import type { PropsWithChildren } from "react";

type PanelProps = PropsWithChildren<{
  title?: string;
  eyebrow?: string;
  tone?: "dark" | "light";
  className?: string;
}>;

export function Panel({ title, eyebrow, tone = "dark", className = "", children }: PanelProps) {
  const toneClasses =
    tone === "light"
      ? "border border-black/10 bg-white text-black shadow-[0_22px_70px_rgba(0,0,0,0.08)]"
      : "shell-surface text-ink";

  return (
    <section className={`rounded-[2rem] p-6 shadow-panel ${toneClasses} ${className}`.trim()}>
      {eyebrow ? (
        <p
          className={`text-[10px] font-semibold uppercase tracking-[0.35em] ${
            tone === "light" ? "text-black/50" : "text-white/35"
          }`}
        >
          {eyebrow}
        </p>
      ) : null}
      {title ? <h2 className="mt-3 text-xl font-semibold tracking-tight">{title}</h2> : null}
      {children}
    </section>
  );
}
