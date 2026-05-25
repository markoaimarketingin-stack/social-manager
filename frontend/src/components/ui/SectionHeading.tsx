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
      <h1 className="mt-4 text-4xl font-black tracking-tight text-white md:text-6xl">{title}</h1>
      <p className="mt-5 max-w-3xl text-base leading-8 text-white/58 md:text-lg">{description}</p>
    </div>
  );
}
