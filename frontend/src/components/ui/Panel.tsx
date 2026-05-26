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
      : "shell-surface text-ink transition-transform duration-500 ease-out";

  return (
    <section className={`rounded-[2rem] p-8 shadow-[0_30px_80px_rgba(0,0,0,0.28)] ${toneClasses} hover:shadow-[0_40px_100px_rgba(0,0,0,0.4)] hover:-translate-y-0.5 ${className}`.trim()}>
      {eyebrow ? (
        <p
          className={`text-[10px] font-bold uppercase tracking-[0.35em] ${
            tone === "light" ? "text-black/50" : "text-white/40"
          }`}
        >
          {eyebrow}
        </p>
      ) : null}
      {title ? <h2 className="mt-4 text-xl font-bold tracking-tight text-white/95">{title}</h2> : null}
      {children}
    </section>
  );
}
