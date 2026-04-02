const BASE = "http://127.0.0.1:7411";

export interface CostAnalytics {
  per_day: Array<{
    date: string;
    cost_usd: number;
    input_tokens: number;
    output_tokens: number;
    run_count: number;
  }>;
  per_model: Array<{
    model: string;
    cost_usd: number;
    input_tokens: number;
    output_tokens: number;
    call_count: number;
  }>;
  per_workflow: Array<{
    workflow_id: string;
    cost_usd: number;
    run_count: number;
  }>;
  totals: {
    cost_usd: number;
    input_tokens: number;
    output_tokens: number;
    run_count: number;
  };
  period_days: number;
}

export async function getCostAnalytics(
  workflowId?: string,
  days?: number
): Promise<CostAnalytics> {
  const params = new URLSearchParams();
  if (days !== undefined) params.set("days", String(days));
  if (workflowId) params.set("workflow_id", workflowId);
  const query = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${BASE}/api/analytics/costs${query}`);
  if (!res.ok) throw new Error(`Analytics fetch failed: ${res.status}`);
  return res.json() as Promise<CostAnalytics>;
}

export function exportCostsAsCSV(data: CostAnalytics): void {
  const header = "date,cost_usd,input_tokens,output_tokens,run_count";
  const rows = data.per_day.map(
    (r) => `${r.date},${r.cost_usd},${r.input_tokens},${r.output_tokens},${r.run_count}`
  );
  const csv = [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `neuralflow-costs-${data.period_days}d.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
