import { useState } from "react";
import { RunLog } from "@/components/run/RunLog";
import { RunHistoryPanel } from "@/components/debug/RunHistoryPanel";
import { VersionHistoryPanel } from "@/components/version/VersionHistoryPanel";
import { useWorkflowStore } from "@/stores/workflowStore";

type Tab = "log" | "history" | "debug" | "versions";

const TAB_LABELS: Record<Tab, string> = {
  log: "Run Log",
  history: "History",
  debug: "Debug",
  versions: "Version History",
};

export function BottomPanel() {
  const [tab, setTab] = useState<Tab>("log");
  const activeWorkflowId = useWorkflowStore((s) => s.activeWorkflowId);

  return (
    <div className="h-full flex flex-col">
      <div className="flex border-b border-border shrink-0">
        {(["log", "history", "debug", "versions"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-xs font-medium capitalize transition-colors ${
              tab === t ? "border-b-2 border-primary text-foreground" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {TAB_LABELS[t]}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-hidden">
        {tab === "log" && <RunLog />}
        {tab === "history" && (
          <div className="p-4 text-xs text-muted-foreground italic">Run history coming soon.</div>
        )}
        {tab === "debug" && <RunHistoryPanel workflowId={activeWorkflowId} />}
        {tab === "versions" && <VersionHistoryPanel workflowId={activeWorkflowId} />}
      </div>
    </div>
  );
}
