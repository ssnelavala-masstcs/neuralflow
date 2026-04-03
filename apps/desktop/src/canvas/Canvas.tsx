import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  addEdge,
  type Connection,
  useReactFlow,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { nodeTypes } from "./nodes";
import { edgeTypes } from "./edges";
import { useWorkflowStore } from "@/stores/workflowStore";
import { Save, ZoomIn, ZoomOut, Maximize2, AlertTriangle, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface CanvasProps {
  onNodeSelect?: () => void;
}

export function Canvas({ onNodeSelect }: CanvasProps) {
  const { nodes, edges, onNodesChange, onEdgesChange, isDirty, isSaving, saveCanvas, validationErrors, validationWarnings, validate } = useWorkflowStore();
  const { fitView, zoomIn, zoomOut } = useReactFlow();

  const onConnect = useCallback(
    (connection: Connection) => {
      useWorkflowStore.setState((s) => ({
        edges: addEdge({ ...connection, type: "data", data: { edgeType: "data" } }, s.edges),
        isDirty: true,
      }));
    },
    []
  );

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const nodeType = e.dataTransfer.getData("application/neuralflow-node");
    if (!nodeType) return;

    const bounds = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const position = { x: e.clientX - bounds.left, y: e.clientY - bounds.top };

    const id = `${nodeType}-${Date.now()}`;
    useWorkflowStore.getState().addNode({
      id,
      type: nodeType,
      position,
      data: { label: `${nodeType.charAt(0).toUpperCase()}${nodeType.slice(1)} ${id.slice(-4)}` },
    });
  }, []);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
  }, []);

  const onNodeClick = useCallback((_e: React.MouseEvent, node: { id: string }) => {
    onNodeSelect?.();
  }, [onNodeSelect]);

  // Validation indicator
  const hasErrors = validationErrors.length > 0;
  const hasWarnings = validationWarnings.length > 0;

  // Node status coloring for minimap
  const minimapNodeColor = useCallback((node: { type?: string; id: string }) => {
    const colors: Record<string, string> = {
      agent: "#3b82f6",
      tool: "#22c55e",
      trigger: "#eab308",
      memory: "#a855f7",
      router: "#f97316",
      output: "#ef4444",
      human: "#14b8a6",
      aggregator: "#06b6d4",
      subflow: "#64748b",
      task: "#6366f1",
    };
    return colors[node.type ?? ""] ?? "#94a3b8";
  }, []);

  return (
    <div className="h-full w-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        deleteKeyCode="Delete"
        multiSelectionKeyCode="Shift"
        className="bg-background"
      >
        <Background gap={16} size={1} className="opacity-30" />
        <Controls
          className="!bg-card !border-border !text-foreground"
          showInteractive={false}
        />

        {/* Custom zoom controls */}
        <Panel position="bottom-left">
          <div className="flex flex-col gap-1">
            <button onClick={() => zoomIn()} className="rounded-md bg-card border border-border p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors" title="Zoom In">
              <ZoomIn className="h-4 w-4" />
            </button>
            <button onClick={() => zoomOut()} className="rounded-md bg-card border border-border p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors" title="Zoom Out">
              <ZoomOut className="h-4 w-4" />
            </button>
            <button onClick={() => fitView({ padding: 0.2, duration: 300 })} className="rounded-md bg-card border border-border p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors" title="Fit View">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
        </Panel>

        <MiniMap
          className="!bg-card !border-border"
          nodeColor={minimapNodeColor}
          pannable
          zoomable
        />

        {/* Empty state */}
        {nodes.length === 0 && (
          <Panel position="top-center">
            <div className="rounded-xl border border-border bg-card/90 backdrop-blur-sm p-8 text-center max-w-sm shadow-xl">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <svg className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <h3 className="text-sm font-semibold text-foreground mb-2">Start Building Your Workflow</h3>
              <p className="text-xs text-muted-foreground mb-4">
                Drag nodes from the left palette onto this canvas and connect them to create AI workflows.
              </p>
              <div className="space-y-2 text-left text-[10px] text-muted-foreground">
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded bg-primary/10 text-primary font-bold">1</span>
                  Drag a <strong className="text-foreground">Trigger</strong> node to start
                </div>
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded bg-primary/10 text-primary font-bold">2</span>
                  Add an <strong className="text-foreground">Agent</strong> node and configure your model
                </div>
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded bg-primary/10 text-primary font-bold">3</span>
                  Connect nodes by dragging from one handle to another
                </div>
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded bg-primary/10 text-primary font-bold">4</span>
                  Add an <strong className="text-foreground">Output</strong> node to capture results
                </div>
              </div>
              <p className="text-[10px] text-muted-foreground mt-4">
                💡 Press <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">Ctrl+K</kbd> for the command palette or browse <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">Templates</kbd> for starter workflows.
              </p>
            </div>
          </Panel>
        )}
        {(hasErrors || hasWarnings) && (
          <Panel position="top-left">
            <button
              onClick={validate}
              className={cn(
                "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium shadow-sm border",
                hasErrors
                  ? "bg-destructive/10 text-destructive border-destructive/30"
                  : "bg-yellow-500/10 text-yellow-500 border-yellow-500/30"
              )}
            >
              {hasErrors ? <AlertTriangle className="h-3 w-3" /> : <CheckCircle className="h-3 w-3" />}
              {hasErrors ? `${validationErrors.length} error(s)` : `${validationWarnings.length} warning(s)`}
            </button>
          </Panel>
        )}

        {/* Save indicator */}
        {isDirty && (
          <Panel position="top-right">
            <button
              onClick={saveCanvas}
              disabled={isSaving}
              className="flex items-center gap-1.5 rounded-md bg-primary text-primary-foreground px-3 py-1.5 text-xs font-medium hover:bg-primary/90 disabled:opacity-50 shadow-sm"
            >
              <Save className="h-3 w-3" />
              {isSaving ? "Saving…" : "Save"}
            </button>
          </Panel>
        )}
      </ReactFlow>
    </div>
  );
}
