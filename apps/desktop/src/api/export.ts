import { api } from "./client";

export async function exportCrewAI(workflowId: string): Promise<{ code: string; filename: string }> {
  return api.get(`/api/export/${workflowId}/crewai`);
}

export async function exportLangGraph(workflowId: string): Promise<{ code: string; filename: string }> {
  return api.get(`/api/export/${workflowId}/langgraph`);
}

export interface Snapshot {
  id: string;
  workflow_id: string;
  name: string | null;
  canvas_data: object;
  execution_mode: string;
  created_at: string;
}

export async function createSnapshot(workflowId: string, name?: string): Promise<Snapshot> {
  return api.post("/api/snapshots", { workflow_id: workflowId, name });
}

export async function listSnapshots(workflowId: string): Promise<Snapshot[]> {
  return api.get(`/api/snapshots?workflow_id=${encodeURIComponent(workflowId)}`);
}

export async function rollbackSnapshot(snapshotId: string): Promise<void> {
  return api.post(`/api/snapshots/${snapshotId}/rollback`);
}

export async function renameSnapshot(snapshotId: string, name: string): Promise<Snapshot> {
  return api.patch(`/api/snapshots/${snapshotId}/name`, { name });
}

export async function deleteSnapshot(snapshotId: string): Promise<void> {
  return api.delete(`/api/snapshots/${snapshotId}`);
}

export function downloadPythonFile(code: string, filename: string): void {
  const blob = new Blob([code], { type: "text/x-python" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
