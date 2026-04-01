import { api } from "./client";
import type { NodeRunRecord, Run, StreamEvent } from "@/types/run";

export const runsApi = {
  start: (workflowId: string, inputData?: Record<string, unknown>) =>
    api.post<Run>("/api/runs", { workflow_id: workflowId, input_data: inputData }),
  get: (id: string) => api.get<Run>(`/api/runs/${id}`),
  list: (workflowId?: string) =>
    api.get<Run[]>(`/api/runs${workflowId ? `?workflow_id=${workflowId}` : ""}`),
  cancel: (id: string) => api.post<{ ok: boolean }>(`/api/runs/${id}/cancel`),
  nodes: (runId: string) => api.get<NodeRunRecord[]>(`/api/runs/${runId}/nodes`),

  stream: (runId: string, onEvent: (e: StreamEvent) => void, onDone: () => void): () => void => {
    const es = api.stream(`/api/runs/${runId}/stream`);
    es.onmessage = (msg) => {
      const event: StreamEvent = JSON.parse(msg.data);
      onEvent(event);
      if (event.type === "done" || event.type === "error") {
        es.close();
        onDone();
      }
    };
    es.onerror = () => {
      es.close();
      onDone();
    };
    return () => es.close();
  },
};
