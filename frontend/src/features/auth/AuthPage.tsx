import { useState, type FormEvent } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { apiBaseUrl } from "../../lib/api/client";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || "/workspaces/demo/dashboard";

  const authRequest = async (endpoint: string, body: { email: string; password: string; name?: string }) => {
    const bases = Array.from(new Set([apiBaseUrl, ""]));
    let lastError: unknown = null;

    for (const baseUrl of bases) {
      try {
        const response = await fetch(`${baseUrl}${endpoint}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        return response;
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError instanceof Error ? lastError : new Error("Failed to fetch");
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const endpoint = isLogin ? "/api/users/login" : "/api/users/register";
      const body = isLogin
        ? { email, password }
        : { email, password, name: name || email.split("@")[0] };

      const response = await authRequest(endpoint, body);

      const contentType = response.headers.get("content-type") || "";
      const rawBody = await response.text();
      let data: any = null;

      if (rawBody) {
        try {
          data = contentType.includes("application/json")
            ? JSON.parse(rawBody)
            : JSON.parse(rawBody);
        } catch {
          data = { detail: rawBody };
        }
      }

      if (!response.ok) {
        throw new Error(data?.detail || rawBody || "Authentication failed");
      }

      if (!data?.access_token) {
        throw new Error("Authentication response missing token");
      }

      login(data.access_token, data.user);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGuestMode = () => {
    const guestToken = "guest-demo-token";
    const guestUser = { id: 0, email: "guest@demo.ai", name: "Demo User" };
    login(guestToken, guestUser);
    navigate("/workspaces/demo/dashboard", { replace: true });
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#050505] text-white flex items-center justify-center">
      {/* Background gradients aligned with PM */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.14),_transparent_35%),radial-gradient(circle_at_bottom_right,_rgba(255,196,86,0.16),_transparent_32%)]" />
      <div className="absolute inset-x-0 top-0 h-72 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),transparent)]" />

      <div className="relative mx-auto flex w-full max-w-md flex-col justify-center px-4 py-10">
        <section className="rounded-[2rem] border border-white/10 bg-[#0d0d0d]/90 p-6 shadow-[0_28px_90px_rgba(0,0,0,0.42)] backdrop-blur sm:p-8 animate-fade-up">
          
          {/* Header Row */}
          <div className="mb-6 flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-white/42">
                {isLogin ? "Welcome back" : "Get started"}
              </p>
              <h2 className="mt-2 text-3xl font-semibold tracking-tight text-white leading-tight">
                {isLogin ? "Continue with email." : "Create your account."}
              </h2>
            </div>
            <div className="grid h-14 w-14 shrink-0 place-items-center rounded-[1.2rem] border border-white/12 bg-white text-black shadow-[0_16px_32px_rgba(255,255,255,0.12)] select-none">
              <span className="text-xl font-bold">M</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            
            {/* Full Name (Sign Up only) */}
            {!isLogin && (
              <div>
                <label htmlFor="name" className="mb-1.5 block text-sm font-medium text-white/78">
                  Full name
                </label>
                <input
                  id="name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  className="w-full rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white placeholder-white/28 outline-none transition focus:border-white/30 focus:bg-white/[0.06]"
                />
              </div>
            )}

            {/* Email */}
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-white/78">
                Work email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white placeholder-white/28 outline-none transition focus:border-white/30 focus:bg-white/[0.06]"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-white/78">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white placeholder-white/28 outline-none transition focus:border-white/30 focus:bg-white/[0.06]"
              />
            </div>

            {/* Info Box */}
            <div className="rounded-[1rem] border border-[#f5c35f]/15 bg-[#f5c35f]/[0.06] px-4 py-3 text-sm leading-6 text-white/70">
              {isLogin
                ? "Your workspace, platform connections, and assistant settings resolve automatically after email login."
                : "After registration you will be redirected to connect your social media platforms."}
            </div>

            {/* Error message */}
            {error && (
              <div className="rounded-[1rem] border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}

            {/* Submit button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-[1rem] bg-white py-3 text-sm font-semibold text-black transition hover:-translate-y-0.5 hover:shadow-[0_18px_36px_rgba(255,255,255,0.18)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0 btn-press"
            >
              {loading ? "Processing…" : (isLogin ? "Log in" : "Create account")}
            </button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center gap-3">
            <div className="h-px flex-1 bg-white/10" />
            <span className="text-[0.7rem] font-medium uppercase tracking-[0.26em] text-white/30">or</span>
            <div className="h-px flex-1 bg-white/10" />
          </div>

          {/* Guest / Demo button */}
          <button
            type="button"
            onClick={handleGuestMode}
            className="w-full rounded-[1rem] border border-white/10 bg-transparent py-3 text-sm font-medium text-white transition hover:bg-white/[0.05] btn-press"
          >
            Continue as guest
            <span className="ml-2 text-xs text-white/42">(mock workspace)</span>
          </button>

          {/* Toggle link */}
          <p className="mt-5 text-center text-xs text-white/35">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => { setIsLogin(!isLogin); setError(""); }}
              className="font-semibold transition-colors hover:text-white underline cursor-pointer text-white/60"
            >
              {isLogin ? "Sign up" : "Sign in"}
            </button>
          </p>

        </section>
      </div>
    </main>
  );
}
