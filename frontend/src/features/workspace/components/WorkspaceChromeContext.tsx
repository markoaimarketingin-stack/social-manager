import type { PropsWithChildren } from "react";
import { createContext, useContext } from "react";

type WorkspaceChromeContextValue = {
  assistantCollapsed: boolean;
  openAssistant: () => void;
  toggleAssistant: () => void;
  openKnowledgeBase: () => void;
  openTrainModal: () => void;
  openNotifications: () => void;
  pushToast: (message: string) => void;
};

const WorkspaceChromeContext = createContext<WorkspaceChromeContextValue | null>(null);

export function WorkspaceChromeProvider({
  value,
  children,
}: PropsWithChildren<{ value: WorkspaceChromeContextValue }>) {
  return <WorkspaceChromeContext.Provider value={value}>{children}</WorkspaceChromeContext.Provider>;
}

export function useWorkspaceChrome() {
  const context = useContext(WorkspaceChromeContext);
  if (!context) {
    throw new Error("useWorkspaceChrome must be used inside WorkspaceChromeProvider");
  }
  return context;
}
