import { AgentNode } from "./AgentNode";
import { AggregatorNode } from "./AggregatorNode";
import { HumanNode } from "./HumanNode";
import { MemoryNode } from "./MemoryNode";
import { OutputNode } from "./OutputNode";
import { RouterNode } from "./RouterNode";
import { SubflowNode } from "./SubflowNode";
import { TaskNode } from "./TaskNode";
import { ToolNode } from "./ToolNode";
import { TriggerNode } from "./TriggerNode";

export const nodeTypes = {
  agent: AgentNode,
  task: TaskNode,
  tool: ToolNode,
  trigger: TriggerNode,
  router: RouterNode,
  memory: MemoryNode,
  human: HumanNode,
  aggregator: AggregatorNode,
  output: OutputNode,
  subflow: SubflowNode,
};
