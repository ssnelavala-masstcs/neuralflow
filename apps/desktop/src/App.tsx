import { useState } from "react";
import { ReactFlowProvider } from "@xyflow/react";
import { BarChart2, Workflow, LayoutGrid } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { CostDashboard } from "@/components/cost/CostDashboard";
import { TemplateGallery } from "@/components/sharing/TemplateGallery";
import { ErrorBoundary } from "@/components/error/ErrorBoundary";
import { cn } from "@/lib/utils";

type View = "canvas" | "cost" | "templates";

const TABS: Array<{ id: View; label: string; icon: React.ReactNode }> = [
  { id: "canvas", label: "Canvas", icon: <Workflow className="h-3.5 w-3.5" /> },
  { id: "templates", label: "Templates", icon: <LayoutGrid className="h-3.5 w-3.5" /> },
  { id: "cost", label: "Cost", icon: <BarChart2 className="h-3.5 w-3.5" /> },
];

export default function App() {
  const [view, setView] = useState<View>("canvas");

  return (
    <ReactFlowProvider>
      <div className="flex h-screen flex-col bg-background overflow-hidden">
        {/* View switcher strip */}
        <div className="flex items-center gap-1 border-b border-border bg-card px-2 shrink-0 h-8">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setView(tab.id)}
              className={cn(
                "flex items-center gap-1.5 rounded px-2.5 py-1 text-xs font-medium transition-colors",
                view === tab.id
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Views */}
        <div className="flex-1 overflow-hidden">
          <ErrorBoundary>
            {view === "canvas" && <AppShell onNavigateTemplates={() => setView("templates")} />}
            {view === "templates" && <TemplateGallery />}
            {view === "cost" && <CostDashboard />}
          </ErrorBoundary>
        </div>
      </div>
    </ReactFlowProvider>
  );
}
