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

  const authRequest = async (endpoint: string, body: { email: string; password: string; name?: string }) => {
    const bases = Array.from(new Set([apiBaseUrl, '']));
    let lastError: unknown = null;

    for (const baseUrl of bases) {
      try {
        const response = await fetch(`${baseUrl}${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        return response;
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError instanceof Error ? lastError : new Error('Failed to fetch');
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isLogin ? '/api/users/login' : '/api/users/register';
      const body = isLogin
        ? { email, password }
        : { email, password, name: name || email.split('@')[0] };

      const response = await authRequest(endpoint, body);

      const contentType = response.headers.get('content-type') || '';
      const rawBody = await response.text();
      let data: any = null;

      if (rawBody) {
        try {
          data = contentType.includes('application/json')
            ? JSON.parse(rawBody)
            : JSON.parse(rawBody);
        } catch {
          data = { detail: rawBody };
        }
      }

      if (!response.ok) {
        throw new Error(data?.detail || rawBody || 'Authentication failed');
      }

      if (!data?.access_token) {
        throw new Error('Authentication response missing token');
      }

      login(data.access_token, data.user);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Guest / demo mode — skips real auth
  const handleGuestMode = () => {
    const guestToken = 'guest-demo-token';
    const guestUser = { id: 0, email: 'guest@demo.ai', name: 'Demo User' };
    login(guestToken, guestUser);
    navigate('/workspaces/demo/dashboard', { replace: true });
  };

  // Initial letter for the logo badge
  const logoLetter = 'M';

  return (
    <div
      className="flex min-h-screen w-full items-center justify-center px-4"
      style={{
        background: 'radial-gradient(ellipse at bottom, #1a0e00 0%, #0a0a0a 60%, #000000 100%)',
      }}
    >
      {/* Card */}
      <div
        className="w-full max-w-[400px] rounded-2xl p-8"
        style={{
          background: 'rgba(18,18,18,0.92)',
          border: '1px solid rgba(255,255,255,0.07)',
          boxShadow: '0 24px 80px rgba(0,0,0,0.6)',
        }}
      >
        {/* Top row: text + logo badge */}
        <div className="flex items-start justify-between mb-1">
          <p
            className="text-[10px] font-bold uppercase tracking-[0.22em]"
            style={{ color: 'rgba(255,255,255,0.4)' }}
          >
            {isLogin ? 'Welcome back' : 'Get started'}
          </p>
          <div
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-sm font-black"
            style={{
              background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
              border: '1px solid rgba(255,255,255,0.12)',
              color: '#ffffff',
              boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
            }}
          >
            {logoLetter}
          </div>
        </div>

        <h1 className="mt-1 mb-6 text-[1.55rem] font-semibold leading-tight text-white">
          {isLogin ? 'Continue with email.' : 'Create your account.'}
        </h1>

        {/* Error banner */}
        {error && (
          <div
            className="mb-4 rounded-xl px-4 py-3 text-sm"
            style={{
              background: 'rgba(248,81,73,0.1)',
              border: '1px solid rgba(248,81,73,0.25)',
              color: '#f85149',
            }}
          >
            {error}
          </div>
        )}

        <form className="space-y-3" onSubmit={handleSubmit}>
          {/* Name field — register only */}
          {!isLogin && (
            <div>
              <label
                className="mb-1.5 block text-xs font-medium"
                style={{ color: 'rgba(255,255,255,0.6)' }}
              >
                Full name
              </label>
              <input
                required
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                className="w-full rounded-xl px-3.5 py-2.5 text-sm text-white outline-none transition-all duration-150"
                style={{
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                }}
                onFocus={(e) => {
                  e.target.style.border = '1px solid rgba(255,255,255,0.25)';
                  e.target.style.background = 'rgba(255,255,255,0.07)';
                }}
                onBlur={(e) => {
                  e.target.style.border = '1px solid rgba(255,255,255,0.1)';
                  e.target.style.background = 'rgba(255,255,255,0.05)';
                }}
              />
            </div>
          )}

          {/* Email */}
          <div>
            <label
              className="mb-1.5 block text-xs font-medium"
              style={{ color: 'rgba(255,255,255,0.6)' }}
            >
              Work email
            </label>
            <input
              required
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="w-full rounded-xl px-3.5 py-2.5 text-sm text-white outline-none transition-all duration-150"
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
              }}
              onFocus={(e) => {
                e.target.style.border = '1px solid rgba(255,255,255,0.25)';
                e.target.style.background = 'rgba(255,255,255,0.07)';
              }}
              onBlur={(e) => {
                e.target.style.border = '1px solid rgba(255,255,255,0.1)';
                e.target.style.background = 'rgba(255,255,255,0.05)';
              }}
            />
          </div>

          {/* Password */}
          <div>
            <label
              className="mb-1.5 block text-xs font-medium"
              style={{ color: 'rgba(255,255,255,0.6)' }}
            >
              Password
            </label>
            <input
              required
              type="password"
              autoComplete={isLogin ? 'current-password' : 'new-password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="w-full rounded-xl px-3.5 py-2.5 text-sm text-white outline-none transition-all duration-150"
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
              }}
              onFocus={(e) => {
                e.target.style.border = '1px solid rgba(255,255,255,0.25)';
                e.target.style.background = 'rgba(255,255,255,0.07)';
              }}
              onBlur={(e) => {
                e.target.style.border = '1px solid rgba(255,255,255,0.1)';
                e.target.style.background = 'rgba(255,255,255,0.05)';
              }}
            />
          </div>

          {/* Info text */}
          <p
            className="rounded-xl px-3.5 py-3 text-[11px] leading-relaxed"
            style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.05)',
              color: 'rgba(255,255,255,0.4)',
            }}
          >
            {isLogin
              ? 'Your workspace, platform connections, and assistant settings resolve automatically after email login.'
              : 'After registration you will be redirected to connect your social media platforms.'}
          </p>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="mt-1 w-full rounded-xl py-2.5 text-sm font-semibold text-black transition-all duration-150 disabled:opacity-50"
            style={{ background: '#ffffff' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.background = '#f0f0f0'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.background = '#ffffff'; }}
          >
            {loading ? 'Processing…' : (isLogin ? 'Log in' : 'Create account')}
          </button>
        </form>

        {/* OR divider */}
        <div className="my-4 flex items-center gap-3">
          <div className="flex-1 h-px" style={{ background: 'rgba(255,255,255,0.07)' }} />
          <span className="text-[10px] font-medium" style={{ color: 'rgba(255,255,255,0.3)' }}>OR</span>
          <div className="flex-1 h-px" style={{ background: 'rgba(255,255,255,0.07)' }} />
        </div>

        {/* Guest / demo button */}
        <button
          type="button"
          onClick={handleGuestMode}
          className="w-full rounded-xl py-2.5 text-xs font-medium transition-all duration-150"
          style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.08)',
            color: 'rgba(255,255,255,0.5)',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.07)';
            (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.75)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.03)';
            (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.5)';
          }}
        >
          Continue as guest <span style={{ color: 'rgba(255,255,255,0.3)' }}>(mock workspace)</span>
        </button>

        {/* Toggle login / register */}
        <p className="mt-5 text-center text-xs" style={{ color: 'rgba(255,255,255,0.35)' }}>
          {isLogin ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={() => { setIsLogin(!isLogin); setError(''); }}
            className="font-semibold transition-colors hover:text-white"
            style={{ color: 'rgba(255,255,255,0.6)' }}
          >
            {isLogin ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  );
}
