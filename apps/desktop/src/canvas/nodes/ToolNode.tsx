import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Wrench } from "lucide-react";
import { cn } from "@/lib/utils";

export function ToolNode({ data, selected }: NodeProps) {
  const label = (data as Record<string, string>).label || "Tool";
  const toolName = (data as Record<string, string>).toolName || "";
  return (
    <div className={cn("w-40 rounded-lg border-2 bg-card shadow-sm transition-all", selected ? "border-primary" : "border-border")}>
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2 rounded-t-md bg-green-500/10 px-3 py-2 border-b border-border">
        <Wrench className="h-4 w-4 text-green-500 shrink-0" />
        <span className="text-xs font-semibold truncate">{label}</span>
      </div>
      <div className="px-3 py-2">
        <p className="text-xs text-muted-foreground">{toolName || "No tool selected"}</p>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
