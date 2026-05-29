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
    id: 'linkedin',
    name: 'LinkedIn',
    description: 'Share professional updates and thought leadership',
    requirement: 'Personal profile or Company Page',
    gradient: 'linear-gradient(135deg, #0077b5, #005885)',
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current text-white">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
      </svg>
    ),
  },
  {
    id: 'instagram',
    name: 'Instagram',
    description: 'Publish photos, reels, and stories',
    requirement: 'Instagram Business Account linked to a Facebook Page',
    gradient: 'linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045)',
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current text-white">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
      </svg>
    ),
  },
  {
    id: 'facebook',
    name: 'Facebook Page',
    description: 'Post to your Facebook Business Page',
    requirement: 'Requires a Facebook Page (Business account)',
    gradient: 'linear-gradient(135deg, #1877f2, #0d5bbf)',
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current text-white">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
    ),
  },
  {
    id: 'x',
    name: 'X (Twitter)',
    description: 'Post tweets and threads',
    requirement: 'X Developer App with OAuth 2.0 enabled',
    gradient: 'linear-gradient(135deg, #1a1a1a, #333)',
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current text-white">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    ),
  },
];

export default function ConnectPage() {
  const { token, user, logout } = useAuth();
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [disconnecting, setDisconnecting] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('success') === 'true') {
      setMessage({ type: 'success', text: `✓ Successfully connected ${params.get('connected')}!` });
    } else if (params.get('error')) {
      setMessage({ type: 'error', text: `Connection failed: ${params.get('description') || params.get('error')}` });
    }
    fetchConnections();
  }, [location]);

  const fetchConnections = async () => {
    try {
      const res = await fetch(`${apiBaseUrl}/api/auth/connections`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setConnections(await res.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const isConnected = (platform: string) => connections.some((c) => c.platform === platform);
  const getConnection = (platform: string) => connections.find((c) => c.platform === platform);

  const handleConnect = (platform: string) => {
    window.location.href = `${apiBaseUrl}/api/auth/${platform}/connect?user_id=${token}`;
  };

  const handleDisconnect = async (platform: string) => {
    if (!window.confirm(`Disconnect ${platform}? This will stop posting to this platform.`)) return;
    setDisconnecting(platform);
    try {
      const res = await fetch(`${apiBaseUrl}/api/auth/${platform}/disconnect`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setConnections(connections.filter((c) => c.platform !== platform));
        setMessage({ type: 'success', text: `Disconnected ${platform}` });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setDisconnecting(null);
    }
  };

  const hasAnyConnection = connections.length > 0;

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ background: '#0d1117', color: '#e6edf3', fontFamily: '"Inter", system-ui, sans-serif' }}
    >
      {/* Top bar */}
      <header style={{ borderBottom: '1px solid #21262d', background: '#161b22' }} className="px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className="flex h-8 w-8 items-center justify-center rounded-md text-white text-xs font-bold"
            style={{ background: 'linear-gradient(135deg, #1f6feb, #388bfd)' }}
          >
            SM
          </div>
          <span className="font-semibold text-sm" style={{ color: '#e6edf3' }}>Social Manager</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs mr-2" style={{ color: '#8b949e' }}>{user?.email}</span>
          <button
            onClick={logout}
            className="px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
            style={{ background: '#21262d', color: '#8b949e', border: '1px solid #30363d' }}
            onMouseEnter={(e) => { (e.target as HTMLElement).style.color = '#e6edf3'; }}
            onMouseLeave={(e) => { (e.target as HTMLElement).style.color = '#8b949e'; }}
          >
            Sign out
          </button>
        </div>
      </header>

      <div className="flex-1 flex flex-col items-center justify-start py-10 px-4">
        <div className="w-full max-w-2xl">
          {/* Header */}
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-widest mb-2" style={{ color: '#388bfd' }}>
              Platform Connections
            </p>
            <h1 className="text-2xl font-bold mb-2" style={{ color: '#e6edf3' }}>
              Connect your social accounts
            </h1>
            <p className="text-sm" style={{ color: '#8b949e' }}>
              Link your social media platforms to start publishing content from Social Manager.
            </p>
          </div>

          {/* Status message */}
          {message && (
            <div
              className="mb-6 px-4 py-3 rounded-lg text-sm"
              style={{
                background: message.type === 'success' ? 'rgba(35,134,54,0.15)' : 'rgba(218,54,51,0.15)',
                border: `1px solid ${message.type === 'success' ? 'rgba(35,134,54,0.3)' : 'rgba(218,54,51,0.3)'}`,
                color: message.type === 'success' ? '#3fb950' : '#f85149',
              }}
            >
              {message.text}
            </div>
          )}

          {/* Go to Dashboard button (shown when any platform connected) */}
          {hasAnyConnection && (
            <div
              className="mb-6 px-4 py-4 rounded-lg flex items-center justify-between"
              style={{ background: 'rgba(31,111,235,0.1)', border: '1px solid rgba(31,111,235,0.3)' }}
            >
              <div>
                <p className="font-semibold text-sm" style={{ color: '#58a6ff' }}>
                  🎉 {connections.length} platform{connections.length > 1 ? 's' : ''} connected!
                </p>
                <p className="text-xs mt-0.5" style={{ color: '#8b949e' }}>
                  You're ready to manage and post to your social accounts.
                </p>
              </div>
              <button
                onClick={() => navigate(`/workspaces/${user?.id}/dashboard`)}
                className="px-4 py-2 rounded-md text-sm font-semibold transition-colors flex items-center gap-2 ml-4 shrink-0"
                style={{ background: '#1f6feb', color: '#fff' }}
                onMouseEnter={(e) => { (e.target as HTMLElement).style.background = '#388bfd'; }}
                onMouseLeave={(e) => { (e.target as HTMLElement).style.background = '#1f6feb'; }}
              >
                Go to Dashboard
                <svg viewBox="0 0 20 20" className="h-4 w-4 fill-current" >
                  <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd"/>
                </svg>
              </button>
            </div>
          )}

          {/* Platform cards */}
          <div className="space-y-3">
            {PLATFORMS.map((platform) => {
              const connected = isConnected(platform.id);
              const conn = getConnection(platform.id);
              const isDisconnecting = disconnecting === platform.id;

              return (
                <div
                  key={platform.id}
                  className="rounded-lg p-4 flex items-center justify-between transition-colors"
                  style={{
                    background: '#161b22',
                    border: connected ? '1px solid rgba(35,134,54,0.35)' : '1px solid #21262d',
                  }}
                >
                  <div className="flex items-center gap-4">
                    {/* Platform icon */}
                    <div
                      className="flex h-10 w-10 items-center justify-center rounded-lg shrink-0"
                      style={{ background: platform.gradient }}
                    >
                      {platform.icon}
                    </div>

                    {/* Platform info */}
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-sm" style={{ color: '#e6edf3' }}>
                          {platform.name}
                        </h3>
                        {connected && (
                          <span
                            className="px-2 py-0.5 rounded-full text-xs font-medium"
                            style={{ background: 'rgba(35,134,54,0.2)', color: '#3fb950', border: '1px solid rgba(35,134,54,0.3)' }}
                          >
                            Connected
                          </span>
                        )}
                      </div>
                      {connected && conn ? (
                        <p className="text-xs mt-0.5" style={{ color: '#3fb950' }}>
                          @{conn.account_name || conn.account_id}
                        </p>
                      ) : (
                        <p className="text-xs mt-0.5" style={{ color: '#6e7681' }}>
                          {platform.requirement}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Action button */}
                  <div className="shrink-0 ml-4">
                    {connected ? (
                      <button
                        onClick={() => handleDisconnect(platform.id)}
                        disabled={isDisconnecting}
                        className="px-3 py-1.5 rounded-md text-xs font-medium transition-colors disabled:opacity-50"
                        style={{
                          background: 'rgba(218,54,51,0.1)',
                          color: '#f85149',
                          border: '1px solid rgba(218,54,51,0.25)',
                        }}
                      >
                        {isDisconnecting ? 'Disconnecting…' : 'Disconnect'}
                      </button>
                    ) : (
                      <button
                        onClick={() => handleConnect(platform.id)}
                        className="px-3 py-1.5 rounded-md text-xs font-semibold transition-colors"
                        style={{ background: '#238636', color: '#fff', border: '1px solid rgba(35,134,54,0.4)' }}
                        onMouseEnter={(e) => { (e.target as HTMLElement).style.background = '#2ea043'; }}
                        onMouseLeave={(e) => { (e.target as HTMLElement).style.background = '#238636'; }}
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
            <div className="mt-6 flex justify-center">
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-white/20 border-t-blue-400" />
            </div>
          )}

          {/* Skip link */}
          {!hasAnyConnection && (
            <div className="mt-6 text-center">
              <button
                onClick={() => navigate(`/workspaces/${user?.id}/dashboard`)}
                className="text-sm transition-colors"
                style={{ color: '#6e7681' }}
                onMouseEnter={(e) => { (e.target as HTMLElement).style.color = '#8b949e'; }}
                onMouseLeave={(e) => { (e.target as HTMLElement).style.color = '#6e7681'; }}
              >
                Skip for now — go to dashboard →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
