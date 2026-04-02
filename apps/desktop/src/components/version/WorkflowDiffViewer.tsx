import { useState, useMemo } from "react";
import { GitCompare, ArrowRight, Plus, Minus, Pencil, X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { CanvasData, NodeType } from "@/types/workflow";

interface DiffItem {
  type: "node_added" | "node_removed" | "node_modified" | "edge_added" | "edge_removed" | "edge_modified";
  id: string;
  label: string;
  nodeType?: NodeType;
  changes?: string[];
}

interface WorkflowDiffViewerProps {
  baseVersion: CanvasData;
  targetVersion: CanvasData;
  baseLabel?: string;
  targetLabel?: string;
}

export function WorkflowDiffViewer({
  baseVersion,
  targetVersion,
  baseLabel = "Base",
  targetLabel = "Target",
}: WorkflowDiffViewerProps) {
  const [view, setView] = useState<"split" | "unified">("split");
  const [filter, setFilter] = useState<"all" | "added" | "removed" | "modified">("all");

  const diff = useMemo(() => computeDiff(baseVersion, targetVersion), [baseVersion, targetVersion]);

  const filtered = diff.filter((item) => {
    if (filter === "all") return true;
    if (filter === "added") return item.type.includes("added");
    if (filter === "removed") return item.type.includes("removed");
    if (filter === "modified") return item.type.includes("modified");
    return true;
  });

  const stats = {
    added: diff.filter((d) => d.type.includes("added")).length,
    removed: diff.filter((d) => d.type.includes("removed")).length,
    modified: diff.filter((d) => d.type.includes("modified")).length,
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
        <div className="flex items-center gap-2">
          <GitCompare className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold">Workflow Diff</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-md border border-border overflow-hidden">
            <button
              onClick={() => setView("split")}
              className={cn(
                "px-3 py-1 text-xs font-medium transition-colors",
                view === "split" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
              )}
            >
              Split
            </button>
            <button
              onClick={() => setView("unified")}
              className={cn(
                "px-3 py-1 text-xs font-medium transition-colors border-l border-border",
                view === "unified" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
              )}
            >
              Unified
            </button>
          </div>
        </div>
      </div>

      {/* Stats bar */}
      <div className="flex items-center gap-4 px-4 py-2 bg-muted/30 border-b border-border shrink-0">
        <span className="text-xs text-muted-foreground">
          {baseLabel} <ArrowRight className="h-3 w-3 inline mx-0.5" /> {targetLabel}
        </span>
        <div className="flex items-center gap-3 ml-auto">
          <span className="flex items-center gap-1 text-xs text-green-500">
            <Plus className="h-3 w-3" /> +{stats.added}
          </span>
          <span className="flex items-center gap-1 text-xs text-red-500">
            <Minus className="h-3 w-3" /> -{stats.removed}
          </span>
          <span className="flex items-center gap-1 text-xs text-yellow-500">
            <Pencil className="h-3 w-3" /> ~{stats.modified}
          </span>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-1 px-4 py-1.5 border-b border-border shrink-0">
        {(["all", "added", "removed", "modified"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "px-2.5 py-1 text-xs rounded-md transition-colors capitalize",
              filter === f ? "bg-accent text-foreground font-medium" : "text-muted-foreground hover:text-foreground"
            )}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Diff content */}
      <div className="flex-1 overflow-y-auto p-4 min-h-0">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <GitCompare className="h-8 w-8 mb-2 opacity-50" />
            <p className="text-sm">No differences found</p>
          </div>
        ) : view === "split" ? (
          <SplitDiffView items={filtered} />
        ) : (
          <UnifiedDiffView items={filtered} />
        )}
      </div>
    </div>
  );
}

/* ─── Split View ─── */

function SplitDiffView({ items }: { items: DiffItem[] }) {
  const leftItems = items.filter((i) => !i.type.includes("added") || i.type.includes("edge"));
  const rightItems = items.filter((i) => !i.type.includes("removed") || i.type.includes("edge"));

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider sticky top-0 bg-background/80 backdrop-blur-sm py-1">Base</h4>
        {leftItems.map((item) => (
          <DiffCard key={item.id} item={item} side="base" />
        ))}
      </div>
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider sticky top-0 bg-background/80 backdrop-blur-sm py-1">Target</h4>
        {rightItems.map((item) => (
          <DiffCard key={item.id} item={item} side="target" />
        ))}
      </div>
    </div>
  );
}

/* ─── Unified View ─── */

function UnifiedDiffView({ items }: { items: DiffItem[] }) {
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <DiffCard key={item.id} item={item} side="unified" />
      ))}
    </div>
  );
}

/* ─── Diff Card ─── */

