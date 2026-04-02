import { applyEdgeChanges, applyNodeChanges, type Edge, type Node, type NodeChange, type EdgeChange } from "@xyflow/react";
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import type { CanvasData, ExecutionMode, Workflow, Workspace } from "@/types/workflow";
import { workflowsApi } from "@/api/workflows";

interface WorkflowState {
  workspaceId: string | null;
  workflows: Workflow[];
  activeWorkflowId: string | null;
  nodes: Node[];
  edges: Edge[];
  isDirty: boolean;
  isSaving: boolean;

  // Actions
  setWorkspace: (id: string) => void;
  setWorkflows: (workflows: Workflow[]) => void;
  setActiveWorkflow: (id: string) => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  addNode: (node: Node) => void;
  updateNodeData: (id: string, data: Partial<Node["data"]>) => void;
  updateExecutionMode: (mode: ExecutionMode) => Promise<void>;
  saveCanvas: () => Promise<void>;
  loadWorkflows: (workspaceId: string) => Promise<void>;
  createWorkflow: (name: string) => Promise<Workflow>;
  deleteWorkflow: (id: string) => Promise<void>;
}

export const useWorkflowStore = create<WorkflowState>()(
  immer((set, get) => ({
    workspaceId: null,
    workflows: [],
    activeWorkflowId: null,
    nodes: [],
    edges: [],
    isDirty: false,
    isSaving: false,

    setWorkspace: (id) => set((s) => { s.workspaceId = id; }),

    setWorkflows: (workflows) => set((s) => { s.workflows = workflows; }),

    setActiveWorkflow: (id) =>
      set((s) => {
        const wf = s.workflows.find((w) => w.id === id);
        if (!wf) return;
        s.activeWorkflowId = id;
        s.nodes = wf.canvas_data.nodes as unknown as Node[];
        s.edges = wf.canvas_data.edges as unknown as Edge[];
        s.isDirty = false;
      }),

    onNodesChange: (changes) =>
      set((s) => {
        s.nodes = applyNodeChanges(changes, s.nodes);
        s.isDirty = true;
      }),

    onEdgesChange: (changes) =>
      set((s) => {
        s.edges = applyEdgeChanges(changes, s.edges);
        s.isDirty = true;
      }),

    addNode: (node) =>
      set((s) => {
        s.nodes.push(node);
        s.isDirty = true;
      }),

    updateNodeData: (id, data) =>
      set((s) => {
        const node = s.nodes.find((n) => n.id === id);
        if (node) {
          Object.assign(node.data, data);
          s.isDirty = true;
        }
      }),

    updateExecutionMode: async (mode) => {
      const { activeWorkflowId } = get();
      if (!activeWorkflowId) return;
      await workflowsApi.update(activeWorkflowId, { execution_mode: mode });
      set((s) => {
        const wf = s.workflows.find((w) => w.id === activeWorkflowId);
        if (wf) wf.execution_mode = mode;
      });
    },

    saveCanvas: async () => {
      const { activeWorkflowId, nodes, edges } = get();
      if (!activeWorkflowId) return;
      set((s) => { s.isSaving = true; });
      try {
        const canvas_data: CanvasData = {
          nodes: nodes as unknown as CanvasData["nodes"],
          edges: edges as unknown as CanvasData["edges"],
        };
        await workflowsApi.update(activeWorkflowId, { canvas_data });
        set((s) => { s.isDirty = false; });
      } finally {
        set((s) => { s.isSaving = false; });
      }
    },

    loadWorkflows: async (workspaceId) => {
      const workflows = await workflowsApi.list(workspaceId);
      set((s) => {
        s.workspaceId = workspaceId;
        s.workflows = workflows;
        if (workflows.length > 0 && !s.activeWorkflowId) {
          s.activeWorkflowId = workflows[0].id;
          s.nodes = workflows[0].canvas_data.nodes as unknown as Node[];
          s.edges = workflows[0].canvas_data.edges as unknown as Edge[];
        }
      });
    },

    createWorkflow: async (name) => {
      const { workspaceId } = get();
      if (!workspaceId) throw new Error("No active workspace");
      const wf = await workflowsApi.create(workspaceId, name);
      set((s) => { s.workflows.unshift(wf); });
      return wf;
    },

    deleteWorkflow: async (id) => {
      await workflowsApi.delete(id);
      set((s) => {
        s.workflows = s.workflows.filter((w) => w.id !== id);
        if (s.activeWorkflowId === id) {
          s.activeWorkflowId = s.workflows[0]?.id ?? null;
          s.nodes = s.workflows[0]?.canvas_data.nodes as unknown as Node[] ?? [];
          s.edges = s.workflows[0]?.canvas_data.edges as unknown as Edge[] ?? [];
        }
      });
    },
  }))
);
