import { useState, useEffect } from "react";

type SettingsModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [groqKey, setGroqKey] = useState("");
  const [openaiKey, setOpenaiKey] = useState("");
  const [customBackendUrl, setCustomBackendUrl] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setGroqKey(localStorage.getItem("groq_api_key") || "");
      setOpenaiKey(localStorage.getItem("openai_api_key") || "");
      setCustomBackendUrl(localStorage.getItem("custom_backend_url") || "");
      setSaved(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = () => {
    localStorage.setItem("groq_api_key", groqKey.trim());
    localStorage.setItem("openai_api_key", openaiKey.trim());
    localStorage.setItem("custom_backend_url", customBackendUrl.trim());
    localStorage.removeItem("demo_mode_fallback");
    setSaved(true);
    setTimeout(() => {
      onClose();
      window.location.reload(); // Reload to refresh contexts and API fallback states
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div
        className="w-full max-w-md rounded-2xl p-6 text-white shadow-2xl animate-scaleIn"
        style={{
          background: "#161b22",
          border: "1px solid #30363d",
          boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#21262d]">
          <div>
            <h3 className="text-lg font-bold tracking-wide">Manage Models & API Keys</h3>
            <p className="text-xs text-white/40">Configure API keys and backend routing.</p>
          </div>
          <button
            onClick={onClose}
            className="text-white/40 hover:text-white transition-colors"
          >
            <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
              <path d="M3.72 3.72a.75.75 0 0 1 1.06 0L8 6.94l3.22-3.22a.75.75 0 1 1 1.06 1.06L9.06 8l3.22 3.22a.75.75 0 1 1-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 0 1-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 0 1 0-1.06z"/>
            </svg>
          </button>
        </div>

        {/* Form Body */}
        <div className="py-5 space-y-4">
          {/* Groq Key */}
          <label className="block">
            <span className="block text-xs font-bold uppercase tracking-wider text-white/60 mb-1.5">
              Groq API Key
            </span>
            <input
              type="password"
              placeholder="gsk_..."
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              className="w-full rounded-lg px-3.5 py-2.5 text-sm bg-[#0d1117] border border-[#30363d] focus:border-[#388bfd] focus:outline-none transition-colors"
            />
            <span className="text-[10px] text-white/35 mt-1 block">
              Used for Groq Llama models in real chat interactions.
            </span>
          </label>

          {/* OpenAI Key */}
          <label className="block">
            <span className="block text-xs font-bold uppercase tracking-wider text-white/60 mb-1.5">
              OpenAI API Key
            </span>
            <input
              type="password"
              placeholder="sk-proj-..."
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              className="w-full rounded-lg px-3.5 py-2.5 text-sm bg-[#0d1117] border border-[#30363d] focus:border-[#388bfd] focus:outline-none transition-colors"
            />
            <span className="text-[10px] text-white/35 mt-1 block">
              Used for custom OpenAI model generations and actions.
            </span>
          </label>

          {/* Deployed Backend API URL */}
          <label className="block">
            <span className="block text-xs font-bold uppercase tracking-wider text-white/60 mb-1.5">
              Deployed Backend API URL
            </span>
            <input
              type="text"
              placeholder="https://your-backend-api.onrender.com"
              value={customBackendUrl}
              onChange={(e) => setCustomBackendUrl(e.target.value)}
              className="w-full rounded-lg px-3.5 py-2.5 text-sm bg-[#0d1117] border border-[#30363d] focus:border-[#388bfd] focus:outline-none transition-colors text-white"
            />
            <span className="text-[10px] text-white/35 mt-1 block">
              Enter your deployed FastAPI server URL (leave empty to use local port 8088).
            </span>
          </label>

        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-[#21262d] flex items-center justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold hover:bg-white/5 transition-colors text-white/60 hover:text-white"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saved}
            className="px-4 py-2 rounded-lg text-xs font-semibold transition-all shadow-[0_4px_12px_rgba(31,111,235,0.2)]"
            style={{
              background: saved ? "#238636" : "#1f6feb",
              color: "#fff",
              border: "1px solid rgba(255,255,255,0.05)",
            }}
          >
            {saved ? "✓ Settings Saved" : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}
