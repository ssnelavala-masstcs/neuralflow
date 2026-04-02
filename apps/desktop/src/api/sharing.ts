import { api } from "./client";
import type { Workflow } from "@/types/workflow";

export interface GistExportResult {
  gist_url: string;
  gist_id: string;
}

export interface CommunityTemplate {
  id: string;
  name: string;
  description: string;
  tags: string[];
  gist_url: string;
  thumbnail_url: string | null;
}

export function exportToGist(
  workflowId: string,
  gistToken: string,
  isPublic = false,
): Promise<GistExportResult> {
  return api.post<GistExportResult>("/api/sharing/export-gist", {
    workflow_id: workflowId,
    gist_token: gistToken,
    public: isPublic,
  });
}

export function importFromUrl(url: string, workspaceId: string): Promise<Workflow> {
  return api.post<Workflow>("/api/sharing/import-url", {
    url,
    workspace_id: workspaceId,
  });
}

export function getCommunityTemplates(): Promise<CommunityTemplate[]> {
  return api.get<CommunityTemplate[]>("/api/sharing/community-templates");
}
