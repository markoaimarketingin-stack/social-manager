type SectionHeadingProps = {
  eyebrow: string;
  title: string;
  description: string;
};

export function SectionHeading({ eyebrow, title, description }: SectionHeadingProps) {
  return (
    <div className="max-w-3xl">
      <p className="text-[9px] font-semibold uppercase tracking-[0.3em] text-white/35">
        {eyebrow}
      </p>
      <h1 className="mt-3 text-2xl font-bold text-white md:text-[2.25rem]">{title}</h1>
      <p className="mt-3 max-w-2xl text-[0.92rem] leading-6 text-white/56">{description}</p>
    </div>
  );
}
