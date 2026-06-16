import type { PropsWithChildren, ReactNode } from "react";

type OverlayModalProps = PropsWithChildren<{
  open: boolean;
  title: string;
  description?: string;
  onClose: () => void;
  footer?: ReactNode;
  maxWidthClassName?: string;
}>;

export function OverlayModal({
  open,
  title,
  description,
  onClose,
  footer,
  children,
  maxWidthClassName = "max-w-3xl",
}: OverlayModalProps) {
  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-[90] flex items-center justify-center bg-black/65 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className={`w-full overflow-hidden rounded-[2rem] border border-white/10 bg-[#0b0b0b] text-white shadow-[0_30px_120px_rgba(0,0,0,0.55)] ${maxWidthClassName}`}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between border-b border-white/10 px-6 py-5">
          <div>
            <h2 className="text-lg font-bold tracking-tight text-white">{title}</h2>
            {description ? <p className="mt-1 text-sm text-white/50">{description}</p> : null}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-white/10 bg-[#000000] px-3 py-2 text-xs font-semibold text-white/70 transition hover:bg-[#050505] hover:text-white"
          >
            Close
          </button>
        </div>
        <div className="max-h-[72vh] overflow-y-auto px-6 py-5">{children}</div>
        {footer ? <div className="border-t border-white/10 px-6 py-4">{footer}</div> : null}
      </div>
    </div>
  );
}
