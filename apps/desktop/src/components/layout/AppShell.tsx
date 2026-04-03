import { useState, useEffect } from "react";
import { Play, Settings, Cpu, StopCircle, Code2, PanelRightOpen, PanelRightClose, LayoutGrid, Globe } from "lucide-react";
import { cn } from "@/lib/utils";
import { Sidebar } from "./Sidebar";
import { BottomPanel } from "./BottomPanel";
import { Canvas } from "@/canvas/Canvas";
import { RunModal } from "@/components/run/RunModal";
import { ExportModal } from "@/components/export/ExportModal";
import { PropertiesPanel } from "@/components/properties/PropertiesPanel";
import { ProviderSettingsModal } from "@/components/settings/ProviderSettingsModal";
import { RemoteConnectionSettings } from "@/components/settings/RemoteConnectionSettings";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { useWorkflowStore } from "@/stores/workflowStore";
import { useRunStore } from "@/stores/runStore";
import { useSettingsStore } from "@/stores/settingsStore";
import { workflowsApi } from "@/api/workflows";

const DEFAULT_WORKSPACE_ID = "default";

interface AppShellProps {
  onNavigateTemplates?: () => void;
}

export function AppShell({ onNavigateTemplates }: AppShellProps) {
  const [runModalOpen, setRunModalOpen] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showProviderSettings, setShowProviderSettings] = useState(false);
  const [showProperties, setShowProperties] = useState(false);
  const [showRemoteSettings, setShowRemoteSettings] = useState(false);
  const { loadWorkflows, activeWorkflowId, workflows } = useWorkflowStore();
  const { runStatus, cancelRun } = useRunStore();
  const { sidecarReady, setSidecarReady, connectionStatus } = useSettingsStore();

  // Bootstrap: ensure default workspace + load workflows
  useEffect(() => {
    async function init() {
      try {
        const workspaces = await workflowsApi.listWorkspaces();
        let wsId = workspaces[0]?.id ?? null;
        if (!wsId) {
          const ws = await workflowsApi.createWorkspace("My Workspace");
          wsId = ws.id;
        }
        await loadWorkflows(wsId);
        setSidecarReady(true);
      } catch {
        setTimeout(init, 1000);
      }
    }
    init();
  }, []);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    shortcuts: [
      { key: "Enter", ctrl: true, handler: () => { if (activeWorkflowId && sidecarReady && !isRunning) setRunModalOpen(true); } },
      { key: "s", ctrl: true, handler: () => { /* save handled by PropertiesPanel */ } },
      { key: "p", ctrl: true, handler: () => setShowProperties((s) => !s) },
      { key: "Escape", handler: () => { if (showProperties) setShowProperties(false); if (showExportModal) setShowExportModal(false); } },
    ],
  });

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
          {connectionStatus === "connected" && (
            <span className="text-xs text-green-500 flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
              Remote
            </span>
          )}
          {connectionStatus === "error" && (
            <span className="text-xs text-red-500 flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
              Remote error
            </span>
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
          <button
            onClick={() => setShowExportModal(true)}
            disabled={!activeWorkflowId}
            className="flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-accent disabled:opacity-50 transition-colors"
            title="Export code"
          >
            <Code2 className="h-3.5 w-3.5" />
            Export
          </button>
          <button
            onClick={() => onNavigateTemplates?.()}
            className="flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            title="Browse templates"
          >
            <LayoutGrid className="h-3.5 w-3.5" />
            Templates
          </button>
          <button
            onClick={() => setShowProperties(!showProperties)}
            className={cn(
              "flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-xs font-medium transition-colors",
              showProperties ? "bg-accent text-foreground border-primary" : "text-muted-foreground hover:text-foreground hover:bg-accent"
            )}
            title="Toggle properties panel"
          >
            {showProperties ? <PanelRightClose className="h-3.5 w-3.5" /> : <PanelRightOpen className="h-3.5 w-3.5" />}
            Properties
          </button>
          <button
            onClick={() => setShowProviderSettings(true)}
            className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            title="Settings"
          >
            <Settings className="h-4 w-4" />
          </button>
          <button
            onClick={() => setShowRemoteSettings(true)}
            className={cn(
              "rounded-md p-1.5 transition-colors",
              connectionStatus === "connected"
                ? "text-green-500 hover:bg-accent"
                : "text-muted-foreground hover:text-foreground hover:bg-accent"
            )}
            title="Remote Connection"
          >
            <Globe className="h-4 w-4" />
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
        {/* Right sidebar: Properties Panel */}
        {showProperties && <PropertiesPanel onClose={() => setShowProperties(false)} />}
      </div>

      <RunModal open={runModalOpen} onClose={() => setRunModalOpen(false)} />
      {showExportModal && activeWorkflowId && (
        <ExportModal workflowId={activeWorkflowId} onClose={() => setShowExportModal(false)} />
      )}
      <ProviderSettingsModal open={showProviderSettings} onClose={() => setShowProviderSettings(false)} />
      <RemoteConnectionSettings open={showRemoteSettings} onClose={() => setShowRemoteSettings(false)} />
    </div>
  );
}
