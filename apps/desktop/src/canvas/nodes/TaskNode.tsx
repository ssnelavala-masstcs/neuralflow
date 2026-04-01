import { Handle, Position, type NodeProps } from "@xyflow/react";
import { ClipboardList } from "lucide-react";
import { cn } from "@/lib/utils";

export function TaskNode({ data, selected }: NodeProps) {
  const label = (data as Record<string, string>).label || "Task";
  const description = (data as Record<string, string>).taskDescription || "";
  return (
    <div className={cn("w-44 rounded-lg border-2 bg-card shadow-sm transition-all", selected ? "border-primary" : "border-border")}>
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2 rounded-t-md bg-indigo-500/10 px-3 py-2 border-b border-border">
        <ClipboardList className="h-4 w-4 text-indigo-500 shrink-0" />
        <span className="text-xs font-semibold truncate">{label}</span>
      </div>
      <div className="px-3 py-2">
        <p className="text-xs text-muted-foreground line-clamp-2">{description || "No description"}</p>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
