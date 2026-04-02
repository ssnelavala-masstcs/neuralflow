import { api } from "./client";

export interface ToolCallDetail {
  id: string;
  name: string;
  source: string;
  input: Record<string, unknown>;
  output: unknown;
  error: string | null;
  latency_ms: number | null;
}

export interface LlmCallDetail {
  id: string;
  model: string;
  call_index: number;
  messages: Array<{ role: string; content: string }>;
  response_content: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  latency_ms: number | null;
  finish_reason: string | null;
  tool_calls: ToolCallDetail[];
}

export interface RunStep {
  id: string;
  node_id: string;
  node_name: string;
  node_type: string;
  status: "running" | "complete" | "error";
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  cost_usd: number;
  input_tokens: number;
  output_tokens: number;
  output_data: Record<string, unknown> | null;
  error_message: string | null;
  llm_call_count: number;
  tool_call_count: number;
  llm_calls: LlmCallDetail[];
}

export const debugApi = {
  getRunSteps: (runId: string) =>
    api.get<RunStep[]>(`/api/runs/${runId}/steps`),

  rerunFromStep: (runId: string, fromNodeRunId: string) =>
    api.post<{ new_run_id: string }>(`/api/runs/${runId}/rerun-from/${fromNodeRunId}`),

  resumeRun: (runId: string, input: { message: string }) =>
    api.post<{ ok: boolean }>(`/api/runs/${runId}/resume`, input),
};
