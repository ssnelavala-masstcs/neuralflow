import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  addEdge,
  type Connection,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { nodeTypes } from "./nodes";
import { edgeTypes } from "./edges";
import { useWorkflowStore } from "@/stores/workflowStore";
import { Save } from "lucide-react";

export function Canvas() {
  const { nodes, edges, onNodesChange, onEdgesChange, isDirty, isSaving, saveCanvas } = useWorkflowStore();

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
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        deleteKeyCode="Delete"
        multiSelectionKeyCode="Shift"
        className="bg-background"
      >
        <Background gap={16} size={1} className="opacity-30" />
        <Controls className="!bg-card !border-border !text-foreground" />
        <MiniMap
          className="!bg-card !border-border"
          nodeColor={(n) => {
            const colors: Record<string, string> = {
              agent: "#3b82f6",
              tool: "#22c55e",
              trigger: "#eab308",
              memory: "#a855f7",
              router: "#f97316",
              output: "#ef4444",
            };
            return colors[n.type ?? ""] ?? "#94a3b8";
          }}
        />
        <Panel position="top-right" className="flex items-center gap-2">
          {isDirty && (
            <button
              onClick={saveCanvas}
              disabled={isSaving}
              className="flex items-center gap-1.5 rounded-md bg-primary text-primary-foreground px-3 py-1.5 text-xs font-medium hover:bg-primary/90 disabled:opacity-50 shadow-sm"
            >
              <Save className="h-3 w-3" />
              {isSaving ? "Saving…" : "Save"}
            </button>
          )}
        </Panel>
      </ReactFlow>
    </div>
  );
}
