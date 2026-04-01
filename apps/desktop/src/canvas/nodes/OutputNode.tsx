import { Handle, Position, type NodeProps } from "@xyflow/react";
import { FileOutput } from "lucide-react";
import { cn } from "@/lib/utils";
import { useRunStore } from "@/stores/runStore";

export function OutputNode({ id, data, selected }: NodeProps) {
  const label = (data as Record<string, string>).label || "Output";
  const nodeStatus = useRunStore((s) => s.nodeStatuses[id]);
  const statusColor = nodeStatus === "complete" ? "border-green-500" : nodeStatus === "error" ? "border-red-500" : "";
  return (
    <div className={cn("w-40 rounded-lg border-2 bg-card shadow-sm transition-all", selected ? "border-primary" : "border-border", statusColor)}>
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2 rounded-t-md bg-rose-500/10 px-3 py-2 border-b border-border">
        <FileOutput className="h-4 w-4 text-rose-500 shrink-0" />
        <span className="text-xs font-semibold truncate">{label}</span>
      </div>
      <div className="px-3 py-2">
        <p className="text-xs text-muted-foreground">Workflow output</p>
      </div>
    </div>
  );
}
