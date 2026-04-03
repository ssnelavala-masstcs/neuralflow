import { useState, useEffect, useCallback } from "react";
import {
  History,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
  MessageSquare,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { runsApi } from "@/api/runs";
import { debugApi, type RunStep } from "@/api/debug";
import type { Run } from "@/types/run";
import { ApiError } from "@/api/client";

/** Extract a readable message from any thrown value. */
function parseError(err: unknown): string {
  if (err instanceof ApiError) {
    // Try to pull the 'detail' field out of a FastAPI JSON error body
    try {
      const body = JSON.parse(err.message);
      if (typeof body?.detail === "string") return `[${err.status}] ${body.detail}`;
      if (Array.isArray(body?.detail)) {
        return `[${err.status}] ${body.detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join("; ")}`;
      }
      // Pydantic validation errors have a different shape
      if (typeof body === "string") return `[${err.status}] ${body}`;
    } catch {/* not JSON */}
    // Raw text — truncate if huge
    const text = err.message.length > 300 ? err.message.slice(0, 300) + "…" : err.message;
    return `[${err.status}] ${text}`;
  }
  return err instanceof Error ? err.message : String(err);
}

interface Props {
  workflowId: string | null;
}

function statusBadge(status: Run["status"]) {
  const base = "inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium";
  if (status === "complete")
    return <span className={cn(base, "bg-green-500/15 text-green-400")}><CheckCircle2 size={10} />complete</span>;
  if (status === "error")
    return <span className={cn(base, "bg-red-500/15 text-red-400")}><XCircle size={10} />error</span>;
  if (status === "running")
    return <span className={cn(base, "bg-yellow-500/15 text-yellow-400")}><Clock size={10} />running</span>;
  return <span className={cn(base, "bg-muted text-muted-foreground")}>{status}</span>;
}

function stepStatusIcon(status: RunStep["status"]) {
  if (status === "complete") return <CheckCircle2 size={12} className="text-green-400 shrink-0" />;
  if (status === "error") return <XCircle size={12} className="text-red-400 shrink-0" />;
  return <Clock size={12} className="text-yellow-400 shrink-0" />;
}

function fmt(ms: number | null) {
  if (ms === null) return "—";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function fmtCost(usd: number) {
  if (usd === 0) return "$0";
  if (usd < 0.001) return `<$0.001`;
  return `$${usd.toFixed(4)}`;
}

function fmtTs(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

interface StepRowProps {
  step: RunStep;
  runId: string;
  onRerun: (newRunId: string) => void;
}

function StepRow({ step, runId, onRerun }: StepRowProps) {
  const [open, setOpen] = useState(false);
  const [rerunning, setRerunning] = useState(false);

  async function handleRerun(e: React.MouseEvent) {
    e.stopPropagation();
    setRerunning(true);
    try {
      const { new_run_id } = await debugApi.rerunFromStep(runId, step.id);
      onRerun(new_run_id);
    } catch (err) {
      alert(`Re-run failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setRerunning(false);
    }
  }

  const outputText = step.output_data?.output != null
    ? String(step.output_data.output).slice(0, 300)
    : null;

  return (
    <div className="border-b border-border last:border-0">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-2 px-3 py-2 hover:bg-muted/40 text-left"
      >
        {open ? <ChevronDown size={12} className="shrink-0 text-muted-foreground" /> : <ChevronRight size={12} className="shrink-0 text-muted-foreground" />}
        {stepStatusIcon(step.status)}
        <span className="text-xs font-medium truncate flex-1">{step.node_name}</span>
        <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">{step.node_type}</span>
        <span className="text-[10px] text-muted-foreground w-14 text-right">{fmt(step.duration_ms)}</span>
        <span className="text-[10px] text-muted-foreground w-16 text-right">{fmtCost(step.cost_usd)}</span>
        <span className="text-[10px] text-muted-foreground w-20 text-right">
          {step.input_tokens + step.output_tokens} tok
        </span>
      </button>

      {open && (
        <div className="px-8 pb-3 space-y-2">
          <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
            <span className="flex items-center gap-1"><MessageSquare size={10} />{step.llm_call_count} LLM calls</span>
            <span className="flex items-center gap-1"><RefreshCw size={10} />{step.tool_call_count} tool calls</span>
            <span>{step.input_tokens} in / {step.output_tokens} out tokens</span>
          </div>

          {step.error_message && (
            <p className="text-[11px] text-red-400 font-mono bg-red-500/10 rounded p-2 break-all">
              {step.error_message}
            </p>
          )}

          {outputText && (
            <div className="text-[11px] font-mono bg-muted rounded p-2 break-all whitespace-pre-wrap leading-relaxed">
              {outputText}
              {String(step.output_data?.output ?? "").length > 300 && (
                <span className="text-muted-foreground"> …(truncated)</span>
              )}
            </div>
          )}

          <button
            onClick={handleRerun}
            disabled={rerunning}
            className="flex items-center gap-1.5 text-[11px] text-primary hover:text-primary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <RefreshCw size={11} className={rerunning ? "animate-spin" : ""} />
            {rerunning ? "Re-running…" : "Re-run from here"}
          </button>
        </div>
      )}
    </div>
  );
}

interface RunRowProps {
  run: Run;
}

function RunRow({ run }: RunRowProps) {
  const [open, setOpen] = useState(false);
  const [steps, setSteps] = useState<RunStep[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  async function toggle() {
    if (!open && steps === null) {
      setLoading(true);
      setError(null);
      try {
        const data = await debugApi.getRunSteps(run.id);
        setSteps(data);
      } catch (err) {
        setError(parseError(err));
      } finally {
        setLoading(false);
      }
    }
    setOpen((v) => !v);
  }

  function handleRerun(newRunId: string) {
    setToast(`New run started: ${newRunId}`);
    setTimeout(() => setToast(null), 4000);
  }

  return (
    <div className="border-b border-border last:border-0">
      <button
        onClick={toggle}
        className="w-full flex items-center gap-2 px-3 py-2.5 hover:bg-muted/40 text-left"
      >
        {open ? <ChevronDown size={12} className="shrink-0 text-muted-foreground" /> : <ChevronRight size={12} className="shrink-0 text-muted-foreground" />}
        <span className="text-[10px] text-muted-foreground w-36 shrink-0">
          {run.started_at ? fmtTs(run.started_at) : "—"}
        </span>
        {statusBadge(run.status)}
        <span className="flex-1" />
        <span className="text-[10px] text-muted-foreground w-14 text-right">{fmt(run.duration_ms)}</span>
        <span className="text-[10px] text-muted-foreground w-16 text-right">{fmtCost(run.total_cost_usd)}</span>
      </button>

      {toast && (
        <div className="mx-3 mb-2 text-[11px] bg-green-500/15 text-green-400 rounded px-2 py-1">
          {toast}
        </div>
      )}

      {open && (
        <div className="ml-6 border-l border-border">
          {loading && (
            <div className="flex items-center gap-2 px-3 py-2 text-[11px] text-muted-foreground">
              <RefreshCw size={11} className="animate-spin" /> Loading steps…
            </div>
          )}
          {error && <ErrorBox message={error} compact />}
          {steps !== null && steps.length === 0 && (
            <div className="px-3 py-2 text-[11px] text-muted-foreground italic">No steps recorded.</div>
          )}
          {steps?.map((step) => (
            <StepRow key={step.id} step={step} runId={run.id} onRerun={handleRerun} />
          ))}
        </div>
      )}
    </div>
  );
}

function ErrorBox({ message, compact, onRetry }: { message: string; compact?: boolean; onRetry?: () => void }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(message).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };
  return (
    <div className={cn("mx-3 rounded-md bg-red-500/10 border border-red-500/20", compact ? "my-1 p-2" : "my-3 p-3")}>
      <div className="flex items-start gap-2">
        <XCircle size={13} className="text-red-400 shrink-0 mt-0.5" />
        <p className="text-[11px] text-red-400 font-mono break-all flex-1 whitespace-pre-wrap">{message}</p>
      </div>
      <div className="flex items-center gap-2 mt-2">
        <button onClick={copy} className="text-[10px] text-muted-foreground hover:text-foreground transition-colors">
          {copied ? "Copied!" : "Copy error"}
        </button>
        {onRetry && (
          <button onClick={onRetry} className="text-[10px] text-primary hover:text-primary/80 transition-colors flex items-center gap-1">
            <RefreshCw size={10} /> Retry
          </button>
        )}
      </div>
    </div>
  );
}

export function RunHistoryPanel({ workflowId }: Props) {
  const [runs, setRuns] = useState<Run[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!workflowId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await runsApi.list(workflowId);
      setRuns(data);
    } catch (err) {
      setError(parseError(err));
    } finally {
      setLoading(false);
    }
  }, [workflowId]);

  useEffect(() => {
    setRuns(null);
    load();
  }, [load]);

  if (!workflowId) {
    return (
      <div className="flex items-center justify-center h-full text-xs text-muted-foreground italic">
        No workflow selected.
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-border shrink-0">
        <span className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
          <History size={13} /> Run History
        </span>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground disabled:opacity-50 transition-colors"
        >
          <RefreshCw size={11} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading && runs === null && (
          <div className="flex items-center gap-2 px-3 py-4 text-xs text-muted-foreground">
            <RefreshCw size={12} className="animate-spin" /> Loading runs…
          </div>
        )}
        {error && <ErrorBox message={error} onRetry={load} />}
        {runs !== null && runs.length === 0 && (
          <div className="px-3 py-4 text-xs text-muted-foreground italic">No runs yet for this workflow.</div>
        )}
        {runs?.map((run) => (
          <RunRow key={run.id} run={run} />
        ))}
      </div>
    </div>
  );
}
