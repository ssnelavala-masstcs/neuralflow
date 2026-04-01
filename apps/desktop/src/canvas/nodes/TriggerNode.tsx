import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Play } from "lucide-react";
import { cn } from "@/lib/utils";

export function TriggerNode({ data, selected }: NodeProps) {
  const label = (data as Record<string, string>).label || "Trigger";
  const triggerType = (data as Record<string, string>).triggerType || "manual";
  return (
    <div className={cn("w-40 rounded-lg border-2 bg-card shadow-sm transition-all", selected ? "border-primary" : "border-border")}>
      <div className="flex items-center gap-2 rounded-t-md bg-yellow-500/10 px-3 py-2 border-b border-border">
        <Play className="h-4 w-4 text-yellow-500 shrink-0" />
        <span className="text-xs font-semibold truncate">{label}</span>
      </div>
      <div className="px-3 py-2">
        <p className="text-xs text-muted-foreground capitalize">{triggerType}</p>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
