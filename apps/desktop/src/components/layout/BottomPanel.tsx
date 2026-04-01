import { useState } from "react";
import { RunLog } from "@/components/run/RunLog";

type Tab = "log" | "history";

export function BottomPanel() {
  const [tab, setTab] = useState<Tab>("log");

  return (
    <div className="h-full flex flex-col">
      <div className="flex border-b border-border shrink-0">
        {(["log", "history"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-xs font-medium capitalize transition-colors ${
              tab === t ? "border-b-2 border-primary text-foreground" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {t === "log" ? "Run Log" : "History"}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-hidden">
        {tab === "log" && <RunLog />}
        {tab === "history" && (
          <div className="p-4 text-xs text-muted-foreground italic">Run history coming soon.</div>
        )}
      </div>
    </div>
  );
}
