import { useRunStore } from "@/stores/runStore";
import { cn } from "@/lib/utils";
import type { StreamEvent } from "@/types/run";
import { useEffect, useRef, useState } from "react";
import { AutoDebugPanel } from "@/components/debug/AutoDebugPanel";

function EventLine({ event }: { event: StreamEvent }) {
  const colors: Record<string, string> = {
    run_started: "text-blue-400",
    run_completed: "text-green-400",
    run_failed: "text-red-400",
    node_started: "text-blue-300",
    node_completed: "text-green-300",
    node_failed: "text-red-300",
    llm_chunk: "text-foreground",
    tool_call: "text-yellow-300",
    tool_result: "text-yellow-400",
    log: "text-muted-foreground",
    error: "text-red-400",
  };

  const label: Record<string, string> = {
    run_started: "[RUN]",
    run_completed: "[DONE]",
    run_failed: "[FAIL]",
    node_started: `[${event.node_name ?? event.node_id}]`,
    node_completed: `[${event.node_name ?? event.node_id}]`,
    node_failed: `[${event.node_name ?? event.node_id}]`,
    llm_chunk: `[${event.node_id ?? ""}]`,
    tool_call: `[TOOL:${event.tool_name}]`,
    tool_result: `[TOOL:${event.tool_name}]`,
    log: `[LOG]`,
    error: `[ERR]`,
  };

  const message: Record<string, string> = {
    run_started: "Workflow started",
    run_completed: `Completed${event.output ? ` — ${JSON.stringify(event.output).slice(0, 80)}` : ""}`,
    run_failed: event.error ?? "Unknown error",
    node_started: "started",
    node_completed: `done (cost: $${event.cost_usd?.toFixed(5) ?? "0"})`,
    node_failed: event.error ?? "error",
    llm_chunk: event.chunk ?? "",
    tool_call: `calling with ${JSON.stringify(event.input ?? {}).slice(0, 60)}`,
    tool_result: `returned ${JSON.stringify(event.output ?? {}).slice(0, 60)}`,
    log: event.message ?? "",
    error: event.message ?? event.error ?? "error",
  };

  if (event.type === "done" || event.type === "cancelled") return null;

  return (
    <div className={cn("font-mono text-xs leading-relaxed whitespace-pre-wrap", colors[event.type] ?? "text-foreground")}>
      <span className="opacity-60 select-none mr-1">{label[event.type] ?? `[${event.type}]`}</span>
      <span>{message[event.type] ?? ""}</span>
    </div>
  );
}

export function RunLog() {
  const { streamEvents, runStatus, output } = useRunStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [lastError, setLastError] = useState<{ message: string; nodeId?: string } | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [streamEvents.length]);

  // Track last error for auto-debug
  useEffect(() => {
    for (let i = streamEvents.length - 1; i >= 0; i--) {
      const ev = streamEvents[i];
      if (ev.type === "error" || ev.type === "node_failed" || ev.type === "run_failed") {
        setLastError({ message: ev.error ?? ev.message ?? "Unknown error", nodeId: ev.node_id });
        break;
      }
    }
    if (runStatus === "idle") setLastError(null);
  }, [streamEvents, runStatus]);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 px-3 py-1.5 border-b border-border shrink-0">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Run Log</span>
        <span className={cn(
          "ml-auto text-xs px-2 py-0.5 rounded-full font-medium",
          runStatus === "idle" && "bg-muted text-muted-foreground",
          runStatus === "running" && "bg-blue-500/20 text-blue-400",
          runStatus === "complete" && "bg-green-500/20 text-green-400",
          runStatus === "error" && "bg-red-500/20 text-red-400",
          runStatus === "queued" && "bg-yellow-500/20 text-yellow-400",
        )}>
          {runStatus}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto p-3 bg-background/60 space-y-0.5">
        {streamEvents.length === 0 && (
          <p className="text-xs text-muted-foreground italic">No run started yet. Press Run to execute the workflow.</p>
        )}
        {streamEvents.map((ev, i) => <EventLine key={i} event={ev} />)}
        <div ref={bottomRef} />
      </div>
      {lastError && (
        <div className="border-t border-border p-2 shrink-0">
          <AutoDebugPanel
            errorMessage={lastError.message}
            nodeConfig={lastError.nodeId ? { node_id: lastError.nodeId } : undefined}
          />
        </div>
      )}
    </div>
  );
}
