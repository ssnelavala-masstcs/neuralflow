import { useState } from "react";
import { ChevronRight, PlusCircle, Workflow } from "lucide-react";
import { NodePalette } from "@/components/palette/NodePalette";
import { useWorkflowStore } from "@/stores/workflowStore";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const { workflows, activeWorkflowId, setActiveWorkflow, createWorkflow } = useWorkflowStore();
  const [creatingName, setCreatingName] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  const handleCreate = async () => {
    if (!creatingName.trim()) return;
    const wf = await createWorkflow(creatingName.trim());
    setActiveWorkflow(wf.id);
    setCreatingName("");
    setShowCreate(false);
  };

  return (
    <div className="flex h-full flex-col w-56 border-r border-border bg-card">
      {/* Workflows list */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Workflows</span>
        <button onClick={() => setShowCreate(!showCreate)} className="text-muted-foreground hover:text-foreground transition-colors" title="New workflow">
          <PlusCircle className="h-4 w-4" />
        </button>
      </div>

      {showCreate && (
        <div className="flex gap-1 px-2 py-1.5 border-b border-border">
          <input
            autoFocus
            className="flex-1 rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
            placeholder="Workflow name…"
            value={creatingName}
            onChange={(e) => setCreatingName(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleCreate(); if (e.key === "Escape") setShowCreate(false); }}
          />
          <button onClick={handleCreate} className="text-xs rounded-md bg-primary text-primary-foreground px-2 py-1 hover:bg-primary/90">
            Add
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto py-1">
        {workflows.length === 0 && (
          <p className="px-4 py-3 text-xs text-muted-foreground italic">No workflows yet.</p>
        )}
        {workflows.map((wf) => (
          <button
            key={wf.id}
            onClick={() => setActiveWorkflow(wf.id)}
            className={cn(
              "flex w-full items-center gap-2 px-3 py-2 text-xs text-left hover:bg-accent transition-colors",
              wf.id === activeWorkflowId && "bg-accent text-accent-foreground font-medium"
            )}
          >
            <Workflow className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
            <span className="truncate">{wf.name}</span>
            {wf.id === activeWorkflowId && <ChevronRight className="ml-auto h-3 w-3 shrink-0 text-muted-foreground" />}
          </button>
        ))}
      </div>

      {/* Node palette */}
      <div className="border-t border-border overflow-y-auto max-h-80">
        <NodePalette />
      </div>
    </div>
  );
}
