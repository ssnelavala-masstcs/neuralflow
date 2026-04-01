import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Merge } from "lucide-react";
import { cn } from "@/lib/utils";

export function AggregatorNode({ data, selected }: NodeProps) {
  const label = (data as Record<string, string>).label || "Aggregator";
  return (
    <div className={cn("w-40 rounded-lg border-2 bg-card shadow-sm transition-all", selected ? "border-primary" : "border-border")}>
      <Handle type="target" position={Position.Top} id="a" style={{ left: "30%" }} />
      <Handle type="target" position={Position.Top} id="b" style={{ left: "70%" }} />
      <div className="flex items-center gap-2 rounded-t-md bg-cyan-500/10 px-3 py-2 border-b border-border">
        <Merge className="h-4 w-4 text-cyan-500 shrink-0" />
        <span className="text-xs font-semibold truncate">{label}</span>
      </div>
      <div className="px-3 py-2">
        <p className="text-xs text-muted-foreground">Merge branches</p>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
