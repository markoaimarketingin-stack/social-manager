export type ToastItem = {
  id: string;
  message: string;
};

export function ToastViewport({ items }: { items: ToastItem[] }) {
  if (!items.length) {
    return null;
  }

  return (
    <div className="pointer-events-none fixed bottom-5 right-5 z-[95] flex w-[min(28rem,calc(100vw-2rem))] flex-col gap-3">
      {items.map((item) => (
        <div
          key={item.id}
          className="rounded-2xl border border-white/10 bg-black/85 px-4 py-3 text-sm text-white shadow-[0_20px_70px_rgba(0,0,0,0.4)] backdrop-blur"
        >
          {item.message}
        </div>
      ))}
    </div>
  );
}
