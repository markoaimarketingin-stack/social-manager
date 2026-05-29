import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../features/auth/AuthContext';

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div
        className="flex h-screen w-full items-center justify-center"
        style={{ background: "#0d1117" }}
      >
        <div className="text-center">
          <div
            className="mx-auto h-8 w-8 animate-spin rounded-full border-2"
            style={{ borderColor: "#21262d", borderTopColor: "#388bfd" }}
          />
          <p className="mt-3 text-xs" style={{ color: "#6e7681", fontFamily: '"Inter", system-ui, sans-serif' }}>
            Loading…
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
