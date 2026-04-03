export interface EvaluationResultItem {
  run_id: string | null;
  cost_usd: number;
  total_tokens: number;
  duration_ms: number | null;
  output: unknown;
  status: string;
}

export interface Evaluation {
  id: string;
  workflow_a_id: string;
  workflow_b_id: string;
  test_input: Record<string, unknown>;
  metric: string;
  status: "pending" | "running" | "complete" | "error";
  result_a: EvaluationResultItem | null;
  result_b: EvaluationResultItem | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}
