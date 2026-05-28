import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

interface Connection {
  platform: string;
  account_name: string;
}

export default function ComposePage() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [content, setContent] = useState('');
  const [platforms, setPlatforms] = useState<string[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchConnections();
  }, []);

  const fetchConnections = async () => {
    try {
      const res = await fetch('http://localhost:8088/api/auth/connections', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setConnections(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const togglePlatform = (platform: string) => {
    setPlatforms(prev =>
      prev.includes(platform) ? prev.filter(p => p !== platform) : [...prev, platform]
    );
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (platforms.length === 0) { setError('Select at least one platform'); return; }
    if (!content.trim()) { setError('Content cannot be empty'); return; }

    setLoading(true);
    try {
      const res = await fetch('http://localhost:8088/api/publishing/schedule', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ platforms, content, scheduled_at: null })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to post');

      setMessage('Post submitted! It is being processed in the background.');
      setContent('');
      setPlatforms([]);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const PLATFORM_META: Record<string, { label: string; icon: string; color: string }> = {
    facebook:  { label: 'Facebook',  icon: 'FB', color: 'bg-blue-500' },
    instagram: { label: 'Instagram', icon: 'IG', color: 'bg-gradient-to-br from-purple-500 to-pink-500' },
    linkedin:  { label: 'LinkedIn',  icon: 'IN', color: 'bg-sky-600' },
  };

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-3xl flex-col px-5 py-12 lg:px-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.35em] text-white/35">
            Social Manager
          </p>
          <h1 className="mt-2 text-3xl font-black tracking-tight text-ink">
            Compose post
          </h1>
          <p className="mt-1 text-sm text-white/50">
            Write a message and publish it to your connected platforms.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/connect')}
            className="rounded-full bg-white/10 px-4 py-2 text-sm font-medium text-ink hover:bg-white/15 transition-colors"
          >
            ← Connections
          </button>
          <button
            onClick={logout}
            className="rounded-full border border-white/10 px-4 py-2 text-sm font-medium text-white/50 hover:text-ink hover:border-white/20 transition-colors"
          >
            Sign out
          </button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="mt-6 rounded-2xl border border-red-500/20 bg-red-500/10 px-5 py-3">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}
      {message && (
        <div className="mt-6 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-5 py-3">
          <p className="text-sm text-emerald-400">{message}</p>
        </div>
      )}

      {/* Composer card */}
      <form onSubmit={handleSubmit} className="mt-8 space-y-6">

        {/* Platform selection */}
        <div className="shell-card rounded-3xl p-6">
          <p className="text-sm font-semibold text-ink">Select platforms</p>
          <p className="mt-1 text-xs text-white/40">
            Only connected platforms are shown.{' '}
            {connections.length === 0 && (
              <button type="button" onClick={() => navigate('/connect')} className="text-white/60 underline">
                Connect a platform first
              </button>
            )}
          </p>

          <div className="mt-4 flex flex-wrap gap-3">
            {connections.map(conn => {
              const meta = PLATFORM_META[conn.platform] || { label: conn.platform, icon: '?', color: 'bg-white/20' };
              const selected = platforms.includes(conn.platform);
              return (
                <button
                  key={conn.platform}
                  type="button"
                  onClick={() => togglePlatform(conn.platform)}
                  className={`flex items-center gap-3 rounded-2xl border px-4 py-3 text-sm font-medium transition-all ${
                    selected
                      ? 'border-white/25 bg-white/10 text-ink shadow-[0_0_20px_rgba(255,255,255,0.05)]'
                      : 'border-white/8 bg-white/[0.03] text-white/50 hover:bg-white/[0.06]'
                  }`}
                >
                  <span className={`h-7 w-7 rounded-lg ${meta.color} flex items-center justify-center text-white text-xs font-bold`}>
                    {meta.icon}
                  </span>
                  <span>{meta.label}</span>
                  {selected && (
                    <span className="ml-1 text-emerald-400">✓</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content textarea */}
        <div className="shell-card rounded-3xl p-6">
          <label htmlFor="compose-content" className="text-sm font-semibold text-ink">
            Post content
          </label>
          <textarea
            id="compose-content"
            rows={5}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="What do you want to say?"
            className="mt-3 w-full resize-none rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 text-sm text-ink placeholder-white/25 focus:border-white/20 focus:outline-none"
          />
          <div className="mt-2 flex items-center justify-between text-xs text-white/30">
            <span>{content.length} characters</span>
            <span>{platforms.length} platform{platforms.length !== 1 ? 's' : ''} selected</span>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || connections.length === 0}
            className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-black shadow-[0_4px_20px_rgba(255,255,255,0.08)] hover:bg-white/90 disabled:opacity-40 transition-colors"
          >
            {loading ? 'Posting...' : 'Post now'}
          </button>
        </div>
      </form>
    </div>
  );
}
