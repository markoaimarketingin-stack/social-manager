import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { IntelligencePage } from "../features/intelligence/pages/IntelligencePage";
import { AudienceSegmentsPage } from "../features/audience/pages/AudienceSegmentsPage";
import { BrandProfilePage } from "../features/brand/pages/BrandProfilePage";
import { OnboardingPage } from "../features/onboarding/pages/OnboardingPage";
import { PlanningPage } from "../features/planning/pages/PlanningPage";
import { PublishingPage } from "../features/publishing/pages/PublishingPage";
import { ReviewPage } from "../features/review/pages/ReviewPage";
import { StrategyPage } from "../features/strategy/pages/StrategyPage";
import { WorkspaceLayout } from "../features/workspace/components/WorkspaceLayout";
import { WorkspaceOverviewPage } from "../features/workspace/pages/WorkspaceOverviewPage";
import { isDemoModeEnabled } from "../lib/api/mock";

export function AppRouter() {
  const homeElement = isDemoModeEnabled() ? (
    <Navigate replace to="/workspaces/demo-workspace" />
  ) : (
    <OnboardingPage />
  );

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={homeElement} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/workspaces/:workspaceId" element={<WorkspaceLayout />}>
          <Route index element={<WorkspaceOverviewPage />} />
          <Route path="brand-profile" element={<BrandProfilePage />} />
          <Route path="audience-segments" element={<AudienceSegmentsPage />} />
          <Route path="intelligence" element={<IntelligencePage />} />
          <Route path="strategy" element={<StrategyPage />} />
          <Route path="planning" element={<PlanningPage />} />
          <Route path="review" element={<ReviewPage />} />
          <Route path="publishing" element={<PublishingPage />} />
        </Route>
        <Route path="*" element={<Navigate replace to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}
