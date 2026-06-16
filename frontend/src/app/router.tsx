import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import AuthPage from "../features/auth/AuthPage";
import ConnectPage from "../features/auth/ConnectPage";
import { ProtectedRoute } from "../components/layout/ProtectedRoute";
import { WorkspaceLayout } from "../features/workspace/components/WorkspaceLayout";
import { WorkspaceOverviewPage } from "../features/workspace/pages/WorkspaceOverviewPage";
import { IntelligencePage } from "../features/intelligence/pages/IntelligencePage";
import { AudienceSegmentsPage } from "../features/audience/pages/AudienceSegmentsPage";
import { BrandProfilePage } from "../features/brand/pages/BrandProfilePage";
import { PlanningPage } from "../features/planning/pages/PlanningPage";
import { PublishingPage } from "../features/publishing/pages/PublishingPage";
import { ReviewPage } from "../features/review/pages/ReviewPage";
import { StrategyPage } from "../features/strategy/pages/StrategyPage";
import { useAuth } from "../features/auth/AuthContext";
import { PlatformWorkspacePage } from "../features/platforms/pages/PlatformWorkspacePage";
import { AnalyticsPage } from "../features/intelligence/pages/AnalyticsPage";

function HomeRedirect() {
  const { isAuthenticated, loading, user } = useAuth();
  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center" style={{ background: "#000000" }}>
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-white/20 border-t-blue-400" />
      </div>
    );
  }
  if (!isAuthenticated || !user) return <Navigate replace to="/auth" />;
  return <Navigate replace to={`/workspaces/${user.id}/dashboard`} />;
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth routes */}
        <Route path="/auth" element={<AuthPage />} />

        {/* Connect platforms */}
        <Route path="/connect" element={<ProtectedRoute><ConnectPage /></ProtectedRoute>} />

        {/* Home — redirects based on auth state */}
        <Route path="/" element={<HomeRedirect />} />

        {/* Workspace routes */}
        <Route
          path="/workspaces/:workspaceId"
          element={<ProtectedRoute><WorkspaceLayout /></ProtectedRoute>}
        >
          <Route index element={<Navigate replace to="dashboard" />} />
          <Route path="dashboard" element={<WorkspaceOverviewPage />} />
          <Route path="social-supervisor" element={<WorkspaceOverviewPage />} />
          <Route path="trends" element={<IntelligencePage />} />
          <Route path="competitors" element={<IntelligencePage />} />
          <Route path="segments" element={<AudienceSegmentsPage />} />
          <Route path="positioning" element={<StrategyPage />} />
          <Route path="copywriter" element={<PlanningPage />} />
          <Route path="ab-copy-tester" element={<ReviewPage />} />
          <Route path="community" element={<PublishingPage />} />
          <Route path="execution-history" element={<ReviewPage />} />
          <Route path="brand-profile" element={<BrandProfilePage />} />
          
          {/* Core Task Workspace Routes */}
          <Route path="content-studio" element={<PlanningPage />} />
          <Route path="approval-inbox" element={<ReviewPage />} />
          <Route path="publishing-calendar" element={<PublishingPage />} />
          <Route path="analytics-center" element={<AnalyticsPage />} />
          <Route path="brand-settings" element={<BrandProfilePage />} />
          
          <Route path="audience-segments" element={<AudienceSegmentsPage />} />
          <Route path="intelligence" element={<IntelligencePage />} />
          <Route path="strategy" element={<StrategyPage />} />
          <Route path="planning" element={<PlanningPage />} />
          <Route path="review" element={<ReviewPage />} />
          <Route path="publishing" element={<PublishingPage />} />
          <Route path="platforms/:platformSlug" element={<PlatformWorkspacePage />} />
        </Route>

        <Route path="*" element={<Navigate replace to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}
