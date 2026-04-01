import { Bot, ClipboardList, Database, FileOutput, GitBranch, Layers, Merge, Play, UserCheck, Wrench } from "lucide-react";
import type { ReactNode } from "react";

interface PaletteItem {
  type: string;
  label: string;
  icon: ReactNode;
  color: string;
  description: string;
}

const PALETTE_ITEMS: PaletteItem[] = [
  { type: "agent", label: "Agent", icon: <Bot className="h-4 w-4" />, color: "text-blue-500 bg-blue-500/10", description: "AI model with tools" },
  { type: "task", label: "Task", icon: <ClipboardList className="h-4 w-4" />, color: "text-indigo-500 bg-indigo-500/10", description: "Unit of work" },
  { type: "tool", label: "Tool", icon: <Wrench className="h-4 w-4" />, color: "text-green-500 bg-green-500/10", description: "Built-in or MCP tool" },
  { type: "trigger", label: "Trigger", icon: <Play className="h-4 w-4" />, color: "text-yellow-500 bg-yellow-500/10", description: "Start workflow" },
  { type: "router", label: "Router", icon: <GitBranch className="h-4 w-4" />, color: "text-orange-500 bg-orange-500/10", description: "Conditional branch" },
  { type: "memory", label: "Memory", icon: <Database className="h-4 w-4" />, color: "text-purple-500 bg-purple-500/10", description: "Vector / KV store" },
  { type: "human", label: "Human", icon: <UserCheck className="h-4 w-4" />, color: "text-teal-500 bg-teal-500/10", description: "Approval checkpoint" },
  { type: "aggregator", label: "Aggregator", icon: <Merge className="h-4 w-4" />, color: "text-cyan-500 bg-cyan-500/10", description: "Merge branches" },
  { type: "output", label: "Output", icon: <FileOutput className="h-4 w-4" />, color: "text-rose-500 bg-rose-500/10", description: "Workflow result" },
  { type: "subflow", label: "Subflow", icon: <Layers className="h-4 w-4" />, color: "text-slate-500 bg-slate-500/10", description: "Nested workflow" },
];

export function NodePalette() {
  const onDragStart = (e: React.DragEvent, nodeType: string) => {
    e.dataTransfer.setData("application/neuralflow-node", nodeType);
    e.dataTransfer.effectAllowed = "copy";
  };

  return (
    <div className="flex flex-col gap-0.5 p-2">
      <p className="px-2 py-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Nodes</p>
      {PALETTE_ITEMS.map((item) => (
        <div
          key={item.type}
          draggable
          onDragStart={(e) => onDragStart(e, item.type)}
          className="flex items-center gap-2.5 rounded-md px-2 py-2 cursor-grab hover:bg-accent transition-colors select-none"
          title={item.description}
        >
          <span className={`flex h-7 w-7 items-center justify-center rounded-md shrink-0 ${item.color}`}>
            {item.icon}
          </span>
          <div className="min-w-0">
            <p className="text-xs font-medium leading-none">{item.label}</p>
            <p className="text-xs text-muted-foreground mt-0.5 truncate">{item.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
