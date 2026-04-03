import { useState, useEffect, useRef, useMemo } from "react";
import { X, Search, Play, Save, Settings, LayoutGrid, Code2, BarChart2, Undo2, Redo2, Plus, Trash2, Globe, PanelRightOpen, Zap, FileDown, Copy, FolderOpen } from "lucide-react";
import { useWorkflowStore } from "@/stores/workflowStore";
import { useRunStore } from "@/stores/runStore";
import { useSettingsStore } from "@/stores/settingsStore";
import { useProviderStore } from "@/stores/providerStore";
import { cn } from "@/lib/utils";

interface Command {
  id: string;
  label: string;
  icon: React.ReactNode;
  shortcut?: string;
  action: () => void;
  section?: string;
}

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
  onShowProperties?: () => void;
  onShowExport?: () => void;
  onShowSettings?: () => void;
  onShowRemoteSettings?: () => void;
  onNavigateTemplates?: () => void;
  onNavigateCost?: () => void;
}

export function CommandPalette({
  open,
  onClose,
  onShowProperties,
  onShowExport,
  onShowSettings,
  onShowRemoteSettings,
  onNavigateTemplates,
  onNavigateCost,
}: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    nodes, edges, activeWorkflowId, workflows, createWorkflow, deleteWorkflow,
    undo, redo, canUndo, canRedo, saveCanvas, validate,
  } = useWorkflowStore();
  const { runStatus } = useRunStore();
  const { sidecarReady } = useSettingsStore();
  const { providers } = useProviderStore();

  const isRunning = runStatus === "running" || runStatus === "queued";

  const commands: Command[] = useMemo(() => [
    {
      id: "run",
      label: "Run Workflow",
      icon: <Play className="h-4 w-4" />,
      shortcut: "Ctrl+Enter",
      action: () => { /* handled by RunModal */ },
      section: "Execution",
    },
    {
      id: "save",
      label: "Save Canvas",
      icon: <Save className="h-4 w-4" />,
      shortcut: "Ctrl+S",
      action: () => saveCanvas(),
      section: "Actions",
    },
    {
      id: "undo",
      label: "Undo",
      icon: <Undo2 className="h-4 w-4" />,
      shortcut: "Ctrl+Z",
      action: () => undo(),
      section: "Edit",
    },
    {
      id: "redo",
      label: "Redo",
      icon: <Redo2 className="h-4 w-4" />,
      shortcut: "Ctrl+Shift+Z",
      action: () => redo(),
      section: "Edit",
    },
    {
      id: "properties",
      label: "Toggle Properties Panel",
      icon: <PanelRightOpen className="h-4 w-4" />,
      shortcut: "Ctrl+P",
      action: () => onShowProperties?.(),
      section: "View",
    },
    {
      id: "export",
      label: "Export Workflow as Code",
      icon: <Code2 className="h-4 w-4" />,
      action: () => onShowExport?.(),
      section: "Actions",
    },
    {
      id: "validate",
      label: "Validate Workflow",
      icon: <Zap className="h-4 w-4" />,
      action: () => validate(),
      section: "Actions",
    },
    {
      id: "templates",
      label: "Browse Templates",
      icon: <LayoutGrid className="h-4 w-4" />,
      action: () => onNavigateTemplates?.(),
      section: "View",
    },
    {
      id: "cost",
      label: "View Cost Dashboard",
      icon: <BarChart2 className="h-4 w-4" />,
      action: () => onNavigateCost?.(),
      section: "View",
    },
    {
      id: "settings",
      label: "Provider Settings",
      icon: <Settings className="h-4 w-4" />,
      action: () => onShowSettings?.(),
      section: "Settings",
    },
    {
      id: "remote",
      label: "Remote Connection Settings",
      icon: <Globe className="h-4 w-4" />,
      action: () => onShowRemoteSettings?.(),
      section: "Settings",
    },
    {
      id: "new-workflow",
      label: "Create New Workflow",
      icon: <Plus className="h-4 w-4" />,
      action: async () => {
        const name = prompt("Workflow name:");
        if (name) await createWorkflow(name);
      },
      section: "Workflows",
    },
    ...workflows.map((wf) => ({
      id: `wf-${wf.id}`,
      label: `Switch to: ${wf.name}`,
      icon: <FolderOpen className="h-4 w-4" />,
      action: () => useWorkflowStore.getState().setActiveWorkflow(wf.id),
      section: "Workflows",
    })),
    ...providers.map((p) => ({
      id: `provider-${p.id}`,
      label: `Provider: ${p.name} (${p.default_model ?? "no model"})`,
      icon: <Settings className="h-4 w-4" />,
      action: () => onShowSettings?.(),
      section: "Providers",
    })),
  ], [saveCanvas, undo, redo, validate, onShowProperties, onShowExport, onNavigateTemplates, onNavigateCost, onShowSettings, onShowRemoteSettings, createWorkflow, workflows, providers, sidecarReady, isRunning]);

  const filtered = useMemo(() => {
    if (!query) return commands;
    const q = query.toLowerCase();
    return commands.filter((c) => c.label.toLowerCase().includes(q));
  }, [commands, query]);

  useEffect(() => {
    if (open) {
      setQuery("");
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((i) => Math.min(i + 1, filtered.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter" && filtered[selectedIndex]) {
        e.preventDefault();
        filtered[selectedIndex].action();
        onClose();
      } else if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open, filtered, selectedIndex, onClose]);

  if (!open) return null;

  const sections = useMemo(() => {
    const map = new Map<string, Command[]>();
    for (const cmd of filtered) {
      const section = cmd.section ?? "General";
      if (!map.has(section)) map.set(section, []);
      map.get(section)!.push(cmd);
    }
    return map;
  }, [filtered]);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]" onClick={onClose}>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative z-10 w-full max-w-lg overflow-hidden rounded-lg border border-border bg-card shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search input */}
        <div className="flex items-center gap-2 border-b border-border px-3 py-3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => { setQuery(e.target.value); setSelectedIndex(0); }}
            placeholder="Type a command or search..."
            className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
          />
          {query && (
            <button onClick={() => setQuery("")} className="text-muted-foreground hover:text-foreground">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Results */}
        <div className="max-h-80 overflow-y-auto p-2">
          {filtered.length === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">No commands found.</p>
          )}
          {Array.from(sections.entries()).map(([section, cmds]) => (
            <div key={section} className="mb-2">
              <p className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{section}</p>
              {cmds.map((cmd) => {
                const globalIndex = filtered.findIndex((c) => c.id === cmd.id);
                return (
                  <button
                    key={cmd.id}
                    onClick={() => { cmd.action(); onClose(); }}
                    onMouseEnter={() => setSelectedIndex(globalIndex)}
                    className={cn(
                      "flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm transition-colors",
                      globalIndex === selectedIndex ? "bg-accent text-accent-foreground" : "text-foreground hover:bg-accent/50"
                    )}
                  >
                    {cmd.icon}
                    <span className="flex-1 text-left">{cmd.label}</span>
                    {cmd.shortcut && (
                      <kbd className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">
                        {cmd.shortcut}
                      </kbd>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="border-t border-border px-3 py-2 text-[10px] text-muted-foreground flex items-center gap-3">
          <span><kbd className="rounded bg-muted px-1">↑↓</kbd> Navigate</span>
          <span><kbd className="rounded bg-muted px-1">↵</kbd> Select</span>
          <span><kbd className="rounded bg-muted px-1">Esc</kbd> Close</span>
        </div>
      </div>
    </div>
  );
}
