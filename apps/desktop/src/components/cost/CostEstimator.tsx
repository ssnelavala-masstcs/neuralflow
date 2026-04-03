import { useState, useEffect } from "react";
import { DollarSign, Loader2 } from "lucide-react";
import { api } from "@/api/client";
import type { Node, Edge } from "@xyflow/react";

interface CostEstimate {
  estimated_input_tokens: number;
  estimated_output_tokens: number;
  estimated_cost_usd: number;
  low_estimate_usd: number;
  high_estimate_usd: number;
  per_node: Array<{
    node_id: string;
    node_name: string;
    model: string;
    estimated_input_tokens: number;
    estimated_output_tokens: number;
    estimated_cost_usd: number;
  }>;
}

interface CostEstimatorProps {
  nodes: Node[];
  edges: Edge[];
}

export function CostEstimator({ nodes, edges }: CostEstimatorProps) {
  const [estimate, setEstimate] = useState<CostEstimate | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (nodes.length === 0) {
      setEstimate(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    api
      .post<CostEstimate>("/api/analytics/estimate", { nodes, edges })
      .then((data) => {
        if (!cancelled) setEstimate(data);
      })
      .catch(() => { /* ignore */ })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [nodes, edges]);

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Loader2 className="h-3 w-3 animate-spin" />
        Estimating cost…
      </div>
    );
  }

  if (!estimate || estimate.estimated_cost_usd === 0) return null;

  return (
    <div className="rounded-md border border-border bg-card p-3 space-y-2">
      <div className="flex items-center gap-2">
        <DollarSign className="h-4 w-4 text-green-500" />
        <span className="text-xs font-semibold">Estimated Cost</span>
      </div>
      <div className="text-sm font-bold text-green-500">
        ${estimate.estimated_cost_usd.toFixed(4)}
        <span className="text-[10px] text-muted-foreground font-normal ml-1">
          (${estimate.low_estimate_usd.toFixed(4)} – ${estimate.high_estimate_usd.toFixed(4)})
        </span>
      </div>
      <div className="text-[10px] text-muted-foreground space-y-0.5">
        <div>Input: {estimate.estimated_input_tokens.toLocaleString()} tokens</div>
        <div>Output: {estimate.estimated_output_tokens.toLocaleString()} tokens</div>
      </div>
      {estimate.per_node.length > 0 && (
        <details className="text-[10px]">
          <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
            Per-node breakdown ({estimate.per_node.length})
          </summary>
          <div className="mt-1 space-y-1">
            {estimate.per_node.map((n) => (
              <div key={n.node_id} className="flex items-center justify-between text-muted-foreground">
                <span className="truncate">{n.node_name}</span>
                <span className="shrink-0 font-mono">${n.estimated_cost_usd.toFixed(6)}</span>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
