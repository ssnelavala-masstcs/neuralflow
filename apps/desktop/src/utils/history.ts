import type { Node, Edge } from "@xyflow/react";

export interface HistoryEntry {
  nodes: Node[];
  edges: Edge[];
}

export class HistoryManager {
  private _past: HistoryEntry[] = [];
  private _future: HistoryEntry[] = [];
  private _maxSize: number;
  private _current: HistoryEntry | null = null;

  constructor(maxSize = 100) {
    this._maxSize = maxSize;
  }

  push(nodes: Node[], edges: Edge[]) {
    const entry: HistoryEntry = {
      nodes: JSON.parse(JSON.stringify(nodes)),
      edges: JSON.parse(JSON.stringify(edges)),
    };

    // Don't push if identical to current
    if (this._current && this._isSame(this._current, entry)) return;

    this._past.push(entry);
    if (this._past.length > this._maxSize) {
      this._past = this._past.slice(-this._maxSize);
    }
    this._future = []; // Clear redo stack on new action
    this._current = entry;
  }

  undo(): HistoryEntry | null {
    if (this._past.length <= 1) return null;
    const current = this._past.pop()!;
    this._future.push(current);
    this._current = this._past[this._past.length - 1];
    return this._current;
  }

  redo(): HistoryEntry | null {
    if (this._future.length === 0) return null;
    const entry = this._future.pop()!;
    this._past.push(entry);
    this._current = entry;
    return this._current;
  }

  get canUndo(): boolean {
    return this._past.length > 1;
  }

  get canRedo(): boolean {
    return this._future.length > 0;
  }

  clear() {
    this._past = [];
    this._future = [];
    this._current = null;
  }

  private _isSame(a: HistoryEntry, b: HistoryEntry): boolean {
    return (
      JSON.stringify(a.nodes) === JSON.stringify(b.nodes) &&
      JSON.stringify(a.edges) === JSON.stringify(b.edges)
    );
  }
}
