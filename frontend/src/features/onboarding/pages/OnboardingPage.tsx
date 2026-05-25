import { useMutation } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { apiPost } from "../../../lib/api/client";
import type { Workspace } from "../../../lib/api/types/domain";
import type { CreateWorkspaceRequest } from "../../../lib/api/types/requests";
import {
  getActiveWorkspaceId,
  setActiveWorkspaceId,
} from "../../workspace/hooks/activeWorkspace";

const initialFormState = {
  workspaceName: "",
  ownerName: "",
  ownerEmail: "",
};

export function OnboardingPage() {
  const navigate = useNavigate();
  const [formState, setFormState] = useState(initialFormState);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const activeWorkspaceId = getActiveWorkspaceId();
    if (activeWorkspaceId) {
      navigate(`/workspaces/${activeWorkspaceId}`, { replace: true });
    }
  }, [navigate]);

  const createWorkspaceMutation = useMutation({
    mutationFn: (payload: CreateWorkspaceRequest) =>
      apiPost<Workspace, CreateWorkspaceRequest>("/api/v1/workspaces", payload),
    onSuccess: (workspace) => {
      setActiveWorkspaceId(workspace.id);
      navigate(`/workspaces/${workspace.id}`);
    },
    onError: (error) => {
      setErrorMessage(error instanceof Error ? error.message : "Workspace creation failed");
    },
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage(null);
    createWorkspaceMutation.mutate({
      name: formState.workspaceName,
      owner: {
        full_name: formState.ownerName,
        email: formState.ownerEmail,
      },
    });
  };

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl items-center px-5 py-12 lg:px-8">
      <div className="grid w-full gap-8 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="shell-surface rounded-[2rem] p-8 shadow-panel">
          <p className="text-[10px] font-semibold uppercase tracking-[0.35em] text-white/35">
            Marko AI
          </p>
          <h1 className="mt-4 text-4xl font-black tracking-tight text-ink md:text-6xl">
            Rebuild the social operating layer without losing the product atmosphere
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-8 text-white/58">
            The legacy product felt like one command center. This onboarding flow preserves that
            recognizable first step while anchoring everything in real workspaces, typed contracts,
            and modular routes.
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {[
              {
                title: "Brand system",
                detail: "Capture voice, mission, and positioning inputs before strategy generation.",
              },
              {
                title: "Audience map",
                detail: "Define segments and platforms explicitly instead of hiding them in a mutable blob.",
              },
              {
                title: "Workflow tracking",
                detail: "Keep every strategy run visible, typed, and workspace-scoped from day one.",
              },
            ].map((card) => (
              <div
                key={card.title}
                className="rounded-3xl border border-white/8 bg-white/[0.04] p-5"
              >
                <p className="text-sm font-semibold">{card.title}</p>
                <p className="mt-3 text-sm leading-6 text-white/58">{card.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-[2rem] border border-black/10 bg-white p-8 text-black shadow-panel">
          <h2 className="text-2xl font-semibold">Workspace setup</h2>
          <p className="mt-2 text-sm leading-7 text-black/65">
            Start with the workspace and owner. The app will guide you into strategy, planning, and
            review views after setup.
          </p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <label className="block">
              <span className="mb-2 block text-sm font-medium">Workspace name</span>
              <input
                required
                value={formState.workspaceName}
                onChange={(event) =>
                  setFormState((current) => ({ ...current, workspaceName: event.target.value }))
                }
                className="w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                placeholder="Acme Social"
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium">Owner name</span>
              <input
                required
                value={formState.ownerName}
                onChange={(event) =>
                  setFormState((current) => ({ ...current, ownerName: event.target.value }))
                }
                className="w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                placeholder="Jordan Rivera"
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium">Owner email</span>
              <input
                required
                type="email"
                value={formState.ownerEmail}
                onChange={(event) =>
                  setFormState((current) => ({ ...current, ownerEmail: event.target.value }))
                }
                className="w-full rounded-2xl border border-black/10 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]"
                placeholder="jordan@acme.co"
              />
            </label>

            {errorMessage ? <p className="text-sm text-red-600">{errorMessage}</p> : null}

            <button
              type="submit"
              disabled={createWorkspaceMutation.isPending}
              className="rounded-full bg-black px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_50px_rgba(0,0,0,0.18)] disabled:opacity-60"
            >
              {createWorkspaceMutation.isPending ? "Creating workspace..." : "Create workspace"}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
