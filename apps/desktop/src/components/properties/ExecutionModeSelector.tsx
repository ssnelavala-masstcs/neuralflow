import { GitBranch, Layers, ListOrdered, Network } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ExecutionMode } from "@/types/workflow";

interface ExecutionModeSelectorProps {
  mode: ExecutionMode;
  onChange: (mode: ExecutionMode) => void;
}

const MODES: {
  value: ExecutionMode;
  label: string;
  description: string;
  Icon: React.ComponentType<{ className?: string }>;
}[] = [
  {
    value: "sequential",
    label: "Sequential",
    description: "Runs agents one after another in order",
    Icon: ListOrdered,
  },
  {
    value: "parallel",
    label: "Parallel",
    description: "Runs independent agents simultaneously",
    Icon: Layers,
  },
  {
    value: "hierarchical",
    label: "Hierarchical",
    description: "Manager agent delegates to worker agents (CrewAI)",
    Icon: Network,
  },
  {
    value: "state_machine",
    label: "State Machine",
    description: "Conditional branching with Router nodes (LangGraph)",
    Icon: GitBranch,
  },
];

export function ExecutionModeSelector({ mode, onChange }: ExecutionModeSelectorProps) {
  return (
    <div className="grid grid-cols-1 gap-1.5 p-2">
      {MODES.map(({ value, label, description, Icon }) => (
        <button
          key={value}
          onClick={() => onChange(value)}
          className={cn(
            "flex items-start gap-2.5 rounded-md border px-2.5 py-2 text-left transition-colors hover:bg-accent",
            mode === value
              ? "border-primary bg-primary/5 text-foreground"
              : "border-border bg-background text-muted-foreground"
          )}
        >
          <Icon className={cn("mt-0.5 h-4 w-4 shrink-0", mode === value && "text-primary")} />
          <div className="min-w-0">
            <p className={cn("text-xs font-medium leading-tight", mode === value && "text-foreground")}>
              {label}
            </p>
            <p className="text-[11px] leading-snug text-muted-foreground">{description}</p>
          </div>
        </button>
      ))}
    </div>
  );
}