function DiffCard({ item, side }: { item: DiffItem; side: "base" | "target" | "unified" }) {
  const isAdded = item.type.includes("added");
  const isRemoved = item.type.includes("removed");
  const isModified = item.type.includes("modified");

  if (side === "base" && isAdded) return null;
  if (side === "target" && isRemoved) return null;
  if (side === "unified" && isRemoved) {
    return (
      <div className="rounded-md border border-red-500/30 bg-red-500/5 p-3">
        <div className="flex items-center gap-2">
          <Minus className="h-3.5 w-3.5 text-red-500 shrink-0" />
          <span className="text-xs font-medium text-red-400">{item.label}</span>
          <span className="text-[10px] text-muted-foreground ml-auto">{item.nodeType}</span>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "rounded-md border p-3",
        isAdded && "border-green-500/30 bg-green-500/5",
        isRemoved && "border-red-500/30 bg-red-500/5",
        isModified && "border-yellow-500/30 bg-yellow-500/5"
      )}
    >
      <div className="flex items-center gap-2">
        {isAdded && <Plus className="h-3.5 w-3.5 text-green-500 shrink-0" />}
        {isRemoved && <Minus className="h-3.5 w-3.5 text-red-500 shrink-0" />}
        {isModified && <Pencil className="h-3.5 w-3.5 text-yellow-500 shrink-0" />}
        <span className="text-xs font-medium text-foreground">{item.label}</span>
        {item.nodeType && (
          <span className="text-[10px] text-muted-foreground ml-auto">{item.nodeType}</span>
        )}
      </div>
      {item.changes && item.changes.length > 0 && (
        <ul className="mt-2 space-y-1">
          {item.changes.map((change, i) => (
            <li key={i} className="text-[10px] font-mono text-muted-foreground pl-2 border-l-2 border-muted">
              {change}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* ─── Diff Computation ─── */

function computeDiff(base: CanvasData, target: CanvasData): DiffItem[] {
  const items: DiffItem[] = [];

  const baseNodes = new Map(base.nodes.map((n) => [n.id, n]));
  const targetNodes = new Map(target.nodes.map((n) => [n.id, n]));

  // Added nodes
  for (const [id, node] of targetNodes) {
    if (!baseNodes.has(id)) {
      items.push({
        type: "node_added",
        id,
        label: (node.data as Record<string, unknown>)?.label as string || id,
        nodeType: node.type as NodeType,
      });
    }
  }

  // Removed nodes
  for (const [id, node] of baseNodes) {
    if (!targetNodes.has(id)) {
      items.push({
        type: "node_removed",
        id,
        label: (node.data as Record<string, unknown>)?.label as string || id,
        nodeType: node.type as NodeType,
      });
    }
  }

  // Modified nodes
  for (const [id, targetNode] of targetNodes) {
    const baseNode = baseNodes.get(id);
    if (!baseNode) continue;

    const changes: string[] = [];
    const baseData = baseNode.data as Record<string, unknown>;
    const targetData = targetNode.data as Record<string, unknown>;

    const allKeys = new Set([...Object.keys(baseData || {}), ...Object.keys(targetData || {})]);
    for (const key of allKeys) {
      const baseVal = JSON.stringify(baseData?.[key] ?? null);
      const targetVal = JSON.stringify(targetData?.[key] ?? null);
      if (baseVal !== targetVal) {
        changes.push(`${key}: ${truncate(baseVal, 40)} → ${truncate(targetVal, 40)}`);
      }
    }

    if (baseNode.position.x !== targetNode.position.x || baseNode.position.y !== targetNode.position.y) {
      changes.push(`position changed`);
    }

    if (changes.length > 0) {
      items.push({
        type: "node_modified",
        id,
        label: (targetData?.label as string) || id,
        nodeType: targetNode.type as NodeType,
        changes,
      });
    }
  }

  // Edge diff
  const baseEdges = new Map(base.edges.map((e) => [e.id, e]));
  const targetEdges = new Map(target.edges.map((e) => [e.id, e]));

  for (const [id] of targetEdges) {
    if (!baseEdges.has(id)) {
      const te = targetEdges.get(id)!;
      const targetNode = targetNodes.get(te.target);
      items.push({
        type: "edge_added",
        id,
        label: `${baseNodes.get(te.source)?.data?.label || te.source} → ${targetNode?.data?.label || te.target}`,
      });
    }
  }

  for (const [id] of baseEdges) {
    if (!targetEdges.has(id)) {
      const be = baseEdges.get(id)!;
      const targetNode = baseNodes.get(be.target);
      items.push({
        type: "edge_removed",
        id,
        label: `${baseNodes.get(be.source)?.data?.label || be.source} → ${targetNode?.data?.label || be.target}`,
      });
    }
  }

  return items;
}

function truncate(str: string, max: number): string {
  return str.length > max ? str.slice(0, max) + "…" : str;
}
