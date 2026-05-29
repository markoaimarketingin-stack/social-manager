import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { apiBaseUrl } from '../../lib/api/client';

interface Connection {
  platform: string;
  account_name: string;
  account_id: string;
  connected: boolean;
  connected_at: string;
}

const PLATFORMS = [
  {
    id: 'facebook',
    name: 'Facebook Page',
    description: 'Post to your Facebook Business Page',
    requirement: 'Requires a Facebook Page (Business account)',
    color: 'bg-blue-500',
    icon: 'FB',
  },
  {
    id: 'instagram',
    name: 'Instagram',
    description: 'Publish photos and reels to Instagram',
    requirement: 'Requires an Instagram Business Account linked to a Facebook Page',
    color: 'bg-gradient-to-br from-purple-500 to-pink-500',
    icon: 'IG',
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    description: 'Share updates on your LinkedIn profile',
    requirement: 'Personal profile or Company Page',
    color: 'bg-sky-600',
    icon: 'IN',
  },
];

export default function ConnectPage() {
  const { token, user, logout } = useAuth();
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('success') === 'true') {
      setMessage(`Successfully connected ${params.get('connected')}!`);
    }
    fetchConnections();
  }, [location]);

  const fetchConnections = async () => {
    try {
      const res = await fetch(`${apiBaseUrl}/api/auth/connections`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setConnections(await res.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const isConnected = (platform: string) => connections.some(c => c.platform === platform);
  const getAccountName = (platform: string) => connections.find(c => c.platform === platform)?.account_name || '';

  const handleConnect = (platform: string) => {
    window.location.href = `${apiBaseUrl}/api/auth/${platform}/connect?user_id=${token}`;
  };

  const handleDisconnect = async (platform: string) => {
    if (!confirm(`Disconnect ${platform}?`)) return;
    try {
      const res = await fetch(`${apiBaseUrl}/api/auth/${platform}/disconnect`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setConnections(connections.filter(c => c.platform !== platform));
        setMessage(`Disconnected ${platform}`);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-4xl flex-col px-5 py-12 lg:px-8">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.35em] text-white/35">
            Social Manager
          </p>
          <h1 className="mt-2 text-3xl font-black tracking-tight text-ink">
            Connect platforms
          </h1>
          <p className="mt-1 text-sm text-white/50">
            Link your social media accounts to publish content. Logged in as{' '}
            <span className="text-white/80">{user?.email}</span>
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/workspaces/demo-workspace/dashboard')}
            className="rounded-full border border-white/10 px-4 py-2 text-sm font-medium text-white/50 hover:text-ink hover:border-white/20 transition-colors"
          >
            Skip for now →
          </button>
          <button
            onClick={() => navigate('/compose')}
            className="rounded-full bg-white/10 px-4 py-2 text-sm font-medium text-ink hover:bg-white/15 transition-colors"
          >
            Composer →
          </button>
          <button
            onClick={logout}
            className="rounded-full border border-white/10 px-4 py-2 text-sm font-medium text-white/50 hover:text-ink hover:border-white/20 transition-colors"
          >
            Sign out
          </button>
        </div>
      </div>

      {message && (
        <div className="mt-6 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-5 py-3">
          <p className="text-sm text-emerald-400">{message}</p>
        </div>
      )}

      {/* Platform cards */}
      <div className="mt-8 space-y-4">
        {PLATFORMS.map((platform) => {
          const connected = isConnected(platform.id);
          const accountName = getAccountName(platform.id);

          return (
            <div
              key={platform.id}
              className="shell-card rounded-3xl p-6 flex items-center justify-between"
            >
              <div className="flex items-center gap-5">
                <div className={`h-12 w-12 rounded-2xl ${platform.color} flex items-center justify-center text-white font-bold text-lg shadow-lg`}>
                  {platform.icon}
                </div>
                <div>
                  <h3 className="text-base font-semibold text-ink">{platform.name}</h3>
                  {connected ? (
                    <p className="mt-0.5 text-sm text-emerald-400">
                      Connected as <span className="font-medium">{accountName}</span>
                    </p>
                  ) : (
                    <p className="mt-0.5 text-sm text-white/40">{platform.requirement}</p>
                  )}
                </div>
              </div>

              <div>
                {connected ? (
                  <button
                    onClick={() => handleDisconnect(platform.id)}
                    className="rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-400 hover:bg-red-500/20 transition-colors"
                  >
                    Disconnect
                  </button>
                ) : (
                  <button
                    onClick={() => handleConnect(platform.id)}
                    className="rounded-full bg-white px-5 py-2 text-sm font-semibold text-black hover:bg-white/90 transition-colors shadow-[0_4px_20px_rgba(255,255,255,0.08)]"
                  >
                    Connect
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {loading && (
        <div className="mt-8 flex justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-white/20 border-t-white/70"></div>
        </div>
      )}
    </div>
  );
}
