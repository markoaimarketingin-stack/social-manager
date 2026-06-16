import { useEffect, useRef, useState } from "react";
import { apiBaseUrl } from "../../lib/api/client";
import { useWorkspaceChrome } from "../../features/workspace/components/WorkspaceChromeContext";

type Mode = "ask" | "agent";
type Tab = "chatbot" | "suggestions";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  published?: Array<{ platform: string; content: string }>;
}

interface Connection {
  platform: string;
  account_name: string;
}

const PLATFORM_STYLES: Record<string, { bg: string; text: string; border: string; abbr: string }> = {
  linkedin:  { bg: "rgba(0,119,181,0.12)",   text: "#388bfd",  border: "rgba(0,119,181,0.25)",  abbr: "LI" },
  instagram: { bg: "rgba(225,48,108,0.12)",  text: "#ff7b72",  border: "rgba(225,48,108,0.25)", abbr: "IG" },
  facebook:  { bg: "rgba(24,119,242,0.12)",  text: "#79c0ff",  border: "rgba(24,119,242,0.25)", abbr: "FB" },
  x:         { bg: "rgba(255,255,255,0.06)", text: "#c9d1d9",  border: "rgba(255,255,255,0.15)", abbr: "X" },
};

function uid() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

const QUICK_ASKS = [
  "Best time to post on LinkedIn?",
  "Write a caption for a product launch",
  "Hashtag strategy for Instagram",
  "How to boost engagement this week?",
];

const QUICK_AGENT_PROMPTS = [
  "Post a motivational Monday quote",
  "Share a professional tip about productivity",
  "Announce we just launched something exciting",
  "Post about the power of social media marketing",
];

type Props = {
  workspaceId: string;
};

