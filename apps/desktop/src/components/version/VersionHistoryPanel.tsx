import { useState, useEffect, useCallback } from "react";
import { Clock, RotateCcw, Pencil, Trash2, Check, X, Plus, GitCompare } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  type Snapshot,
  createSnapshot,
  listSnapshots,
  rollbackSnapshot,
  renameSnapshot,
  deleteSnapshot,
} from "@/api/export";
import { WorkflowDiffViewer } from "./WorkflowDiffViewer";
import { useWorkflowStore } from "@/stores/workflowStore";

interface Props {
  workflowId: string | null;
}

export function VersionHistoryPanel({ workflowId }: Props) {
  const { activeWorkflowId, workflows } = useWorkflowStore();
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(false);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [compareMode, setCompareMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [showDiff, setShowDiff] = useState(false);

  const load = useCallback(async () => {
    if (!workflowId) return;
    setLoading(true);
    try {
      const data = await listSnapshots(workflowId);
      setSnapshots(data);
    } finally {
      setLoading(false);
    }
  }, [workflowId]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSaveSnapshot = async () => {
    if (!workflowId) return;
    const name = window.prompt("Snapshot name (optional):") ?? undefined;
    await createSnapshot(workflowId, name || undefined);
    await load();
  };

  const handleRollback = async (snap: Snapshot, index: number) => {
    const label = snap.name ?? `Snapshot ${index + 1}`;
    if (!window.confirm(`Rollback to "${label}"? Current canvas will be replaced.`)) return;
    await rollbackSnapshot(snap.id);
    window.location.reload();
  };

  const startRename = (snap: Snapshot) => {
    setRenamingId(snap.id);
    setRenameValue(snap.name ?? "");
  };

  const commitRename = async (snapId: string) => {
    if (!renameValue.trim()) {
      setRenamingId(null);
      return;
    }
    const updated = await renameSnapshot(snapId, renameValue.trim());
    setSnapshots((prev) => prev.map((s) => (s.id === snapId ? updated : s)));
    setRenamingId(null);
  };

  const handleDelete = async (snapId: string) => {
    await deleteSnapshot(snapId);
    setSnapshots((prev) => prev.filter((s) => s.id !== snapId));
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : prev.length < 2 ? [...prev, id] : [prev[1], id]
    );
  };

  const handleCompare = () => {
    if (selectedIds.length !== 2) return;
    setShowDiff(true);
  };

  // If showing diff, render the diff viewer
  if (showDiff && selectedIds.length === 2) {
    const baseSnap = snapshots.find((s) => s.id === selectedIds[0]);
    const targetSnap = snapshots.find((s) => s.id === selectedIds[1]);
    if (!baseSnap || !targetSnap) return null;

    return (
      <WorkflowDiffViewer
        baseVersion={baseSnap.canvas_data as any}
        targetVersion={targetSnap.canvas_data as any}
        baseLabel={baseSnap.name ?? `v${snapshots.indexOf(baseSnap) + 1}`}
        targetLabel={targetSnap.name ?? `v${snapshots.indexOf(targetSnap) + 1}`}
      />
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border shrink-0">
        <div className="flex items-center gap-1.5">
          <Clock className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-xs font-semibold">Version History</span>
        </div>
        <div className="flex items-center gap-1">
          {compareMode && selectedIds.length === 2 && (
            <button
              onClick={handleCompare}
              className="flex items-center gap-1 rounded-md bg-primary text-primary-foreground px-2 py-1 text-xs font-medium hover:bg-primary/90 transition-colors"
            >
              <GitCompare className="h-3 w-3" />
              Compare
            </button>
          )}
          <button
            onClick={() => { setCompareMode(!compareMode); setSelectedIds([]); setShowDiff(false); }}
            className={cn(
              "flex items-center gap-1 rounded-md border border-border px-2 py-1 text-xs transition-colors",
              compareMode ? "bg-accent text-foreground" : "text-muted-foreground hover:text-foreground"
            )}
          >
            <GitCompare className="h-3 w-3" />
            {compareMode ? "Cancel" : "Diff"}
          </button>
          <button
            onClick={handleSaveSnapshot}
            disabled={!workflowId}
            className="flex items-center gap-1 rounded-md border border-border px-2 py-1 text-xs text-muted-foreground hover:text-foreground hover:bg-accent disabled:opacity-50 transition-colors"
          >
            <Plus className="h-3 w-3" />
            Save
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto">
        {!workflowId && (
          <p className="px-4 py-3 text-xs text-muted-foreground italic">No workflow selected.</p>
        )}
        {workflowId && loading && (
          <p className="px-4 py-3 text-xs text-muted-foreground animate-pulse">Loading…</p>
        )}
        {workflowId && !loading && snapshots.length === 0 && (
          <p className="px-4 py-3 text-xs text-muted-foreground italic">No snapshots yet.</p>
        )}
        {snapshots.map((snap, i) => (
          <div
            key={snap.id}
            className={cn(
              "flex items-center gap-2 border-b border-border px-3 py-2 hover:bg-accent/50 transition-colors group",
              selectedIds.includes(snap.id) && "bg-accent"
            )}
          >
            {compareMode && (
              <input
                type="checkbox"
                checked={selectedIds.includes(snap.id)}
                onChange={() => toggleSelect(snap.id)}
                className="rounded border-input shrink-0"
              />
            )}
            <div className="flex-1 min-w-0">
              {renamingId === snap.id ? (
                <div className="flex items-center gap-1">
                  <input
                    autoFocus
                    className="flex-1 rounded border border-input bg-background px-1.5 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
                    value={renameValue}
                    onChange={(e) => setRenameValue(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") commitRename(snap.id);
                      if (e.key === "Escape") setRenamingId(null);
                    }}
                  />
                  <button
                    onClick={() => commitRename(snap.id)}
                    className="text-green-500 hover:text-green-400 transition-colors"
                  >
                    <Check className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={() => setRenamingId(null)}
                    className="text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              ) : (
                <span className="text-xs truncate block">
                  {snap.name ?? `Snapshot ${i + 1}`}
                </span>
              )}
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-[10px] text-muted-foreground">
                  {new Date(snap.created_at).toLocaleString()}
                </span>
                <span
                  className={cn(
                    "text-[10px] rounded px-1 py-0.5 font-medium",
                    "bg-muted text-muted-foreground"
                  )}
                >
                  {snap.execution_mode}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() => startRename(snap)}
                className="rounded p-1 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                title="Rename"
              >
                <Pencil className="h-3 w-3" />
              </button>
              <button
                onClick={() => handleRollback(snap, i)}
                className="rounded p-1 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                title="Rollback"
              >
                <RotateCcw className="h-3 w-3" />
              </button>
              <button
                onClick={() => handleDelete(snap.id)}
                className="rounded p-1 text-muted-foreground hover:text-destructive hover:bg-accent transition-colors"
                title="Delete"
              >
                <Trash2 className="h-3 w-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
