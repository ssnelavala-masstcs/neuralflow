import { useState, useEffect } from "react";
import { Play, Settings, Cpu, StopCircle } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { BottomPanel } from "./BottomPanel";
import { Canvas } from "@/canvas/Canvas";
import { RunModal } from "@/components/run/RunModal";
import { useWorkflowStore } from "@/stores/workflowStore";
import { useRunStore } from "@/stores/runStore";
import { useSettingsStore } from "@/stores/settingsStore";
import { workflowsApi } from "@/api/workflows";

const DEFAULT_WORKSPACE_ID = "default";

export function AppShell() {
  const [runModalOpen, setRunModalOpen] = useState(false);
  const { loadWorkflows, activeWorkflowId, workflows } = useWorkflowStore();
  const { runStatus, cancelRun } = useRunStore();
  const { sidecarReady, setSidecarReady } = useSettingsStore();

  // Bootstrap: ensure default workspace + load workflows
  useEffect(() => {
    async function init() {
      try {
        // Ensure default workspace exists
        const workspaces = await workflowsApi.listWorkspaces();
        let wsId = workspaces[0]?.id ?? null;
        if (!wsId) {
          const ws = await workflowsApi.createWorkspace("My Workspace");
          wsId = ws.id;
        }
        await loadWorkflows(wsId);
        setSidecarReady(true);
      } catch {
        // Sidecar not yet up — retry
        setTimeout(init, 1000);
      }
    }
    init();
  }, []);

  const isRunning = runStatus === "running" || runStatus === "queued";
  const activeWorkflow = workflows.find((w) => w.id === activeWorkflowId);

  return (
    <div className="flex h-screen flex-col bg-background overflow-hidden">
      {/* Title bar */}
      <header className="flex h-10 items-center gap-2 border-b border-border px-3 shrink-0 bg-card">
        <Cpu className="h-4 w-4 text-primary" />
        <span className="text-sm font-semibold">NeuralFlow</span>
        {activeWorkflow && (
          <>
            <span className="text-muted-foreground mx-1">/</span>
            <span className="text-sm text-muted-foreground truncate max-w-xs">{activeWorkflow.name}</span>
          </>
        )}

        <div className="ml-auto flex items-center gap-2">
          {!sidecarReady && (
            <span className="text-xs text-yellow-500 animate-pulse">Connecting to sidecar…</span>
          )}
          {isRunning ? (
            <button
              onClick={cancelRun}
              className="flex items-center gap-1.5 rounded-md bg-destructive text-destructive-foreground px-3 py-1.5 text-xs font-medium hover:bg-destructive/90 transition-colors"
            >
              <StopCircle className="h-3.5 w-3.5" />
              Stop
            </button>
          ) : (
            <button
              onClick={() => setRunModalOpen(true)}
              disabled={!activeWorkflowId || !sidecarReady}
              className="flex items-center gap-1.5 rounded-md bg-primary text-primary-foreground px-3 py-1.5 text-xs font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              <Play className="h-3.5 w-3.5" />
              Run
            </button>
          )}
          <button className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors" title="Settings">
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </header>

      {/* Main layout */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Canvas */}
          <div className="flex-1 overflow-hidden">
            <Canvas />
          </div>
          {/* Bottom panel */}
          <div className="h-52 border-t border-border shrink-0">
            <BottomPanel />
          </div>
        </div>
      </div>

      <RunModal open={runModalOpen} onClose={() => setRunModalOpen(false)} />
    </div>
  );
}
