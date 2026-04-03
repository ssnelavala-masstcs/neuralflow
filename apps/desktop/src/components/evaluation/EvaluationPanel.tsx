import { useEffect, useState } from "react";
import {
  ArrowRightLeft,
  Clock,
  Coins,
  Loader2,
  Play,
  Trash2,
  Workflow,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { evaluationsApi } from "@/api/evaluations";
import { workflowsApi } from "@/api/workflows";
import type { Evaluation, EvaluationResultItem } from "@/types/evaluation";
import type { Workflow as WorkflowType } from "@/types/workflow";

type Metric = "cost" | "tokens" | "duration";

export function EvaluationPanel() {
  const [workflows, setWorkflows] = useState<WorkflowType[]>([]);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [workflowAId, setWorkflowAId] = useState("");
  const [workflowBId, setWorkflowBId] = useState("");
  const [testInput, setTestInput] = useState("{}");
  const [metric, setMetric] = useState<Metric>("cost");
  const [running, setRunning] = useState(false);
  const [selectedEval, setSelectedEval] = useState<Evaluation | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    const hasRunning = evaluations.some((e) => e.status === "running" || e.status === "pending");
    if (!hasRunning) return;
    const interval = setInterval(() => {
      loadEvaluations();
    }, 2000);
    return () => clearInterval(interval);
  }, [evaluations]);

  const loadData = async () => {
    try {
      const [evals, workspaces] = await Promise.all([
        evaluationsApi.list(),
        workflowsApi.listWorkspaces(),
      ]);
      setEvaluations(evals);
      const allWfs: WorkflowType[] = [];
      for (const ws of workspaces) {
        const wfs = await workflowsApi.list(ws.id);
        allWfs.push(...wfs);
      }
      setWorkflows(allWfs);
      if (allWfs.length >= 2) {
        setWorkflowAId(allWfs[0].id);
        setWorkflowBId(allWfs[1].id);
      }
    } catch {
      // ignore
    }
  };

  const loadEvaluations = async () => {
    try {
      setEvaluations(await evaluationsApi.list());
    } catch {
      // ignore
    }
  };

  const handleRun = async () => {
    if (!workflowAId || !workflowBId) return;
    let input: Record<string, unknown>;
    try {
      input = JSON.parse(testInput);
    } catch {
      input = {};
    }
    setRunning(true);
    try {
      const ev = await evaluationsApi.create(workflowAId, workflowBId, input, metric);
      setEvaluations((prev) => [ev, ...prev]);
      setSelectedEval(ev);
    } catch {
      // ignore
    } finally {
      setRunning(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await evaluationsApi.delete(id);
      setEvaluations((prev) => prev.filter((e) => e.id !== id));
      if (selectedEval?.id === id) setSelectedEval(null);
    } catch {
      // ignore
    }
  };

  const wfName = (id: string) => workflows.find((w) => w.id === id)?.name ?? id.slice(0, 8);

  const statusColor = (status: string) => {
    switch (status) {
      case "complete": return "text-green-500";
      case "error": return "text-red-500";
      case "running": return "text-blue-500";
      default: return "text-muted-foreground";
    }
  };

  const formatMs = (ms: number | null) => {
    if (ms == null) return "—";
    return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`;
  };

  const winner = (a: EvaluationResultItem | null, b: EvaluationResultItem | null) => {
    if (!a || !b || a.status !== "complete" || b.status !== "complete") return null;
    switch (metric) {
      case "cost": return a.cost_usd < b.cost_usd ? "a" : a.cost_usd > b.cost_usd ? "b" : "tie";
      case "tokens": return a.total_tokens < b.total_tokens ? "a" : a.total_tokens > b.total_tokens ? "b" : "tie";
      case "duration": return (a.duration_ms ?? Infinity) < (b.duration_ms ?? Infinity) ? "a" : (a.duration_ms ?? Infinity) > (b.duration_ms ?? Infinity) ? "b" : "tie";
      default: return null;
    }
  };

  const w = selectedEval ? winner(selectedEval.result_a, selectedEval.result_b) : null;
  const ra = selectedEval?.result_a;
  const rb = selectedEval?.result_b;

  return (
    <div className="flex h-full flex-col bg-background">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3 shrink-0">
        <ArrowRightLeft className="h-4 w-4 text-primary" />
        <h2 className="text-sm font-semibold">A/B Evaluation</h2>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left panel */}
        <div className="w-72 border-r border-border p-3 overflow-y-auto shrink-0">
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">New Evaluation</h3>

          <label className="block text-xs text-muted-foreground mb-1">Workflow A</label>
          <select
            className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs mb-3 focus:outline-none focus:ring-1 focus:ring-ring"
            value={workflowAId}
            onChange={(e) => setWorkflowAId(e.target.value)}
          >
            {workflows.map((wf) => (
              <option key={wf.id} value={wf.id}>{wf.name}</option>
            ))}
          </select>

          <label className="block text-xs text-muted-foreground mb-1">Workflow B</label>
          <select
            className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs mb-3 focus:outline-none focus:ring-1 focus:ring-ring"
            value={workflowBId}
            onChange={(e) => setWorkflowBId(e.target.value)}
          >
            {workflows.map((wf) => (
              <option key={wf.id} value={wf.id}>{wf.name}</option>
            ))}
          </select>

          <label className="block text-xs text-muted-foreground mb-1">Metric</label>
          <div className="flex gap-1 mb-3">
            {(["cost", "tokens", "duration"] as Metric[]).map((m) => (
              <button
                key={m}
                onClick={() => setMetric(m)}
                className={cn(
                  "flex-1 rounded px-2 py-1 text-xs capitalize transition-colors",
                  metric === m ? "bg-primary text-primary-foreground" : "border border-border text-muted-foreground hover:bg-accent"
                )}
              >
                {m}
              </button>
            ))}
          </div>

          <label className="block text-xs text-muted-foreground mb-1">Test Input (JSON)</label>
          <textarea
            className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs font-mono mb-3 h-24 resize-none focus:outline-none focus:ring-1 focus:ring-ring"
            value={testInput}
            onChange={(e) => setTestInput(e.target.value)}
            placeholder='{"key": "value"}'
          />

          <button
            onClick={handleRun}
            disabled={running || !workflowAId || !workflowBId}
            className="w-full flex items-center justify-center gap-1.5 rounded-md bg-primary text-primary-foreground px-3 py-2 text-xs font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {running ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
            Run Evaluation
          </button>

          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mt-5 mb-2">History</h3>
          {evaluations.length === 0 && (
            <p className="text-xs text-muted-foreground italic">No evaluations yet.</p>
          )}
          <div className="space-y-1">
            {evaluations.map((ev) => (
              <div
                key={ev.id}
                className={cn(
                  "flex items-center gap-2 rounded-md px-2 py-1.5 text-xs cursor-pointer transition-colors hover:bg-accent",
                  selectedEval?.id === ev.id && "bg-accent"
                )}
                onClick={() => setSelectedEval(ev)}
              >
                <Workflow className="h-3 w-3 shrink-0 text-muted-foreground" />
                <span className="truncate flex-1">{wfName(ev.workflow_a_id)} vs {wfName(ev.workflow_b_id)}</span>
                <span className={cn("text-xs capitalize", statusColor(ev.status))}>
                  {ev.status === "running" || ev.status === "pending" ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : ev.status}
                </span>
                <button
                  onClick={(e) => { e.stopPropagation(); handleDelete(ev.id); }}
                  className="text-muted-foreground hover:text-destructive transition-colors"
                  title="Delete"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Results */}
        <div className="flex-1 overflow-y-auto p-4">
          {!selectedEval && (
            <div className="flex items-center justify-center h-full text-muted-foreground text-sm italic">
              Select or create an evaluation to view results
            </div>
          )}

          {selectedEval?.status === "error" && (
            <div className="rounded-md border border-red-500/30 bg-red-500/5 p-4 text-sm text-red-400">
              <p className="font-semibold mb-1">Evaluation Failed</p>
              <p className="text-xs">{selectedEval.error_message}</p>
            </div>
          )}

          {(selectedEval?.status === "running" || selectedEval?.status === "pending") && (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-muted-foreground">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-sm">Running evaluation…</p>
            </div>
          )}

          {selectedEval?.status === "complete" && ra && rb && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-sm font-semibold">Results</span>
                {w && w !== "tie" && (
                  <span className="ml-auto rounded-full bg-green-500/10 text-green-500 px-2 py-0.5 text-xs font-medium">
                    Winner: Workflow {w.toUpperCase()}
                  </span>
                )}
                {w === "tie" && (
                  <span className="ml-auto rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">Tie</span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <ResultCard label={`A: ${wfName(selectedEval.workflow_a_id)}`} result={ra} isWinner={w === "a"} formatMs={formatMs} />
                <ResultCard label={`B: ${wfName(selectedEval.workflow_b_id)}`} result={rb} isWinner={w === "b"} formatMs={formatMs} />
              </div>

              <div className="mt-6 rounded-md border border-border overflow-hidden">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-border bg-muted/50">
                      <th className="text-left px-3 py-2 font-semibold text-muted-foreground">Metric</th>
                      <th className="text-center px-3 py-2 font-semibold text-muted-foreground">A</th>
                      <th className="text-center px-3 py-2 font-semibold text-muted-foreground">B</th>
                    </tr>
                  </thead>
                  <tbody>
                    <ComparisonRow label="Cost" icon={<Coins className="h-3.5 w-3.5" />} aVal={`$${ra.cost_usd.toFixed(4)}`} bVal={`$${rb.cost_usd.toFixed(4)}`} aBetter={ra.cost_usd < rb.cost_usd} bBetter={ra.cost_usd > rb.cost_usd} />
                    <ComparisonRow label="Tokens" icon={<Coins className="h-3.5 w-3.5" />} aVal={String(ra.total_tokens)} bVal={String(rb.total_tokens)} aBetter={ra.total_tokens < rb.total_tokens} bBetter={ra.total_tokens > rb.total_tokens} />
                    <ComparisonRow label="Duration" icon={<Clock className="h-3.5 w-3.5" />} aVal={formatMs(ra.duration_ms)} bVal={formatMs(rb.duration_ms)} aBetter={(ra.duration_ms ?? Infinity) < (rb.duration_ms ?? Infinity)} bBetter={(ra.duration_ms ?? Infinity) > (rb.duration_ms ?? Infinity)} />
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ResultCard({ label, result, isWinner, formatMs }: { label: string; result: EvaluationResultItem; isWinner: boolean; formatMs: (ms: number | null) => string }) {
  return (
    <div className={cn("rounded-md border p-4", isWinner ? "border-green-500/50 bg-green-500/5" : "border-border")}>
      <div className="flex items-center gap-2 mb-3">
        <Workflow className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-semibold truncate">{label}</span>
        {isWinner && <span className="ml-auto text-xs text-green-500 font-medium">Winner</span>}
      </div>
      <div className="space-y-2 text-xs">
        <div className="flex justify-between"><span className="text-muted-foreground">Cost</span><span className="font-mono">${result.cost_usd.toFixed(4)}</span></div>
        <div className="flex justify-between"><span className="text-muted-foreground">Tokens</span><span className="font-mono">{result.total_tokens}</span></div>
        <div className="flex justify-between"><span className="text-muted-foreground">Duration</span><span className="font-mono">{formatMs(result.duration_ms)}</span></div>
        <div className="flex justify-between"><span className="text-muted-foreground">Status</span><span className="capitalize">{result.status}</span></div>
      </div>
    </div>
  );
}

function ComparisonRow({ label, icon, aVal, bVal, aBetter, bBetter }: { label: string; icon: React.ReactNode; aVal: string; bVal: string; aBetter: boolean; bBetter: boolean }) {
  return (
    <tr className="border-b border-border last:border-0">
      <td className="px-3 py-2 flex items-center gap-1.5">{icon}<span>{label}</span></td>
      <td className={cn("text-center px-3 py-2 font-mono", aBetter && "text-green-500 font-semibold")}>{aVal}</td>
      <td className={cn("text-center px-3 py-2 font-mono", bBetter && "text-green-500 font-semibold")}>{bVal}</td>
    </tr>
  );
}
