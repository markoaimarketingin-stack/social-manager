import { useState, useEffect } from "react";
import { apiBaseUrl } from "../../lib/api/client";
import { isDemoModeEnabled } from "../../lib/api/mock";

type KnowledgeBaseModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

interface Document {
  id: number;
  filename: string;
  category: string;
  file_type: string;
  uploaded_at: string;
  processing_status: string;
}

const DEFAULT_DEMO_DOCS: Document[] = [
  {
    id: 101,
    filename: "brand_voice_guidelines.txt",
    category: "brand voice",
    file_type: "txt",
    uploaded_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    processing_status: "completed",
  },
  {
    id: 102,
    filename: "target_audience_personas.txt",
    category: "audience profile",
    file_type: "txt",
    uploaded_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    processing_status: "completed",
  },
  {
    id: 103,
    filename: "competitor_social_audit.txt",
    category: "competitor signals",
    file_type: "txt",
    uploaded_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    processing_status: "completed",
  },
];

export function KnowledgeBaseModal({ isOpen, onClose }: KnowledgeBaseModalProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      if (isDemoModeEnabled()) {
        await new Promise((r) => setTimeout(r, 600));
        const stored = localStorage.getItem("demo_kb_docs");
        if (!stored) {
          localStorage.setItem("demo_kb_docs", JSON.stringify(DEFAULT_DEMO_DOCS));
          setDocuments(DEFAULT_DEMO_DOCS);
        } else {
          setDocuments(JSON.parse(stored));
        }
      } else {
        const res = await fetch(`${apiBaseUrl}/api/knowledge_base/documents`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        });
        if (!res.ok) throw new Error("Failed to load documents");
        const data = await res.json();
        setDocuments(data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to fetch documents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDocuments();
    }
  }, [isOpen]);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this document from the training context?")) return;

    try {
      if (isDemoModeEnabled()) {
        const stored = JSON.parse(localStorage.getItem("demo_kb_docs") || "[]");
        const updated = stored.filter((d: any) => d.id !== id);
        localStorage.setItem("demo_kb_docs", JSON.stringify(updated));
        setDocuments(updated);
      } else {
        const res = await fetch(`${apiBaseUrl}/api/knowledge_base/${id}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        });
        if (!res.ok) throw new Error("Failed to delete document");
        setDocuments((prev) => prev.filter((d) => d.id !== id));
      }
    } catch (err: any) {
      alert(`Error deleting document: ${err.message}`);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div
        className="w-full max-w-2xl rounded-2xl p-6 text-white shadow-2xl animate-scaleIn flex flex-col max-h-[85vh]"
        style={{
          background: "#161b22",
          border: "1px solid #30363d",
          boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#21262d] shrink-0">
          <div>
            <h3 className="text-lg font-bold tracking-wide">Knowledge Base</h3>
            <p className="text-xs text-white/40">View and manage uploaded materials that inform the model strategy.</p>
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

        {/* Content Container */}
        <div className="flex-1 overflow-y-auto py-4 scrollbar-thin space-y-4 pr-1 min-h-[250px]">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-10 space-y-2">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-white/20 border-t-blue-400" />
              <p className="text-xs text-white/40">Loading workspace corpus...</p>
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-center text-xs text-[#f85149]">
              {error}
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 space-y-3">
              <svg viewBox="0 0 16 16" className="mx-auto h-12 w-12 text-[#30363d] fill-current">
                <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/>
              </svg>
              <div>
                <p className="text-sm font-semibold">Knowledge base is empty</p>
                <p className="text-xs text-white/40 mt-1">Train your model by uploading brand briefs, CSV datasets, or guides.</p>
              </div>
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-[#30363d] bg-[#0d1117]/40">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-[#161b22] border-b border-[#30363d] text-white/60">
                    <th className="p-3 font-semibold uppercase tracking-wider">Document</th>
                    <th className="p-3 font-semibold uppercase tracking-wider">Category</th>
                    <th className="p-3 font-semibold uppercase tracking-wider">Type</th>
                    <th className="p-3 font-semibold uppercase tracking-wider">Trained At</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#21262d]">
                  {documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="p-3 font-semibold truncate max-w-[180px]">{doc.filename}</td>
                      <td className="p-3">
                        <span
                          className="px-2 py-0.5 rounded-full text-[10px] font-medium border capitalize"
                          style={{
                            background: "rgba(56,139,253,0.08)",
                            color: "#388bfd",
                            borderColor: "rgba(56,139,253,0.2)",
                          }}
                        >
                          {doc.category}
                        </span>
                      </td>
                      <td className="p-3 uppercase text-[10px] text-white/40 font-semibold">{doc.file_type}</td>
                      <td className="p-3 text-white/50">{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="text-white/40 hover:text-red-400 p-1.5 rounded transition-all"
                          title="Delete from knowledge base"
                        >
                          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current">
                            <path d="M11 1.5v1h3.5a.5.5 0 0 1 0 1h-.538l-.853 10.66A2 2 0 0 1 11.115 16H4.885a2 2 0 0 1-1.992-1.84L2.04 3.5H1.5a.5.5 0 0 1 0-1H5v-1A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5Zm-5 0v1h4v-1a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5ZM4.5 5.029l.5 8.5a.5.5 0 1 0 .998-.06l-.5-8.5a.5.5 0 1 0-.998.06Zm6.53-.528a.5.5 0 0 0-.528.47l-.5 8.5a.5.5 0 0 0 .998.058l.5-8.5a.5.5 0 0 0-.47-.528ZM8 4.5a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 1 0V5a.5.5 0 0 0-.5-.5Z"/>
                          </svg>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-[#21262d] flex items-center justify-end shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold hover:bg-white/5 transition-colors text-white/60 hover:text-white"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
