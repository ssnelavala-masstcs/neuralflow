import { useState, useEffect, useCallback } from "react";
import { Play, Settings, Cpu, StopCircle, Code2, PanelRightOpen, PanelRightClose, LayoutGrid, Globe, Undo2, Redo2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Sidebar } from "./Sidebar";
import { BottomPanel } from "./BottomPanel";
import { Canvas } from "@/canvas/Canvas";
import { RunModal } from "@/components/run/RunModal";
import { ExportModal } from "@/components/export/ExportModal";
import { PropertiesPanel } from "@/components/properties/PropertiesPanel";
import { ProviderSettingsModal } from "@/components/settings/ProviderSettingsModal";
import { RemoteConnectionSettings } from "@/components/settings/RemoteConnectionSettings";
import { ErrorToast } from "@/components/error/ErrorToast";
import { CommandPalette } from "@/components/palette/CommandPalette";
import { ConnectionStatus } from "@/components/connection/ConnectionStatus";
import { NotificationCenter } from "@/components/notifications/NotificationCenter";
import { connectionManager } from "@/utils/connectionManager";
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
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const { loadWorkflows, activeWorkflowId, workflows, undo, redo, canUndo, canRedo, validate } = useWorkflowStore();
  const { runStatus, cancelRun } = useRunStore();
  const { sidecarReady, setSidecarReady, connectionStatus } = useSettingsStore();

  // Start connection manager
  useEffect(() => {
    connectionManager.start();
    return () => connectionManager.stop();
  }, []);

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
      { key: "k", ctrl: true, handler: () => setShowCommandPalette((s) => !s) },
      { key: "z", ctrl: true, handler: () => { undo(); } },
      { key: "z", ctrl: true, shift: true, handler: () => { redo(); } },
      { key: "Escape", handler: () => { if (showCommandPalette) setShowCommandPalette(false); if (showProperties) setShowProperties(false); if (showExportModal) setShowExportModal(false); } },
    ],
  });

  const isRunning = runStatus === "running" || runStatus === "queued";
  const activeWorkflow = workflows.find((w) => w.id === activeWorkflowId);

  return (
    <div className="flex h-full flex-col bg-background overflow-hidden">
      {/* Title bar */}
      <header className="relative z-20 flex h-10 items-center gap-2 border-b border-border px-3 shrink-0 bg-card">
        <Cpu className="h-4 w-4 text-primary" />
        <span className="text-sm font-semibold">NeuralFlow</span>
        {activeWorkflow && (
          <>
            <span className="text-muted-foreground mx-1">/</span>
            <span className="text-sm text-muted-foreground truncate max-w-xs">{activeWorkflow.name}</span>
          </>
        )}

        <div className="ml-auto flex items-center gap-2">
          <ConnectionStatus />
          {!sidecarReady && (
            <span className="text-xs text-yellow-500 animate-pulse">Connecting to sidecar…</span>
          )}
          <button
            onClick={() => undo()}
            disabled={!canUndo}
            className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            title="Undo (Ctrl+Z)"
          >
            <Undo2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => redo()}
            disabled={!canRedo}
            className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            title="Redo (Ctrl+Shift+Z)"
          >
            <Redo2 className="h-4 w-4" />
          </button>
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
          <NotificationCenter />
        </div>
      </header>

      {/* Main layout */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden min-w-0">
          {/* Canvas */}
          <div className="flex-1 overflow-hidden min-w-0">
            <Canvas onNodeSelect={() => setShowProperties(true)} />
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
      <ErrorToast />
      <CommandPalette
        open={showCommandPalette}
        onClose={() => setShowCommandPalette(false)}
        onShowProperties={() => setShowProperties(true)}
        onShowExport={() => setShowExportModal(true)}
        onShowSettings={() => setShowProviderSettings(true)}
        onShowRemoteSettings={() => setShowRemoteSettings(true)}
      />
    </div>
  );
}
