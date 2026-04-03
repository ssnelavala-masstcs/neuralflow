import { useState } from "react";
import { Wand2, Loader2, ArrowRight, CheckCircle, AlertCircle } from "lucide-react";
import { api } from "@/api/client";
import { useWorkflowStore } from "@/stores/workflowStore";

interface GeneratedWorkflow {
  name: string;
  description: string;
  nodes: Array<{ id: string; type: string; position: { x: number; y: number }; data: Record<string, unknown> }>;
  edges: Array<{ id: string; source: string; target: string; type: string }>;
}

export function AIWorkflowBuilder() {
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GeneratedWorkflow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { createWorkflow, setActiveWorkflow, workflows } = useWorkflowStore();

  const generate = async () => {
    if (!description.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.post<GeneratedWorkflow>("/api/ai-builder/generate", { description });
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate workflow");
    } finally {
      setLoading(false);
    }
  };

  const useWorkflow = async () => {
    if (!result) return;
    try {
      const wf = await createWorkflow(result.name);
      // Update canvas with generated nodes/edges
      useWorkflowStore.setState({
        activeWorkflowId: wf.id,
        nodes: result.nodes as any,
        edges: result.edges as any,
        isDirty: true,
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create workflow");
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-medium text-foreground mb-1 block">
          Describe your workflow
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="e.g., I need a workflow that searches the web for research, summarizes findings, and generates a report"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none h-24 focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      <button
        onClick={generate}
        disabled={loading || !description.trim()}
        className="flex items-center gap-2 rounded-md bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
      >
        {loading ? (
          <><Loader2 className="h-4 w-4 animate-spin" /> Generating…</>
        ) : (
          <><Wand2 className="h-4 w-4" /> Generate Workflow</>
        )}
      </button>

      {error && (
        <div className="flex items-center gap-2 rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {result && (
        <div className="rounded-lg border border-border bg-card p-4 space-y-3">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <h3 className="text-sm font-semibold">{result.name}</h3>
          </div>
          <p className="text-xs text-muted-foreground">{result.description}</p>

          {/* Node preview */}
          <div className="text-[10px] text-muted-foreground">
            <p>{result.nodes.length} nodes, {result.edges.length} connections</p>
            <div className="flex flex-wrap gap-1 mt-1">
              {result.nodes.map((n) => (
                <span key={n.id} className="rounded bg-muted px-1.5 py-0.5 font-mono">
                  {n.type}
                </span>
              ))}
            </div>
          </div>

          <button
            onClick={useWorkflow}
            className="flex items-center gap-1.5 rounded-md bg-primary text-primary-foreground px-3 py-1.5 text-xs font-medium hover:bg-primary/90 transition-colors"
          >
            <ArrowRight className="h-3 w-3" />
            Use This Workflow
          </button>
        </div>
      )}
    </div>
  );
}
