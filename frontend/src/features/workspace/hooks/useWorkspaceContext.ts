import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { ApiError, apiGet } from "../../../lib/api/client";
import type {
  BrandProfile,
  BrandStrategy,
  ContentPlan,
  PostDraft,
  WorkspaceActivityEvent,
  WorkspaceActivitySummary,
  WorkflowRun,
  WorkspaceDetail,
} from "../../../lib/api/types/domain";
import { queryKeys } from "../../../lib/query/keys";

export function useWorkspaceContext() {
  const { workspaceId = "" } = useParams();

  const workspaceQuery = useQuery({
    queryKey: queryKeys.workspace(workspaceId),
    queryFn: () => apiGet<WorkspaceDetail>(`/api/v1/workspaces/${workspaceId}`),
    enabled: workspaceId.length > 0,
  });

  const brandProfileQuery = useQuery({
    queryKey: queryKeys.brandProfile(workspaceId),
    queryFn: () => apiGet<BrandProfile>(`/api/v1/workspaces/${workspaceId}/brand-profile`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  const workflowRunsQuery = useQuery({
    queryKey: queryKeys.workflowRuns(workspaceId),
    queryFn: () => apiGet<WorkflowRun[]>(`/api/v1/workspaces/${workspaceId}/workflow-runs`),
    enabled: workspaceId.length > 0,
  });

  const latestStrategyQuery = useQuery({
    queryKey: queryKeys.latestStrategy(workspaceId),
    queryFn: () => apiGet<BrandStrategy>(`/api/v1/workspaces/${workspaceId}/strategies/latest`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  const strategiesQuery = useQuery({
    queryKey: queryKeys.strategies(workspaceId),
    queryFn: () => apiGet<BrandStrategy[]>(`/api/v1/workspaces/${workspaceId}/strategies`),
    enabled: workspaceId.length > 0,
  });

  const latestContentPlanQuery = useQuery({
    queryKey: queryKeys.latestContentPlan(workspaceId),
    queryFn: () => apiGet<ContentPlan>(`/api/v1/workspaces/${workspaceId}/content-plans/latest`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  const contentPlansQuery = useQuery({
    queryKey: queryKeys.contentPlans(workspaceId),
    queryFn: () => apiGet<ContentPlan[]>(`/api/v1/workspaces/${workspaceId}/content-plans`),
    enabled: workspaceId.length > 0,
  });

  const reviewQueueQuery = useQuery({
    queryKey: queryKeys.reviewQueue(workspaceId),
    queryFn: () => apiGet<PostDraft[]>(`/api/v1/workspaces/${workspaceId}/drafts/review-queue`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  const publishingQueueQuery = useQuery({
    queryKey: queryKeys.publishingQueue(workspaceId),
    queryFn: () => apiGet<PostDraft[]>(`/api/v1/workspaces/${workspaceId}/drafts/publishing-queue`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  const activityQuery = useQuery({
    queryKey: queryKeys.activity(workspaceId),
    queryFn: () => apiGet<WorkspaceActivityEvent[]>(`/api/v1/workspaces/${workspaceId}/activity`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  const activitySummaryQuery = useQuery({
    queryKey: queryKeys.activitySummary(workspaceId),
    queryFn: () => apiGet<WorkspaceActivitySummary>(`/api/v1/workspaces/${workspaceId}/activity/summary`),
    enabled: workspaceId.length > 0,
    retry: (_, error) => !(error instanceof ApiError && error.status === 404),
  });

  return {
    workspaceId,
    workspaceQuery,
    brandProfileQuery,
    workflowRunsQuery,
    strategiesQuery,
    latestStrategyQuery,
    contentPlansQuery,
    latestContentPlanQuery,
    reviewQueueQuery,
    publishingQueueQuery,
    activityQuery,
    activitySummaryQuery,
  };
}