export function AssistantPanel({ workspaceId }: Props) {
  const { toggleAssistant } = useWorkspaceChrome();
  const [mode, setMode] = useState<Mode>("ask");
  const [activeTab, setActiveTab] = useState<Tab>("chatbot");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState("marko-2.0-mini");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Fetch connections
  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) return;
    fetch(`${apiBaseUrl}/api/auth/connections`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.ok ? r.json() : [])
      .then((data: Connection[]) => {
        setSelectedPlatforms(data.map((c) => c.platform));
      })
      .catch(console.error);
  }, [workspaceId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 100)}px`;
  }, [input]);

  const addMessage = (role: Message["role"], content: string, extra?: Partial<Message>) => {
    const msg: Message = {
      id: uid(),
      role,
      content,
      timestamp: new Date(),
      ...extra,
    };
    setMessages((prev) => [...prev, msg]);
    return msg;
  };

  const sendMessage = async (text?: string) => {
    const prompt = (text ?? input).trim();
    if (!prompt) return;
    setInput("");
    setActiveTab("chatbot");

    addMessage("user", prompt);
    setLoading(true);

    try {
      const token = localStorage.getItem("auth_token");
      const body: Record<string, unknown> = {
        message: prompt,
        history: messages.map((m) => ({ role: m.role, content: m.content })),
        mode,
        model: selectedModel,
      };
      if (mode === "agent") {
        body.platforms = selectedPlatforms;
      }

      const groqKey = localStorage.getItem("groq_api_key");
      const openaiKey = localStorage.getItem("openai_api_key");

      const res = await fetch(`${apiBaseUrl}/api/chat/interact`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...(groqKey ? { "X-Groq-Api-Key": groqKey } : {}),
          ...(openaiKey ? { "X-OpenAI-Api-Key": openaiKey } : {}),
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res.json();
        addMessage("assistant", `⚠️ ${err.detail || "Error communicating with assistant."}`);
        return;
      }

      const data = await res.json();
      addMessage("assistant", data.response, {
        published: data.published ?? [],
      });

      if (data.published && data.published.length > 0) {
        for (const p of data.published) {
          addMessage("system", `✓ Posted to ${p.platform.charAt(0).toUpperCase() + p.platform.slice(1)}`);
        }
      }
    } catch (e: any) {
      addMessage("assistant", `⚠️ Connection error: ${e.message}. Is the backend running?`);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const switchMode = (newMode: Mode) => {
    setMode(newMode);
    addMessage(
      "system",
      newMode === "agent"
        ? "🤖 Switched to Agent mode — I can now post to your connected platforms."
        : "💬 Switched to Ask mode — I'll answer questions without posting anything."
    );
  };

  const handleModelChange = (val: string) => {
    if (val === "manage-keys") {
      window.dispatchEvent(new Event("open-settings-modal"));
    } else {
      setSelectedModel(val);
    }
  };

  const hasMessages = messages.length > 0;
  const quickPrompts = mode === "ask" ? QUICK_ASKS : QUICK_AGENT_PROMPTS;

  return (
    <aside className="relative flex h-full w-full shrink-0 flex-col border-l border-[rgba(255,255,255,0.08)] bg-[#000000]">
      {/* Header matches PM exactly */}
      <div className="flex h-[88px] shrink-0 items-center border-b border-[rgba(255,255,255,0.08)] bg-[#000000] px-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-[rgba(255,255,255,0.04)] bg-[#0b0b0b]">
            <img src="/marko%20ai.png" alt="MarkoAI" className="h-5 w-5 object-contain" />
          </div>
          <div>
            <div className="text-[1.02rem] font-semibold text-white leading-tight">Assistant</div>
            <div className="text-[10px] uppercase tracking-[0.16em] text-white/40 mt-0.5">
              {mode === "ask" ? "Read-only mode" : "Agent mode"}
            </div>
          </div>
        </div>

        <div className="ml-auto flex items-center gap-3">
          {/* New Chat / Clear Chat */}
          <button
            type="button"
            onClick={() => setMessages([])}
            className="text-[#ffffff] transition-opacity hover:opacity-80 p-1 rounded hover:bg-white/5"
            aria-label="New conversation"
            title="Clear Chat"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 5v14M5 12h14" />
            </svg>
          </button>

          {/* Saved Prompts */}
          <button
            type="button"
            onClick={() => {
              window.dispatchEvent(new Event("open-settings-modal"));
            }}
            className="text-[#ffffff]/50 hover:text-white transition-opacity hover:opacity-80 p-1 rounded hover:bg-white/5"
            aria-label="Saved prompts"
            title="Saved Prompts"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
            </svg>
          </button>

          {/* History */}
          <button
            type="button"
            className="text-[#ffffff]/50 hover:text-white transition-opacity hover:opacity-80 p-1 rounded hover:bg-white/5"
            aria-label="History"
            title="History"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v5l3 2" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.05 11A9 9 0 1 1 6 17.3" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 4v7h7" />
            </svg>
          </button>

          {/* Close Panel */}
          <button
            type="button"
            className="text-[#ffffff] transition-opacity hover:opacity-80 p-1 rounded hover:bg-white/5"
            aria-label="Close panel"
            onClick={() => toggleAssistant()}
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Tabs segment matching PM */}
      <div className="px-4 py-3 shrink-0">
        <div className="rounded-[0.9rem] border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] p-1">
          <div className="grid grid-cols-2 gap-1">
            <button
              type="button"
              onClick={() => setActiveTab("chatbot")}
              className={`flex items-center justify-center gap-1.5 rounded-[0.72rem] px-3 py-2.5 text-[0.84rem] font-semibold transition ${
                activeTab === "chatbot" ? "bg-black text-white" : "text-white/72 hover:bg-white/5"
              }`}
            >
              <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.85}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h8M8 14h5m-8 6 3.6-3H19a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2v3Z" />
              </svg>
              Chatbot
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("suggestions")}
              className={`flex items-center justify-center gap-1.5 rounded-[0.72rem] px-3 py-2.5 text-[0.84rem] font-semibold transition ${
                activeTab === "suggestions" ? "bg-black text-white" : "text-white/72 hover:bg-white/5"
              }`}
            >
              <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.85}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.75c.86.6 1.5 1.49 1.75 2.49h4.5c.25-1 .89-1.89 1.75-2.49A7 7 0 0 0 12 2Z" />
              </svg>
              Suggestions
            </button>
          </div>
        </div>
      </div>

      {/* Main chat list */}
      <div className="flex-1 overflow-y-auto px-5 py-5 space-y-4">
        {activeTab === "suggestions" ? (
          <div className="space-y-4 animate-fade-up">
            <div className="p-3.5 rounded-xl border border-[rgba(255,255,255,0.04)] bg-[#000000]/60">
              <h5 className="text-xs font-bold text-white uppercase tracking-wider mb-1">Prompt Library</h5>
              <p className="text-[10px] text-white/40">Select a focused strategic action to run instantly.</p>
            </div>
            <div className="space-y-2">
              {quickPrompts.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="w-full text-left rounded-xl px-4 py-3 text-xs transition-all duration-200 bg-[#000000]/80 hover:bg-[#0a0a0a] border border-[rgba(255,255,255,0.04)] text-white/70 hover:text-white hover:border-[#388bfd]/50 btn-press"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4 animate-fade-up">
            {!hasMessages && (
              <div className="flex h-full items-center justify-center py-20">
                <div className="max-w-[19rem] text-center text-sm leading-6 text-white/55">
                  Ask mode is for Q&amp;A and fetching context. Agent mode can prepare optimizations or Meta budget changes, always behind confirmation.
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} ${msg.role === "system" ? "justify-center" : ""}`}
              >
                {msg.role === "system" ? (
                  <div className="px-3 py-1 rounded-full text-[10px] font-bold border bg-green-500/10 text-green-400 border-green-500/20">
                    {msg.content}
                  </div>
                ) : msg.role === "user" ? (
                  <div className="flex flex-col items-end gap-1 max-w-[88%]">
                    <div className="rounded-2xl bg-[rgba(255,255,255,0.06)] px-3 py-2 text-[0.85rem] leading-relaxed text-white/90">
                      {msg.content}
                    </div>
                    <span className="text-[9px] text-white/30">{formatTime(msg.timestamp)}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-start gap-1 max-w-[90%] w-full">
                    <div className="w-full rounded-2xl border border-[rgba(255,255,255,0.06)] bg-[rgba(255,255,255,0.02)] px-3 py-3">
                      <div className="text-[0.85rem] leading-relaxed text-white/80 whitespace-pre-wrap">
                        {msg.content}
                      </div>
                      <div className="mt-2 text-[11px] uppercase tracking-[0.14em] text-white/40">
                        {selectedModel}
                      </div>
                    </div>
                    {msg.published && msg.published.length > 0 && (
                      <div className="mt-1 flex flex-wrap gap-1">
                        {msg.published.map((p) => {
                          const s = PLATFORM_STYLES[p.platform] || PLATFORM_STYLES.x;
                          return (
                            <span
                              key={p.platform}
                              className="px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider border"
                              style={{ background: s.bg, color: s.text, borderColor: s.border }}
                            >
                              ✓ {p.platform}
                            </span>
                          );
                        })}
                      </div>
                    )}
                    <span className="text-[9px] text-white/30">{formatTime(msg.timestamp)}</span>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="flex flex-col items-start gap-1 max-w-[90%] w-full">
                  <div className="w-full rounded-2xl border border-[rgba(255,255,255,0.06)] bg-[rgba(255,255,255,0.02)] px-3 py-3 flex items-center gap-2.5">
                    <div className="h-3.5 w-3.5 rounded-full border border-t-transparent animate-spin border-white/60" />
                    <span className="text-xs text-white/50">
                      {mode === "agent" ? "Publishing content..." : "Assistant is thinking..."}
                    </span>
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input composer matches PM */}
      <div className="shrink-0 p-3 bg-[#000000]" style={{ borderTop: "1px solid rgba(255,255,255,0.08)" }}>
        <div className="flex flex-col gap-2 p-2 rounded-xl bg-[#080808] border border-[#161616]">
          <span className="text-[9px] text-white/25 px-1 font-semibold">
            Add context (#), extensions (@), commands (/)
          </span>

          {mode === "agent" && (
            <div className="flex items-center gap-2 px-1 py-1.5 border-b border-white/5 select-none animate-fade-up">
              <span className="text-[9px] uppercase font-bold text-white/40 tracking-wider">Post To:</span>
              <div className="flex items-center gap-1.5 flex-wrap">
                {["facebook", "instagram", "linkedin", "x"].map((platform) => {
                  const isSelected = selectedPlatforms.includes(platform);
                  const s = PLATFORM_STYLES[platform] || PLATFORM_STYLES.x;
                  return (
                    <button
                      key={platform}
                      type="button"
                      onClick={() => {
                        setSelectedPlatforms((prev) =>
                          prev.includes(platform) ? prev.filter((p) => p !== platform) : [...prev, platform]
                        );
                      }}
                      className={`flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase transition-all duration-200 border cursor-pointer ${
                        isSelected
                          ? "shadow-[0_2px_8px_rgba(31,111,235,0.15)]"
                          : "opacity-40 hover:opacity-75"
                      }`}
                      style={{
                        background: isSelected ? s.bg : "transparent",
                        color: isSelected ? s.text : "#8b949e",
                        borderColor: isSelected ? s.border : "rgba(255,255,255,0.08)",
                      }}
                    >
                      {isSelected ? "✓" : "+"} {platform}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            rows={1}
            placeholder={mode === "ask" ? "Ask or instruct the assistant..." : "Tell me what to post..."}
            className="w-full resize-none bg-transparent text-xs outline-none disabled:opacity-50 px-1 py-1"
            style={{
              color: "#e6edf3",
              lineHeight: "1.5",
              minHeight: "24px",
              maxHeight: "100px",
            }}
          />

          <div className="flex items-center justify-between pt-1.5 border-t border-white/5 px-1">
            <div className="flex items-center gap-1.5">
              <select
                value={mode}
                onChange={(e) => switchMode(e.target.value as Mode)}
                disabled={loading}
                className="bg-[#0a0a0a] hover:bg-white/5 border border-[rgba(255,255,255,0.08)] rounded-md px-2 py-1 text-[10px] font-bold text-white/70 outline-none transition-colors appearance-none cursor-pointer pr-5"
                style={{
                  backgroundImage: "url('data:image/svg+xml;charset=UTF-8,%3csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%238b949e%22 stroke-width=%222.5%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22%3e%3cpolyline points=%226 9 12 15 18 9%22%3e%3c/polyline%3e%3c/svg%3e')",
                  backgroundRepeat: "no-repeat",
                  backgroundPosition: "right 6px center",
                  backgroundSize: "10px",
                }}
              >
                <option value="ask">Ask</option>
                <option value="agent">Agent</option>
              </select>

              <select
                value={selectedModel}
                onChange={(e) => handleModelChange(e.target.value)}
                disabled={loading}
                className="bg-[#0a0a0a] hover:bg-white/5 border border-[rgba(255,255,255,0.08)] rounded-md px-2 py-1 text-[10px] font-bold text-white/70 outline-none transition-colors appearance-none cursor-pointer pr-5"
                style={{
                  backgroundImage: "url('data:image/svg+xml;charset=UTF-8,%3csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%238b949e%22 stroke-width=%222.5%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22%3e%3cpolyline points=%226 9 12 15 18 9%22%3e%3c/polyline%3e%3c/svg%3e')",
                  backgroundRepeat: "no-repeat",
                  backgroundPosition: "right 6px center",
                  backgroundSize: "10px",
                }}
              >
                <option value="marko-2.0-mini">marko-2.0-mini</option>
                <option value="groq-llama-3.1-8b">groq-llama-3.1-8b</option>
                <option value="gpt-4o-mini">gpt-4o-mini</option>
                <option value="manage-keys">Manage API Keys...</option>
              </select>
            </div>

            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="shrink-0 flex h-6 w-6 items-center justify-center rounded-lg transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed text-white shadow-sm btn-press"
              style={{ background: mode === "agent" ? "#1f6feb" : "#238636" }}
            >
              {loading ? (
                <div className="h-3 w-3 rounded-full border border-white/40 border-t-white animate-spin" />
              ) : (
                <svg viewBox="0 0 16 16" className="h-3 w-3 fill-current">
                  <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576 6.636 10.07Z"/>
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}
