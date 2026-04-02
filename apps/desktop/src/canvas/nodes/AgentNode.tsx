import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Bot } from "lucide-react";
import { cn } from "@/lib/utils";
import { useRunStore } from "@/stores/runStore";

export function AgentNode({ id, data, selected }: NodeProps) {
  const nodeStatus = useRunStore((s) => s.nodeStatuses[id]);
  const label = (data as Record<string, string>).label || "Agent";
  const model = (data as Record<string, string>).model || "";

  const statusColor = {
    running: "border-blue-500 shadow-blue-500/30 shadow-lg",
    complete: "border-green-500",
    error: "border-red-500",
    pending: "",
    skipped: "",
  }[nodeStatus ?? ""] ?? "";

  return (
    <div
      className={cn(
        "w-48 rounded-lg border-2 bg-card text-card-foreground shadow-sm transition-all",
        selected ? "border-primary" : "border-border",
        statusColor
      )}
    >
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2 rounded-t-md bg-blue-500/10 px-3 py-2 border-b border-border">
        <Bot className="h-4 w-4 text-blue-500 shrink-0" />
        <span className="text-xs font-semibold truncate text-foreground">{label}</span>
        {nodeStatus === "running" && (
          <span className="ml-auto h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
        )}
      </div>
      <div className="px-3 py-2">
        <p className="text-xs text-muted-foreground truncate">{model || "No model selected"}</p>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
