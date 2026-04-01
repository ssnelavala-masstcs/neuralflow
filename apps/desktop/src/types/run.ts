export type RunStatus = "queued" | "running" | "paused" | "complete" | "error" | "cancelled";
export type NodeRunStatus = "pending" | "running" | "complete" | "error" | "skipped";

export interface Run {
  id: string;
  workflow_id: string;
  status: RunStatus;
  trigger_type: string;
  input_data: Record<string, unknown> | null;
  output_data: Record<string, unknown> | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  total_cost_usd: number;
  total_input_tokens: number;
  total_output_tokens: number;
}

export interface NodeRunRecord {
  id: string;
  run_id: string;
  node_id: string;
  node_type: string;
  node_name: string;
  status: NodeRunStatus;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  input_data: unknown;
  output_data: unknown;
  error_message: string | null;
  cost_usd: number;
  input_tokens: number;
  output_tokens: number;
}

export type StreamEventType =
  | "run_started"
  | "run_completed"
  | "run_failed"
  | "node_started"
  | "node_completed"
  | "node_failed"
  | "llm_chunk"
  | "tool_call"
  | "tool_result"
  | "log"
  | "done"
  | "error"
  | "cancelled";

export interface StreamEvent {
  type: StreamEventType;
  run_id: string;
  node_id?: string;
  node_name?: string;
  node_type?: string;
  chunk?: string;
  output?: unknown;
  error?: string;
  message?: string;
  tool_name?: string;
  input?: unknown;
  cost_usd?: number;
  level?: "info" | "warn" | "error";
}
