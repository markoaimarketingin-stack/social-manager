const STORAGE_KEY = "social_manager_active_workspace_id";

export function getActiveWorkspaceId(): string | null {
  return window.localStorage.getItem(STORAGE_KEY);
}

export function setActiveWorkspaceId(workspaceId: string): void {
  window.localStorage.setItem(STORAGE_KEY, workspaceId);
}
