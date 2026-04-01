import { api } from "./client";
import type { CanvasData, Workflow, Workspace } from "@/types/workflow";

export const workflowsApi = {
  listWorkspaces: () => api.get<Workspace[]>("/api/workspaces"),
  createWorkspace: (name: string, description?: string) =>
    api.post<Workspace>("/api/workspaces", { name, description }),

  list: (workspaceId: string) =>
    api.get<Workflow[]>(`/api/workspaces/${workspaceId}/workflows`),
  create: (workspaceId: string, name: string, description?: string) =>
    api.post<Workflow>(`/api/workspaces/${workspaceId}/workflows`, {
      workspace_id: workspaceId,
      name,
      description,
    }),
  get: (id: string) => api.get<Workflow>(`/api/workflows/${id}`),
  update: (id: string, data: Partial<{ name: string; description: string; canvas_data: CanvasData; execution_mode: string; tags: string[] }>) =>
    api.patch<Workflow>(`/api/workflows/${id}`, data),
  delete: (id: string) => api.delete<void>(`/api/workflows/${id}`),
  duplicate: (id: string) => api.post<Workflow>(`/api/workflows/${id}/duplicate`),
};
