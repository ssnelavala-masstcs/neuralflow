import { useState } from "react";
import { useWorkflowStore } from "@/stores/workflowStore";
import { useRunStore } from "@/stores/runStore";
import { CostEstimator } from "@/components/cost/CostEstimator";

interface RunModalProps {
  open: boolean;
  onClose: () => void;
}

export function RunModal({ open, onClose }: RunModalProps) {
  const [input, setInput] = useState("");
  const { activeWorkflowId, nodes, edges } = useWorkflowStore();
  const { startRun, runStatus } = useRunStore();

  if (!open) return null;

  const handleRun = async () => {
    if (!activeWorkflowId) return;
    onClose();
    const inputData = input.trim() ? { message: input.trim() } : undefined;
    await startRun(activeWorkflowId, inputData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-xl border border-border bg-card shadow-2xl p-6">
        <h2 className="text-lg font-semibold mb-1">Run Workflow</h2>
        <p className="text-sm text-muted-foreground mb-4">Optionally provide initial input for the workflow.</p>
        <textarea
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none h-28 focus:outline-none focus:ring-2 focus:ring-ring"
          placeholder="Enter your message or leave blank…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <div className="mt-3">
          <CostEstimator nodes={nodes} edges={edges} />
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={onClose} className="rounded-md px-4 py-2 text-sm border border-border hover:bg-accent transition-colors">
            Cancel
          </button>
          <button
            onClick={handleRun}
            disabled={runStatus === "running" || runStatus === "queued"}
            className="rounded-md px-4 py-2 text-sm bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors font-medium"
          >
            Run
          </button>
        </div>
      </div>
    </div>
  );
}
