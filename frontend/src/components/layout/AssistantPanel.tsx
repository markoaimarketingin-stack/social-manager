import { useEffect, useRef, useState } from "react";
import { apiBaseUrl } from "../../lib/api/client";

type Mode = "ask" | "agent";

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
  linkedin:  { bg: "rgba(0,119,181,0.15)",   text: "#58a6ff",  border: "rgba(0,119,181,0.3)",   abbr: "LI" },
  instagram: { bg: "rgba(225,48,108,0.15)",  text: "#f78166",  border: "rgba(225,48,108,0.3)",  abbr: "IG" },
  facebook:  { bg: "rgba(24,119,242,0.15)",  text: "#79c0ff",  border: "rgba(24,119,242,0.3)",  abbr: "FB" },
  x:         { bg: "rgba(255,255,255,0.08)", text: "#e6edf3",  border: "rgba(255,255,255,0.2)", abbr: "X" },
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
  const [mode, setMode] = useState<Mode>("ask");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
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
        setConnections(data);
        setSelectedPlatforms(data.map((c) => c.platform));
      })
      .catch(console.error);
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`;
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

    addMessage("user", prompt);
    setLoading(true);

    try {
      const token = localStorage.getItem("auth_token");
      const body: Record<string, unknown> = {
        message: prompt,
        history: messages.map((m) => ({ role: m.role, content: m.content })),
        mode,
      };
      if (mode === "agent") {
        body.platforms = selectedPlatforms;
      }

      const res = await fetch(`${apiBaseUrl}/api/chat/interact`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
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

  const togglePlatform = (platform: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platform) ? prev.filter((p) => p !== platform) : [...prev, platform]
    );
  };

  const switchMode = (newMode: Mode) => {
    setMode(newMode);
    if (messages.length === 0) return;
    addMessage(
      "system",
      newMode === "agent"
        ? "🤖 Switched to Agent mode — I can now post to your connected platforms."
        : "💬 Switched to Ask mode — I'll answer questions without posting anything."
    );
  };

  const hasMessages = messages.length > 0;
  const quickPrompts = mode === "ask" ? QUICK_ASKS : QUICK_AGENT_PROMPTS;

  return (
    <div
      className="flex h-full w-full flex-col"
      style={{ background: "#161b22", color: "#e6edf3" }}
    >
      {/* Header */}
      <div
        className="shrink-0 px-4 py-3 flex items-center justify-between"
        style={{ borderBottom: "1px solid #21262d" }}
      >
        <div className="flex items-center gap-2.5">
          <div
            className="flex h-7 w-7 items-center justify-center rounded-md assistant-orb"
            style={{ background: "linear-gradient(135deg, #1f6feb, #388bfd)" }}
          >
            <svg viewBox="0 0 16 16" className="h-4 w-4 fill-white">
              <path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5ZM3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.58 26.58 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.933.933 0 0 1-.765.935c-.845.147-2.34.346-4.235.346-1.895 0-3.39-.2-4.235-.346A.933.933 0 0 1 3 9.219V8.062Zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a24.767 24.767 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25.286 25.286 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.134Z"/>
              <path d="M8 1c-1.573 0-3.022.289-4.096.777C2.875 2.245 2 2.993 2 4s.875 1.755 1.904 2.223C4.978 6.711 6.427 7 8 7s3.022-.289 4.096-.777C13.125 5.755 14 5.007 14 4s-.875-1.755-1.904-2.223C11.022 1.289 9.573 1 8 1ZM2.056 4h11.888L8 7.083 2.056 4ZM8 5a1 1 0 0 1 0-2 1 1 0 0 1 0 2Z"/>
            </svg>
          </div>
          <div>
            <p className="font-semibold text-sm leading-tight" style={{ color: "#e6edf3" }}>AI Assistant</p>
            <p className="text-xs" style={{ color: "#388bfd" }}>Social Manager</p>
          </div>
        </div>

        {/* Mode switcher */}
        <div
          className="flex rounded-md overflow-hidden text-xs font-medium"
          style={{ border: "1px solid #30363d" }}
        >
          <button
            onClick={() => switchMode("ask")}
            className="px-3 py-1.5 transition-colors"
            style={{
              background: mode === "ask" ? "#238636" : "transparent",
              color: mode === "ask" ? "#fff" : "#6e7681",
            }}
          >
            Ask
          </button>
          <button
            onClick={() => switchMode("agent")}
            className="px-3 py-1.5 transition-colors"
            style={{
              background: mode === "agent" ? "#1f6feb" : "transparent",
              color: mode === "agent" ? "#fff" : "#6e7681",
              borderLeft: "1px solid #30363d",
            }}
          >
            Agent
          </button>
        </div>
      </div>

      {/* Mode indicator banner */}
      <div
        className="shrink-0 px-4 py-2 text-xs"
        style={{
          background: mode === "agent" ? "rgba(31,111,235,0.08)" : "rgba(35,134,54,0.06)",
          borderBottom: "1px solid #21262d",
          color: mode === "agent" ? "#388bfd" : "#3fb950",
        }}
      >
        {mode === "agent"
          ? "🤖 Agent mode — I will generate and post content to your platforms"
          : "💬 Ask mode — I will answer questions and give advice (no posting)"}
      </div>

      {/* Platform selector (agent mode only) */}
      {mode === "agent" && connections.length > 0 && (
        <div
          className="shrink-0 px-4 py-2 flex flex-wrap gap-1.5"
          style={{ borderBottom: "1px solid #21262d" }}
        >
          <span className="text-xs mr-1 self-center" style={{ color: "#484f58" }}>Post to:</span>
          {connections.map((c) => {
            const s = PLATFORM_STYLES[c.platform] || PLATFORM_STYLES.x;
            const selected = selectedPlatforms.includes(c.platform);
            return (
              <button
                key={c.platform}
                onClick={() => togglePlatform(c.platform)}
                className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium transition-all"
                style={{
                  background: selected ? s.bg : "transparent",
                  color: selected ? s.text : "#484f58",
                  border: `1px solid ${selected ? s.border : "#30363d"}`,
                }}
              >
                <span>{s.abbr}</span>
                <span className="capitalize">{c.platform}</span>
              </button>
            );
          })}
          {connections.length === 0 && (
            <span className="text-xs" style={{ color: "#f85149" }}>No platforms connected</span>
          )}
        </div>
      )}

      {/* Messages area */}
      <div className="scrollbar-thin flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {!hasMessages && (
          <div className="space-y-5">
            {/* Welcome */}
            <div className="text-center pt-4">
              <div
                className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full"
                style={{ background: "rgba(31,111,235,0.15)", border: "1px solid rgba(31,111,235,0.3)" }}
              >
                <svg viewBox="0 0 16 16" className="h-6 w-6 fill-current" style={{ color: "#388bfd" }}>
                  <path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5ZM3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.58 26.58 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.933.933 0 0 1-.765.935c-.845.147-2.34.346-4.235.346-1.895 0-3.39-.2-4.235-.346A.933.933 0 0 1 3 9.219V8.062Zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a24.767 24.767 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25.286 25.286 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.134Z"/>
                </svg>
              </div>
              <p className="font-semibold text-sm" style={{ color: "#e6edf3" }}>
                {mode === "ask" ? "Ask me anything" : "I'm ready to post"}
              </p>
              <p className="text-xs mt-1" style={{ color: "#6e7681" }}>
                {mode === "ask"
                  ? "Ask about social media strategy, content ideas, or analytics."
                  : "Tell me what to post and I'll craft and publish it to your connected platforms."}
              </p>
            </div>

            {/* Quick prompts */}
            <div className="space-y-1.5">
              <p className="text-xs uppercase tracking-wide font-medium" style={{ color: "#484f58" }}>
                {mode === "ask" ? "Quick questions" : "Quick actions"}
              </p>
              {quickPrompts.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="w-full text-left rounded-md px-3 py-2 text-xs transition-colors"
                  style={{
                    background: "#21262d",
                    color: "#8b949e",
                    border: "1px solid #30363d",
                  }}
                  onMouseEnter={(e) => {
                    (e.target as HTMLElement).style.background = "#30363d";
                    (e.target as HTMLElement).style.color = "#e6edf3";
                  }}
                  onMouseLeave={(e) => {
                    (e.target as HTMLElement).style.background = "#21262d";
                    (e.target as HTMLElement).style.color = "#8b949e";
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex assistant-message ${msg.role === "user" ? "justify-end" : "justify-start"} ${msg.role === "system" ? "justify-center" : ""}`}
          >
            {msg.role === "system" ? (
              <div className="chat-bubble-system">{msg.content}</div>
            ) : msg.role === "user" ? (
              <div className="flex flex-col items-end gap-1 max-w-[88%]">
                <div className="chat-bubble-user">{msg.content}</div>
                <span className="text-xs" style={{ color: "#484f58" }}>{formatTime(msg.timestamp)}</span>
              </div>
            ) : (
              <div className="flex flex-col items-start gap-1 max-w-[92%]">
                <div className="flex items-center gap-1.5 mb-0.5">
                  <div
                    className="h-4 w-4 rounded flex items-center justify-center text-white"
                    style={{ background: "#1f6feb", fontSize: "9px", fontWeight: "bold" }}
                  >
                    AI
                  </div>
                  <span className="text-xs font-medium" style={{ color: "#6e7681" }}>AI Assistant</span>
                </div>
                <div className="chat-bubble-assistant" style={{ whiteSpace: "pre-wrap" }}>
                  {msg.content}
                </div>
                {msg.published && msg.published.length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {msg.published.map((p) => {
                      const s = PLATFORM_STYLES[p.platform] || PLATFORM_STYLES.x;
                      return (
                        <span
                          key={p.platform}
                          className="px-2 py-0.5 rounded-full text-xs font-medium"
                          style={{ background: s.bg, color: s.text, border: `1px solid ${s.border}` }}
                        >
                          ✓ {p.platform}
                        </span>
                      );
                    })}
                  </div>
                )}
                <span className="text-xs" style={{ color: "#484f58" }}>{formatTime(msg.timestamp)}</span>
              </div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start assistant-message">
            <div className="flex flex-col items-start gap-1">
              <div className="flex items-center gap-1.5 mb-0.5">
                <div
                  className="h-4 w-4 rounded flex items-center justify-center text-white"
                  style={{ background: "#1f6feb", fontSize: "9px", fontWeight: "bold" }}
                >
                  AI
                </div>
                <span className="text-xs font-medium" style={{ color: "#6e7681" }}>AI Assistant</span>
              </div>
              <div
                className="chat-bubble-assistant flex items-center gap-2"
                style={{ minWidth: "80px" }}
              >
                <div
                  className="h-3.5 w-3.5 rounded-full border border-t-transparent animate-spin"
                  style={{ borderColor: "#388bfd", borderTopColor: "transparent" }}
                />
                <span className="text-xs" style={{ color: "#6e7681" }}>
                  {mode === "agent" ? "Drafting & posting…" : "Thinking…"}
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input dock */}
      <div className="shrink-0 p-3" style={{ borderTop: "1px solid #21262d" }}>
        <div
          className="assistant-dock flex items-end gap-2 px-3 py-2"
          style={{ borderRadius: "8px" }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            rows={1}
            placeholder={
              mode === "ask"
                ? "Ask about social media…"
                : "Tell me what to post…"
            }
            className="flex-1 resize-none bg-transparent text-sm outline-none disabled:opacity-50"
            style={{
              color: "#e6edf3",
              lineHeight: "1.5",
              fontFamily: "inherit",
              minHeight: "24px",
              maxHeight: "120px",
            }}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="shrink-0 flex h-7 w-7 items-center justify-center rounded-md transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{ background: mode === "agent" ? "#1f6feb" : "#238636" }}
            onMouseEnter={(e) => !loading && !(!input.trim()) && ((e.target as HTMLElement).style.opacity = "0.85")}
            onMouseLeave={(e) => !loading && !(!input.trim()) && ((e.target as HTMLElement).style.opacity = "1")}
          >
            {loading ? (
              <div
                className="h-3.5 w-3.5 rounded-full border border-white/40 border-t-white animate-spin"
              />
            ) : (
              <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-white">
                <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576 6.636 10.07Zm6.787-8.201L1.591 6.602l4.339 2.76 7.494-7.493Z"/>
              </svg>
            )}
          </button>
        </div>
        <p className="mt-1.5 text-center text-xs" style={{ color: "#484f58" }}>
          {mode === "agent" && selectedPlatforms.length > 0
            ? `Will post to: ${selectedPlatforms.join(", ")}`
            : mode === "agent"
            ? "Select platforms above"
            : "Enter to send · Shift+Enter for new line"}
        </p>
      </div>
    </div>
  );
}
