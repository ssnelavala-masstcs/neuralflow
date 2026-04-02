import { useState, useEffect } from "react";
import { Code2, Copy, Check, Download, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { exportCrewAI, exportLangGraph, downloadPythonFile } from "@/api/export";

type ExportTab = "crewai" | "langgraph";

interface Props {
  workflowId: string;
  onClose: () => void;
}

export function ExportModal({ workflowId, onClose }: Props) {
  const [tab, setTab] = useState<ExportTab>("crewai");
  const [code, setCode] = useState<string | null>(null);
  const [filename, setFilename] = useState("export.py");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setCode(null);
    setLoading(true);
    const fetcher = tab === "crewai" ? exportCrewAI : exportLangGraph;
    fetcher(workflowId)
      .then(({ code: c, filename: f }) => {
        setCode(c);
        setFilename(f);
      })
      .finally(() => setLoading(false));
  }, [tab, workflowId]);

  const handleCopy = async () => {
    if (!code) return;
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!code) return;
    downloadPythonFile(code, filename);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="relative flex flex-col w-[680px] max-h-[80vh] rounded-lg border border-border bg-background shadow-xl">
        {/* Header */}
        <div className="flex items-center gap-2 border-b border-border px-4 py-3 shrink-0">
          <Code2 className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold">Export Code</span>
          <button
            onClick={onClose}
            className="ml-auto rounded-md p-1 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border shrink-0">
          {(["crewai", "langgraph"] as ExportTab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={cn(
                "px-4 py-2 text-xs font-medium transition-colors capitalize",
                tab === t
                  ? "border-b-2 border-primary text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {t === "crewai" ? "CrewAI" : "LangGraph"}
            </button>
          ))}
        </div>

        {/* Code area */}
        <div className="flex-1 overflow-hidden p-4 min-h-0">
          {loading ? (
            <div className="flex h-full items-center justify-center">
              <span className="text-xs text-muted-foreground animate-pulse">Loading…</span>
            </div>
          ) : (
            <pre className="h-full overflow-auto rounded-md bg-muted p-3 text-xs font-mono max-h-96 whitespace-pre">
              {code ?? ""}
            </pre>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 border-t border-border px-4 py-3 shrink-0">
          <button
            onClick={handleCopy}
            disabled={!code}
            className="flex items-center gap-1.5 rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium hover:bg-accent disabled:opacity-50 transition-colors"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? "Copied!" : "Copy"}
          </button>
          <button
            onClick={handleDownload}
            disabled={!code}
            className="flex items-center gap-1.5 rounded-md bg-primary text-primary-foreground px-3 py-1.5 text-xs font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            <Download className="h-3.5 w-3.5" />
            Download .py
          </button>
        </div>
      </div>
    </div>
  );
}
