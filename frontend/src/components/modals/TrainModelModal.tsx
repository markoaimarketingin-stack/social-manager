import { useState, useRef } from "react";
import { apiFetch } from "../../lib/api/client";

type TrainModelModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
};

export function TrainModelModal({ isOpen, onClose, onSuccess }: TrainModelModalProps) {
  const [category, setCategory] = useState("brand voice");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setFeedback(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setFeedback("Please select a file first.");
      return;
    }

    setLoading(true);
    setFeedback(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("category", category);

      const res = await apiFetch("/api/knowledge_base/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      setFeedback("Document uploaded and trained successfully!");
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setTimeout(() => {
        onSuccess?.();
        onClose();
      }, 1200);
    } catch (err: any) {
      setFeedback(`Error: ${err.message || "Failed to upload file."}`);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div
        className="w-full max-w-md rounded-2xl p-6 text-white shadow-2xl animate-scaleIn"
        style={{
          background: "#000000",
          border: "1px solid rgba(255,255,255,0.08)",
          boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[rgba(255,255,255,0.04)]">
          <div>
            <h3 className="text-lg font-bold tracking-wide">Train Model</h3>
            <p className="text-xs text-white/40">Queue document context for the model training pipeline.</p>
          </div>
          <button
            onClick={onClose}
            className="text-white/40 hover:text-white transition-colors"
          >
            <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
              <path d="M3.72 3.72a.75.75 0 0 1 1.06 0L8 6.94l3.22-3.22a.75.75 0 1 1 1.06 1.06L9.06 8l3.22 3.22a.75.75 0 1 1-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 0 1-1.06-1.06L8 9.06l-3.22 3.22a.75.75 0 0 1-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 0 1 0-1.06z"/>
            </svg>
          </button>
        </div>

        {/* Body Form */}
        <form onSubmit={handleUpload} className="py-5 space-y-4">
          {/* Category Dropdown */}
          <label className="block">
            <span className="block text-xs font-bold uppercase tracking-wider text-white/60 mb-1.5">
              Training Category
            </span>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full rounded-lg px-3.5 py-2.5 text-sm bg-[#000000] border border-[rgba(255,255,255,0.08)] focus:border-[#388bfd] focus:outline-none transition-colors appearance-none"
              style={{
                backgroundImage: "url('data:image/svg+xml;charset=UTF-8,%3csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%236e7681%22 stroke-width=%222%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22%3e%3cpolyline points=%226 9 12 15 18 9%22%3e%3c/polyline%3e%3c/svg%3e')",
                backgroundRepeat: "no-repeat",
                backgroundPosition: "right 12px center",
                backgroundSize: "16px",
              }}
            >
              <option value="brand voice">brand voice</option>
              <option value="audience profile">audience profile</option>
              <option value="creative briefs">creative briefs</option>
              <option value="competitor signals">competitor signals</option>
            </select>
          </label>

          {/* Drag and Drop Box */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-[rgba(255,255,255,0.08)] hover:border-[#388bfd] rounded-2xl p-6 text-center cursor-pointer transition-all duration-200 bg-[#000000]/50 hover:bg-[#000000]"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,.csv"
              className="hidden"
            />
            <div className="flex flex-col items-center gap-2">
              <svg viewBox="0 0 16 16" className="h-8 w-8 text-[#8b949e] fill-current">
                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
              </svg>
              <p className="text-xs font-semibold mt-1">
                {file ? file.name : "Upload briefs, voice guides, or audience files"}
              </p>
              <p className="text-[10px] text-white/30">
                PDF, DOCX, TXT, CSV. Size up to 10MB.
              </p>
            </div>
          </div>

          {feedback && (
            <p className="text-xs text-center" style={{ color: feedback.startsWith("Error:") ? "#f85149" : "#3fb950" }}>
              {feedback}
            </p>
          )}

          {/* Footer actions inside form */}
          <div className="pt-4 border-t border-[rgba(255,255,255,0.04)] flex items-center justify-end gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold hover:bg-[#000000] transition-colors text-white/60 hover:text-white"
            >
              Close
            </button>
            <button
              type="submit"
              disabled={loading || !file}
              className="px-4 py-2 rounded-lg text-xs font-bold transition-all shadow-[0_4px_12px_rgba(35,134,54,0.2)] disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                background: "#238636",
                color: "#fff",
                border: "1px solid rgba(255,255,255,0.05)",
              }}
            >
              {loading ? "Training..." : "Start Training"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
