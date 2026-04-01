from dataclasses import dataclass, field
from typing import Any


@dataclass
class NodeSpec:
    id: str
    type: str
    data: dict[str, Any]
    label: str = ""

    @property
    def name(self) -> str:
        return self.data.get("label") or self.data.get("name") or self.type


@dataclass
class EdgeSpec:
    id: str
    source: str
    target: str
    edge_type: str = "data"  # data | control | conditional
    condition: str | None = None


@dataclass
class AnalyzedWorkflow:
    nodes: list[NodeSpec]
    edges: list[EdgeSpec]
    execution_mode: str
    # Topologically sorted node IDs for sequential execution
    topo_order: list[str] = field(default_factory=list)
    # node_id → list of predecessor node IDs
    predecessors: dict[str, list[str]] = field(default_factory=dict)


def analyze(canvas_data: dict[str, Any], execution_mode: str = "sequential") -> AnalyzedWorkflow:
    raw_nodes: list[dict] = canvas_data.get("nodes", [])
    raw_edges: list[dict] = canvas_data.get("edges", [])

    nodes = [
        NodeSpec(
            id=n["id"],
            type=n.get("type", "unknown"),
            data=n.get("data", {}),
        )
        for n in raw_nodes
    ]
    edges = [
        EdgeSpec(
            id=e["id"],
            source=e["source"],
            target=e["target"],
            edge_type=e.get("data", {}).get("edgeType", "data"),
            condition=e.get("data", {}).get("condition"),
        )
        for e in raw_edges
    ]

    node_ids = {n.id for n in nodes}
    adj: dict[str, list[str]] = {n.id: [] for n in nodes}
    in_degree: dict[str, int] = {n.id: 0 for n in nodes}
    predecessors: dict[str, list[str]] = {n.id: [] for n in nodes}

    for e in edges:
        if e.source in node_ids and e.target in node_ids:
            adj[e.source].append(e.target)
            in_degree[e.target] += 1
            predecessors[e.target].append(e.source)

    # Kahn's algorithm for topological sort
    queue = [nid for nid, deg in in_degree.items() if deg == 0]
    topo: list[str] = []
    while queue:
        nid = queue.pop(0)
        topo.append(nid)
        for successor in adj[nid]:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)

    # If cycle detected, fall back to original node order
    if len(topo) < len(nodes):
        topo = [n.id for n in nodes]

    return AnalyzedWorkflow(
        nodes=nodes,
        edges=edges,
        execution_mode=execution_mode,
        topo_order=topo,
        predecessors=predecessors,
    )
