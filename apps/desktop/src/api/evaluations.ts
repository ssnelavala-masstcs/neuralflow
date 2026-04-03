import { api } from "./client";
import type { Evaluation } from "@/types/evaluation";

export const evaluationsApi = {
  list: () => api.get<Evaluation[]>("/api/evaluations"),
  get: (id: string) => api.get<Evaluation>(`/api/evaluations/${id}`),
  create: (workflowAId: string, workflowBId: string, testInput: Record<string, unknown>, metric: string) =>
    api.post<Evaluation>("/api/evaluations", {
      workflow_a_id: workflowAId,
      workflow_b_id: workflowBId,
      test_input: testInput,
      metric,
    }),
  delete: (id: string) => api.delete<void>(`/api/evaluations/${id}`),
};
