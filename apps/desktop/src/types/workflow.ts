export type NodeType =
  | "agent"
  | "task"
  | "tool"
  | "trigger"
  | "router"
  | "memory"
  | "human"
  | "aggregator"
  | "output"
  | "subflow";

export type EdgeType = "data" | "control" | "conditional";

export type ExecutionMode = "sequential" | "parallel" | "hierarchical" | "state_machine";

export interface AgentNodeData {
  label: string;
  model: string;
  systemPrompt: string;
  temperature: number;
  maxTokens: number;
  tools: string[];
  role: string;
  allowDelegation: boolean;
  verbose: boolean;
  maxIterations: number;
}

export interface ToolNodeData {
  label: string;
  toolName: string;
  config: Record<string, unknown>;
}

export interface TriggerNodeData {
  label: string;
  triggerType: "manual" | "cron" | "webhook" | "file_watch";
  cronExpression?: string;
  webhookPath?: string;
}

export interface OutputNodeData {
  label: string;
  outputFormat: "markdown" | "json" | "text";
}

export interface RouterNodeData {
  label: string;
  conditions: Array<{ expression: string; targetLabel: string }>;
}

export interface MemoryNodeData {
  label: string;
  storeType: "vector" | "kv" | "conversation";
  embeddingModel?: string;
}

export interface HumanNodeData {
  label: string;
  prompt: string;
}

export interface AggregatorNodeData {
  label: string;
  strategy: "concat" | "json_merge" | "last";
}

export type NodeData =
  | AgentNodeData
  | ToolNodeData
  | TriggerNodeData
  | OutputNodeData
  | RouterNodeData
  | MemoryNodeData
  | HumanNodeData
  | AggregatorNodeData
  | Record<string, unknown>;

export interface CanvasData {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
}

export interface CanvasNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: NodeData;
}

export interface CanvasEdge {
  id: string;
  source: string;
  target: string;
  type?: EdgeType;
  data?: { edgeType: EdgeType; condition?: string };
}

export interface Workflow {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  tags: string[];
  canvas_data: CanvasData;
  execution_mode: ExecutionMode;
  created_at: string;
  updated_at: string;
  last_run_at: string | null;
  run_count: number;
  is_template: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}
