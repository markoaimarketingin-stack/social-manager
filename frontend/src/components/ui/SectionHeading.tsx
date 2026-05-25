type SectionHeadingProps = {
  eyebrow: string;
  title: string;
  description: string;
};

export function SectionHeading({ eyebrow, title, description }: SectionHeadingProps) {
  return (
    <div className="max-w-4xl">
      <p className="text-[10px] font-semibold uppercase tracking-[0.35em] text-white/35">
        {eyebrow}
      </p>
      <h1 className="mt-4 text-3xl font-black tracking-tight text-white md:text-5xl">{title}</h1>
      <p className="mt-5 max-w-3xl text-sm leading-7 text-white/58 md:text-base">{description}</p>
    </div>
  );
}
