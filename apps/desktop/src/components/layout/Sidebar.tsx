import { useState, useEffect, useRef } from "react";
import {
  ChevronRight,
  PlusCircle,
  Workflow,
  FolderOpen,
  Trash2,
  Download,
  Upload,
  ChevronDown,
} from "lucide-react";
import { NodePalette } from "@/components/palette/NodePalette";
import { ExecutionModeSelector } from "@/components/properties/ExecutionModeSelector";
import { useWorkflowStore } from "@/stores/workflowStore";
import { cn } from "@/lib/utils";
import { workflowsApi } from "@/api/workflows";
import type { Workspace } from "@/types/workflow";

export function Sidebar() {
  const {
    workspaceId,
    workflows,
    activeWorkflowId,
    setActiveWorkflow,
    createWorkflow,
    updateExecutionMode,
    loadWorkflows,
    setWorkspace,
  } = useWorkflowStore();

  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [wsMenuOpen, setWsMenuOpen] = useState(false);
  const [creatingName, setCreatingName] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [creatingWs, setCreatingWs] = useState(false);
  const [wsNameInput, setWsNameInput] = useState("");
  const wsMenuRef = useRef<HTMLDivElement>(null);

  const activeWorkflow = workflows.find((w) => w.id === activeWorkflowId);
  const activeWs = workspaces.find((w) => w.id === workspaceId);

  // Close workspace menu on outside click
  useEffect(() => {
    if (!wsMenuOpen) return;
    const handler = (e: MouseEvent) => {
      if (wsMenuRef.current && !wsMenuRef.current.contains(e.target as Node)) {
        setWsMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [wsMenuOpen]);

  const loadWorkspaces = async () => {
    try {
      const list = await workflowsApi.listWorkspaces();
      setWorkspaces(list);
    } catch {
      // ignore
    }
  };

  const handleCreateWorkflow = async () => {
    if (!creatingName.trim()) return;
    const wf = await createWorkflow(creatingName.trim());
    setActiveWorkflow(wf.id);
    setCreatingName("");
    setShowCreate(false);
  };

  const handleCreateWorkspace = async () => {
    if (!wsNameInput.trim()) return;
    setCreatingWs(true);
    try {
      const ws = await workflowsApi.createWorkspace(wsNameInput.trim());
      setWorkspaces((prev) => [...prev, ws]);
      setWorkspace(ws.id);
      await loadWorkflows(ws.id);
      setWsNameInput("");
      setWsMenuOpen(false);
    } catch {
      // ignore
    } finally {
      setCreatingWs(false);
    }
  };

  const handleSwitchWorkspace = async (wsId: string) => {
    setWorkspace(wsId);
    await loadWorkflows(wsId);
    setWsMenuOpen(false);
  };

  const handleDeleteWorkspace = async (wsId: string) => {
    try {
      await workflowsApi.deleteWorkspace(wsId);
      setWorkspaces((prev) => prev.filter((w) => w.id !== wsId));
      if (workspaceId === wsId) {
        const remaining = workspaces.filter((w) => w.id !== wsId);
        if (remaining.length > 0) {
          await handleSwitchWorkspace(remaining[0].id);
        }
      }
    } catch {
      // ignore
    }
  };

  const handleExportWorkspace = async () => {
    if (!workspaceId) return;
    try {
      const data = await workflowsApi.exportWorkspace(workspaceId);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${activeWs?.name ?? "workspace"}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // ignore
    }
  };

  const handleImportWorkspace = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      try {
        const text = await file.text();
        const data = JSON.parse(text);
        const ws = await workflowsApi.importWorkspace(data);
        setWorkspaces((prev) => [...prev, ws]);
        await handleSwitchWorkspace(ws.id);
      } catch {
        // ignore
      }
    };
    input.click();
  };

  return (
    <div className="flex h-full flex-col w-56 border-r border-border bg-card">
      {/* Workspace switcher */}
      <div className="px-2 py-2 border-b border-border" ref={wsMenuRef}>
        <div className="relative">
          <button
            onClick={() => {
              setWsMenuOpen(!wsMenuOpen);
              if (!wsMenuOpen) loadWorkspaces();
            }}
            className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-xs hover:bg-accent transition-colors"
          >
            <FolderOpen className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
            <span className="truncate flex-1 text-left">{activeWs?.name ?? "Select workspace"}</span>
            <ChevronDown className={cn("h-3 w-3 text-muted-foreground shrink-0 transition-transform", wsMenuOpen && "rotate-180")} />
          </button>

          {wsMenuOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 rounded-md border border-border bg-card shadow-lg z-50 overflow-hidden">
              <div className="max-h-48 overflow-y-auto py-1">
                {workspaces.map((ws) => (
                  <div
                    key={ws.id}
                    className={cn(
                      "flex items-center gap-2 px-2 py-1.5 text-xs hover:bg-accent cursor-pointer",
                      ws.id === workspaceId && "bg-accent font-medium"
                    )}
                  >
                    <button className="flex-1 text-left truncate" onClick={() => handleSwitchWorkspace(ws.id)}>
                      {ws.name}
                    </button>
                    {workspaces.length > 1 && (
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDeleteWorkspace(ws.id); }}
                        className="text-muted-foreground hover:text-destructive transition-colors"
                        title="Delete workspace"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <div className="border-t border-border px-2 py-1.5 flex gap-1">
                <button
                  onClick={handleExportWorkspace}
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors flex-1"
                  title="Export workspace"
                >
                  <Download className="h-3 w-3" /> Export
                </button>
                <button
                  onClick={handleImportWorkspace}
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors flex-1"
                  title="Import workspace"
                >
                  <Upload className="h-3 w-3" /> Import
                </button>
              </div>
              <div className="border-t border-border px-2 py-1.5">
                <div className="flex gap-1">
                  <input
                    className="flex-1 rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
                    placeholder="New workspace…"
                    value={wsNameInput}
                    onChange={(e) => setWsNameInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") handleCreateWorkspace(); }}
                  />
                  <button
                    onClick={handleCreateWorkspace}
                    disabled={creatingWs || !wsNameInput.trim()}
                    className="text-xs rounded-md bg-primary text-primary-foreground px-2 py-1 hover:bg-primary/90 disabled:opacity-50"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Workflows list */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Workflows</span>
        <button onClick={() => setShowCreate(!showCreate)} className="text-muted-foreground hover:text-foreground transition-colors" title="New workflow">
          <PlusCircle className="h-4 w-4" />
        </button>
      </div>

      {showCreate && (
        <div className="flex gap-1 px-2 py-1.5 border-b border-border">
          <input
            autoFocus
            className="flex-1 rounded-md border border-input bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
            placeholder="Workflow name…"
            value={creatingName}
            onChange={(e) => setCreatingName(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleCreateWorkflow(); if (e.key === "Escape") setShowCreate(false); }}
          />
          <button onClick={handleCreateWorkflow} className="text-xs rounded-md bg-primary text-primary-foreground px-2 py-1 hover:bg-primary/90">
            Add
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto py-1">
        {workflows.length === 0 && (
          <p className="px-4 py-3 text-xs text-muted-foreground italic">No workflows yet.</p>
        )}
        {workflows.map((wf) => (
          <button
            key={wf.id}
            onClick={() => setActiveWorkflow(wf.id)}
            className={cn(
              "flex w-full items-center gap-2 px-3 py-2 text-xs text-left hover:bg-accent transition-colors",
              wf.id === activeWorkflowId && "bg-accent text-accent-foreground font-medium"
            )}
          >
            <Workflow className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
            <span className="truncate">{wf.name}</span>
            {wf.id === activeWorkflowId && <ChevronRight className="ml-auto h-3 w-3 shrink-0 text-muted-foreground" />}
          </button>
        ))}
      </div>

      {/* Execution mode */}
      {activeWorkflow && (
        <div className="border-t border-border">
          <div className="px-3 py-1.5">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Execution Mode</span>
          </div>
          <ExecutionModeSelector
            mode={activeWorkflow.execution_mode}
            onChange={updateExecutionMode}
          />
        </div>
      )}

      {/* Node palette */}
      <div className="border-t border-border overflow-y-auto max-h-80">
        <NodePalette />
      </div>
    </div>
  );
}
