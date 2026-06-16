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
    <main className="relative min-h-screen overflow-hidden bg-[#050505] text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.14),_transparent_35%),radial-gradient(circle_at_bottom_right,_rgba(255,196,86,0.16),_transparent_32%)]" />
      <div className="absolute inset-x-0 top-0 h-72 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),transparent)]" />

      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl items-center px-5 py-12 lg:px-8">
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
                  className="rounded-3xl border border-white/8 bg-[#000000] p-5"
                >
                  <p className="text-sm font-semibold">{card.title}</p>
                  <p className="mt-3 text-sm leading-6 text-white/58">{card.detail}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-[2rem] border border-white/10 bg-[#0d0d0d]/90 p-8 text-white shadow-panel backdrop-blur">
            <h2 className="text-2xl font-semibold">Workspace setup</h2>
            <p className="mt-2 text-sm leading-7 text-white/60">
              Start with the workspace and owner. The app will guide you into strategy, planning, and
              review views after setup.
            </p>

            <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white/78">Workspace name</span>
                <input
                  required
                  value={formState.workspaceName}
                  onChange={(event) =>
                    setFormState((current) => ({ ...current, workspaceName: event.target.value }))
                  }
                  className="w-full rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white placeholder-white/28 outline-none transition focus:border-white/30 focus:bg-white/[0.06]"
                  placeholder="Acme Social"
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white/78">Owner name</span>
                <input
                  required
                  value={formState.ownerName}
                  onChange={(event) =>
                    setFormState((current) => ({ ...current, ownerName: event.target.value }))
                  }
                  className="w-full rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white placeholder-white/28 outline-none transition focus:border-white/30 focus:bg-white/[0.06]"
                  placeholder="Jordan Rivera"
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-white/78">Owner email</span>
                <input
                  required
                  type="email"
                  value={formState.ownerEmail}
                  onChange={(event) =>
                    setFormState((current) => ({ ...current, ownerEmail: event.target.value }))
                  }
                  className="w-full rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white placeholder-white/28 outline-none transition focus:border-white/30 focus:bg-white/[0.06]"
                  placeholder="jordan@acme.co"
                />
              </label>

              {errorMessage ? <p className="text-sm text-red-400">{errorMessage}</p> : null}

              <button
                type="submit"
                disabled={createWorkspaceMutation.isPending}
                className="w-full rounded-[1rem] bg-white py-3 text-sm font-semibold text-black transition hover:-translate-y-0.5 hover:shadow-[0_18px_36px_rgba(255,255,255,0.18)] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {createWorkspaceMutation.isPending ? "Creating workspace..." : "Create workspace"}
              </button>
            </form>
          </section>
        </div>
      </div>
    </main>
  );
}
