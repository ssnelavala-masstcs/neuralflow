import { useState, useEffect } from "react";
import { X, Bot, Save } from "lucide-react";
import { useWorkflowStore } from "@/stores/workflowStore";
import { useRunStore } from "@/stores/runStore";
import { cn } from "@/lib/utils";
import type { Node } from "@xyflow/react";
import { AgentPropertiesForm } from "./AgentPropertiesForm";
import {
  TaskPropertiesForm,
  ToolPropertiesForm,
  TriggerPropertiesForm,
  RouterPropertiesForm,
  MemoryPropertiesForm,
  HumanPropertiesForm,
  AggregatorPropertiesForm,
  OutputPropertiesForm,
  SubflowPropertiesForm,
} from "./NodePropertyForms";

// Re-export shared form components for use by NodePropertyForms and AgentPropertiesForm
export { Field, SliderField, ToggleField } from "./PropertyFields";

const NODE_ICONS: Record<string, typeof Bot> = {
  agent: Bot, task: Bot, tool: Bot, trigger: Bot, router: Bot,
  memory: Bot, human: Bot, aggregator: Bot, output: Bot, subflow: Bot,
};

interface PropertiesPanelProps {
  onClose: () => void;
}

export function PropertiesPanel({ onClose }: PropertiesPanelProps) {
  const { nodes, updateNodeData, saveCanvas, isDirty } = useWorkflowStore();
  const { runStatus } = useRunStore();
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  useEffect(() => {
    const selected = nodes.find((n) => n.selected);
    setSelectedNode(selected ?? null);
  }, [nodes]);

  useEffect(() => {
    const interval = setInterval(() => {
      const selected = nodes.find((n) => n.selected);
      setSelectedNode((prev) => (prev?.id === selected?.id ? prev : selected ?? null));
    }, 200);
    return () => clearInterval(interval);
  }, [nodes]);

  if (!selectedNode) {
    return (
      <div className="flex h-full flex-col w-72 border-l border-border bg-card">
        <div className="flex items-center justify-between px-3 py-2 border-b border-border">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Properties</span>
          <button onClick={onClose} className="rounded-md p-1 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="flex-1 flex items-center justify-center p-4">
          <p className="text-xs text-muted-foreground text-center italic">Select a node on the canvas to edit its properties.</p>
        </div>
      </div>
    );
  }

  const nodeType = selectedNode.type as string;
  const data = selectedNode.data as Record<string, unknown>;
  const Icon = NODE_ICONS[nodeType] ?? Bot;
  const isRunning = runStatus === "running" || runStatus === "queued";

  const update = (updates: Record<string, unknown>) => updateNodeData(selectedNode.id, updates);
  const handleSave = async () => { await saveCanvas(); };

  return (
    <div className="flex h-full flex-col w-72 border-l border-border bg-card">
      <div className="flex items-center justify-between px-3 py-2 border-b border-border shrink-0">
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-primary" />
          <span className="text-xs font-semibold text-foreground truncate max-w-[160px]">{(data.label as string) || `${nodeType} node`}</span>
        </div>
        <div className="flex items-center gap-1">
          {isDirty && (
            <button onClick={handleSave} disabled={isRunning} className="rounded-md p-1 text-green-500 hover:text-green-400 hover:bg-accent transition-colors disabled:opacity-50" title="Save workflow">
              <Save className="h-4 w-4" />
            </button>
          )}
          <button onClick={onClose} className="rounded-md p-1 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">{nodeType.charAt(0).toUpperCase() + nodeType.slice(1)} Properties</span>
        {nodeType === "agent" && <AgentPropertiesForm data={data} update={update} />}
        {nodeType === "task" && <TaskPropertiesForm data={data} update={update} />}
        {nodeType === "tool" && <ToolPropertiesForm data={data} update={update} />}
        {nodeType === "trigger" && <TriggerPropertiesForm data={data} update={update} />}
        {nodeType === "router" && <RouterPropertiesForm data={data} update={update} />}
        {nodeType === "memory" && <MemoryPropertiesForm data={data} update={update} />}
        {nodeType === "human" && <HumanPropertiesForm data={data} update={update} />}
        {nodeType === "aggregator" && <AggregatorPropertiesForm data={data} update={update} />}
        {nodeType === "output" && <OutputPropertiesForm data={data} update={update} />}
        {nodeType === "subflow" && <SubflowPropertiesForm data={data} update={update} />}
      </div>
    </div>
  );
}
