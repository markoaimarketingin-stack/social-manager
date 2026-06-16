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
    console.log("Loading assistant panel for workspace:", workspaceId);
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
    setActiveTab("chatbot"); // Auto switch to chatbot if suggestion clicked

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

      // Add custom api keys to headers if configured locally
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

      // If posted, add a system confirmation for each platform
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
    <div
      className="flex h-full w-full flex-col"
      style={{ background: "#080808", color: "#e6edf3", borderLeft: "1px solid rgba(255,255,255,0.04)" }}
    >
      {/* Header */}
      <div
        className="shrink-0 px-4 py-3.5 flex items-center justify-between"
        style={{ borderBottom: "1px solid #111111" }}
      >
        <div className="flex items-center gap-2">
          <div
            className="flex h-6 w-6 items-center justify-center rounded-lg text-white"
            style={{ background: "linear-gradient(135deg, #1f6feb, #388bfd)", border: "1px solid rgba(255,255,255,0.1)" }}
          >
            <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current">
              <path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5ZM3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.58 26.58 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.933.933 0 0 1-.765.935c-.845.147-2.34.346-4.235.346-1.895 0-3.39-.2-4.235-.346A.933.933 0 0 1 3 9.219V8.062Zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a24.767 24.767 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25.286 25.286 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.134Z"/>
            </svg>
          </div>
          <div>
            <h4 className="font-bold text-xs" style={{ color: "#ffffff", lineHeight: 1.1 }}>Assistant</h4>
            <span
              className="text-[9px] font-bold tracking-wider"
              style={{ color: mode === "agent" ? "#388bfd" : "#8b949e" }}
            >
              {mode === "agent" ? "AGENT MODE" : "READ-ONLY MODE"}
            </span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setMessages([])}
            className="p-1 rounded hover:bg-white/5 text-white/50 hover:text-white transition-colors"
            title="Clear Chat"
          >
            <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current">
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
              <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>
          </button>
          <button
            onClick={() => toggleAssistant()}
            className="p-1 rounded hover:bg-white/5 text-white/50 hover:text-white transition-colors"
            title="Collapse Panel"
          >
            <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current">
              <path d="M3.72 3.72a.75.75 0 0 1 1.06 0L8 6.94l3.22-3.22a.75.75 0 1 1 1.06 1.06L9.06 8l3.22 3.22a.75.75 0 1 1-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 0 1-1.06-1.06L8 9.06l-3.22 3.22a.75.75 0 0 1-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 0 1 0-1.06z"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Internal Tabs Switcher */}
      <div className="shrink-0 px-4 py-2 border-b border-[#161b22] flex gap-4 text-xs font-semibold">
        <button
          onClick={() => setActiveTab("chatbot")}
          className="flex items-center gap-1.5 pb-2 transition-all border-b-2 relative -bottom-[9px]"
          style={{
            color: activeTab === "chatbot" ? "#388bfd" : "#6e7681",
            borderColor: activeTab === "chatbot" ? "#388bfd" : "transparent",
          }}
        >
          <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current">
            <path d="M5 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/>
            <path d="m2.165 15.803.02-.004c1.83-.363 2.948-.842 3.468-1.105A9.06 9.06 0 0 0 8 15c4.418 0 8-3.134 8-7s-3.582-7-8-7-8 3.134-8 7c0 1.76.743 3.37 1.97 4.6a10.437 10.437 0 0 1-1.805 3.195.5.5 0 0 0 .425.808a10.43 10.43 0 0 0 1.575-.105zM1.01 8c0-3.31 3.13-6 7-6s7 2.69 7 6-3.13 6-7 6a8.032 8.032 0 0 1-2.31-.34A.5.5 0 0 0 5 13.7c-.42.27-1.42.75-2.77 1.07a8.497 8.497 0 0 0 1.01-1.92.5.5 0 0 0-.17-.552C2.07 11.23 1.01 9.7 1.01 8z"/>
          </svg>
          Chatbot
        </button>
        <button
          onClick={() => setActiveTab("suggestions")}
          className="flex items-center gap-1.5 pb-2 transition-all border-b-2 relative -bottom-[9px]"
          style={{
            color: activeTab === "suggestions" ? "#388bfd" : "#6e7681",
            borderColor: activeTab === "suggestions" ? "#388bfd" : "transparent",
          }}
        >
          <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current">
            <path d="M2 6a6 6 0 1 1 10.174 4.31c-.203.196-.359.4-.453.619l-.762 1.769A.5.5 0 0 1 8.5 13h-1a.5.5 0 0 1-.46-.31l-.762-1.77a2.235 2.235 0 0 0-.453-.618A5.984 5.984 0 0 1 2 6zm6-5a5 5 0 0 0-3.479 8.592c.263.254.514.564.676.941L5.83 12h4.34l.632-1.467c.162-.377.413-.687.676-.941A5 5 0 0 0 8 1z"/>
          </svg>
          Suggestions
        </button>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 scrollbar-thin space-y-4">
        {activeTab === "suggestions" ? (
          /* Suggestions Panel View */
          <div className="space-y-4 animate-fadeIn">
            <div className="p-3.5 rounded-xl border border-[#21262d] bg-[#0d1117]/60">
              <h5 className="text-xs font-bold text-white uppercase tracking-wider mb-1">Prompt Library</h5>
              <p className="text-[10px] text-white/40">Select a focused strategic action to run instantly.</p>
            </div>
            <div className="space-y-2">
              {quickPrompts.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="w-full text-left rounded-xl px-4 py-3 text-xs transition-all duration-200 bg-[#0d1117]/80 hover:bg-[#161b22] border border-[#21262d] text-white/70 hover:text-white hover:border-[#388bfd]/50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Chatbot Panel View */
          <div className="space-y-4 animate-fadeIn">
            {!hasMessages && (
              <div className="text-center py-10 space-y-3">
                <div className="h-10 w-10 mx-auto flex items-center justify-center rounded-full bg-white/[0.02] border border-[#21262d] text-white/50">
                  💬
                </div>
                <div>
                  <p className="text-xs font-bold text-white/80">
                    {mode === "ask" ? "Ask me anything" : "I'm ready to post"}
                  </p>
                  <p className="text-[10px] text-white/40 mt-1 max-w-[200px] mx-auto leading-relaxed">
                    {mode === "ask"
                      ? "Ask about strategy, draft content, or retrieve information."
                      : "Provide a description of your post, and I will publish it to your connected platforms."}
                  </p>
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} ${msg.role === "system" ? "justify-center" : ""}`}
              >
                {msg.role === "system" ? (
                  <div
                    className="px-3 py-1 rounded-full text-[10px] font-bold border"
                    style={{ background: "rgba(35,134,54,0.06)", color: "#3fb950", borderColor: "rgba(35,134,54,0.2)" }}
                  >
                    {msg.content}
                  </div>
                ) : msg.role === "user" ? (
                  <div className="flex flex-col items-end gap-1 max-w-[85%]">
                    <div className="rounded-xl px-3 py-2 text-xs bg-[#1f6feb] text-white shadow-md leading-relaxed">
                      {msg.content}
                    </div>
                    <span className="text-[9px] text-white/30">{formatTime(msg.timestamp)}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-start gap-1 max-w-[90%]">
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <div className="h-4 w-4 rounded flex items-center justify-center text-[9px] font-bold bg-[#161b22] text-white/70 border border-[#30363d]">
                        AI
                      </div>
                      <span className="text-[10px] font-bold text-white/40">AI Assistant</span>
                    </div>
                    <div className="rounded-xl px-3.5 py-2.5 text-xs bg-[#161b22] border border-[#21262d] text-white/90 leading-relaxed shadow-sm whitespace-pre-wrap">
                      {msg.content}
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

            {/* Loading indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="flex flex-col items-start gap-1">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <div className="h-4 w-4 rounded flex items-center justify-center text-[9px] font-bold bg-[#161b22] text-white/70 border border-[#30363d]">
                      AI
                    </div>
                    <span className="text-[10px] font-bold text-white/40">AI Assistant</span>
                  </div>
                  <div className="rounded-xl px-3 py-2 text-xs bg-[#161b22] border border-[#21262d] text-white/40 flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full border border-t-transparent animate-spin border-[#388bfd]" />
                    <span>{mode === "agent" ? "Posting to platforms..." : "Thinking..."}</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input Dock at Bottom */}
      <div className="shrink-0 p-3 bg-[#000000]" style={{ borderTop: "1px solid #111111" }}>
        <div
          className="flex flex-col gap-2 p-2 rounded-xl bg-[#080808] border border-[#161616]"
        >
          {/* Helper details line */}
          <span className="text-[9px] text-white/25 px-1 font-semibold">
            Add context (#), extensions (@), commands (/)
          </span>

          {/* Connected Platforms Selector Pills (Only in Agent mode) */}
          {mode === "agent" && (
            <div className="flex items-center gap-2 px-1 py-1.5 border-b border-[#161b22] select-none animate-fadeIn">
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
                        borderColor: isSelected ? s.border : "#30363d",
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

          {/* Bottom Dock Controls Bar */}
          <div className="flex items-center justify-between pt-1.5 border-t border-[#161b22] px-1">
            <div className="flex items-center gap-1.5">
              {/* Mode Selector Dropdown */}
              <select
                value={mode}
                onChange={(e) => switchMode(e.target.value as Mode)}
                disabled={loading}
                className="bg-[#161b22] hover:bg-white/5 border border-[#30363d] rounded-md px-2 py-1 text-[10px] font-bold text-white/70 outline-none transition-colors appearance-none cursor-pointer pr-5"
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

              {/* Model Selector Dropdown */}
              <select
                value={selectedModel}
                onChange={(e) => handleModelChange(e.target.value)}
                disabled={loading}
                className="bg-[#161b22] hover:bg-white/5 border border-[#30363d] rounded-md px-2 py-1 text-[10px] font-bold text-white/70 outline-none transition-colors appearance-none cursor-pointer pr-5"
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

            {/* Send Button */}
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="shrink-0 flex h-6 w-6 items-center justify-center rounded-lg transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed text-white shadow-sm"
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
    </div>
  );
}
