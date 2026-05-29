import { useState, type FormEvent } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { apiBaseUrl } from '../../lib/api/client';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/connect';

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isLogin ? '/api/users/login' : '/api/users/register';
      const body = isLogin 
        ? { email, password }
        : { email, password, name };
      const apiBaseUrl = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

      const response = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      login(data.access_token, data.user);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl items-center justify-center px-5 py-12 lg:px-8">
      <div className="grid w-full gap-8 xl:grid-cols-[1.1fr_0.9fr]">

        {/* Left: Hero panel */}
        <section className="shell-surface rounded-[2rem] p-8 shadow-panel">
          <p className="text-[10px] font-semibold uppercase tracking-[0.35em] text-white/35">
            Social Manager
          </p>
          <h1 className="mt-4 text-4xl font-black tracking-tight text-ink md:text-6xl">
            Manage all your social media from one place
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-8 text-white/58">
            Connect your Facebook, Instagram, and LinkedIn accounts. 
            Publish content across all platforms simultaneously. 
            Track engagement and grow your audience.
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {[
              {
                title: "Multi-platform",
                detail: "Connect Facebook Pages, Instagram Business, and LinkedIn — all in one dashboard.",
              },
              {
                title: "One-click publish",
                detail: "Write once, select your platforms, and post everywhere simultaneously.",
              },
              {
                title: "Per-user accounts",
                detail: "Each client connects their own accounts. Your data stays yours.",
              },
            ].map((card) => (
              <div
                key={card.title}
                className="rounded-3xl border border-white/8 bg-white/[0.04] p-5"
              >
                <p className="text-sm font-semibold">{card.title}</p>
                <p className="mt-3 text-sm leading-6 text-white/58">{card.detail}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Right: Form panel */}
        <section className="rounded-[2rem] border border-black/10 bg-white p-8 text-black shadow-panel">
          <h2 className="text-2xl font-semibold">
            {isLogin ? 'Sign in' : 'Create account'}
          </h2>
          <p className="mt-2 text-sm leading-7 text-black/65">
            {isLogin 
              ? 'Enter your credentials to access your dashboard.' 
              : 'Set up your account to start managing your social media.'}
          </p>

          {error && (
            <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 p-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            {!isLogin && (
              <label className="block">
                <span className="mb-2 block text-sm font-medium">Full name</span>
                <input
                  required
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                  placeholder="Jordan Rivera"
                />
              </label>
            )}

            <label className="block">
              <span className="mb-2 block text-sm font-medium">Email address</span>
              <input
                required
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                placeholder="jordan@acme.co"
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium">Password</span>
              <input
                required
                type="password"
                autoComplete={isLogin ? "current-password" : "new-password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                placeholder="••••••••"
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-full bg-black px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_50px_rgba(0,0,0,0.18)] disabled:opacity-60"
            >
              {loading ? 'Processing...' : (isLogin ? 'Sign in' : 'Create account')}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-black/50">
            {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
            <button
              onClick={() => { setIsLogin(!isLogin); setError(''); }}
              className="font-semibold text-black hover:underline"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </section>

      </div>
    </div>
  );
}
