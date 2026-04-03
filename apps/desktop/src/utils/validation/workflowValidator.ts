import type { Node, Edge } from "@xyflow/react";

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  nodeId?: string;
  code: string;
  message: string;
  severity: "error";
}

export interface ValidationWarning {
  nodeId?: string;
  code: string;
  message: string;
  severity: "warning";
}

export function validateWorkflow(
  nodes: Node[],
  edges: Edge[]
): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationWarning[] = [];

  if (nodes.length === 0) {
    return { valid: true, errors: [], warnings: [] };
  }

  // 1. At least one Trigger node
  const triggers = nodes.filter((n) => n.type === "trigger");
  if (triggers.length === 0) {
    errors.push({
      code: "missing_trigger",
      message: "Workflow needs at least one Trigger node.",
      severity: "error",
    });
  }

  // 2. At least one Output node
  const outputs = nodes.filter((n) => n.type === "output");
  if (outputs.length === 0) {
    errors.push({
      code: "missing_output",
      message: "Workflow needs at least one Output node.",
      severity: "error",
    });
  }

  // 3. All Agent nodes must have a model configured
  for (const node of nodes) {
    if (node.type === "agent") {
      const data = node.data as Record<string, unknown>;
      if (!data.model || (data.model as string).trim() === "") {
        errors.push({
          nodeId: node.id,
          code: "missing_model",
          message: `Agent "${data.name ?? node.id}" is missing its model configuration.`,
          severity: "error",
        });
      }
    }
  }

  // 4. No orphaned nodes — every node must be reachable from a trigger
  const reachable = findReachableFromTriggers(nodes, edges);
  const orphaned = nodes.filter((n) => !reachable.has(n.id));
  if (orphaned.length > 0) {
    warnings.push({
      code: "orphaned_nodes",
      message: `${orphaned.length} node(s) are not connected to the workflow.`,
      severity: "warning",
    });
    for (const node of orphaned) {
      warnings.push({
        nodeId: node.id,
        code: "orphaned_node",
        message: `Node "${(node.data as Record<string, unknown>).name ?? node.id}" is not connected.`,
        severity: "warning",
      });
    }
  }

  // 5. Check for disconnected handles
  for (const node of nodes) {
    const nodeEdges = edges.filter(
      (e) => e.source === node.id || e.target === node.id
    );
    const nodeType = node.type;

    // Trigger nodes should have at least one outgoing edge
    if (nodeType === "trigger" && nodeEdges.filter((e) => e.source === node.id).length === 0) {
      warnings.push({
        nodeId: node.id,
        code: "disconnected_trigger",
        message: "Trigger node has no outgoing connections.",
        severity: "warning",
      });
    }

    // Output nodes should have at least one incoming edge
    if (nodeType === "output" && nodeEdges.filter((e) => e.target === node.id).length === 0) {
      warnings.push({
        nodeId: node.id,
        code: "disconnected_output",
        message: "Output node has no incoming connections.",
        severity: "warning",
      });
    }
  }

  // 6. No duplicate node IDs
  const ids = nodes.map((n) => n.id);
  const duplicates = ids.filter((id, i) => ids.indexOf(id) !== i);
  if (duplicates.length > 0) {
    errors.push({
      code: "duplicate_ids",
      message: `Duplicate node IDs: ${[...new Set(duplicates)].join(", ")}`,
      severity: "error",
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

function findReachableFromTriggers(nodes: Node[], edges: Edge[]): Set<string> {
  const reachable = new Set<string>();
  const triggers = nodes.filter((n) => n.type === "trigger");
  const adjacency = buildAdjacency(edges);

  const queue = triggers.map((t) => t.id);
  while (queue.length > 0) {
    const current = queue.shift()!;
    if (reachable.has(current)) continue;
    reachable.add(current);
    for (const neighbor of adjacency.get(current) ?? []) {
      if (!reachable.has(neighbor)) {
        queue.push(neighbor);
      }
    }
  }

  return reachable;
}

function buildAdjacency(edges: Edge[]): Map<string, string[]> {
  const map = new Map<string, string[]>();
  for (const edge of edges) {
    if (!map.has(edge.source)) map.set(edge.source, []);
    map.get(edge.source)!.push(edge.target);
  }
  return map;
}
