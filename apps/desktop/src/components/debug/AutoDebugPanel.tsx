import { useState } from "react";
import { Bug, AlertTriangle, CheckCircle, Lightbulb, Loader2 } from "lucide-react";
import { api } from "@/api/client";

interface DebugReport {
  root_cause: string;
  suggested_fix: string;
  confidence: number;
  details: Record<string, unknown>;
  alternative_fixes: string[];
}

interface AutoDebugPanelProps {
  errorMessage: string;
  nodeType?: string;
  nodeConfig?: Record<string, unknown>;
}

export function AutoDebugPanel({ errorMessage, nodeType, nodeConfig }: AutoDebugPanelProps) {
  const [report, setReport] = useState<DebugReport | null>(null);
  const [loading, setLoading] = useState(false);

  const diagnose = async () => {
    setLoading(true);
    try {
      const data = await api.post<DebugReport>("/api/debug/diagnose", {
        error_message: errorMessage,
        node_type: nodeType,
        node_config: nodeConfig,
      });
      setReport(data);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  if (!errorMessage) return null;

  return (
    <div className="rounded-md border border-border bg-card p-3 space-y-3">
      <div className="flex items-center gap-2">
        <Bug className="h-4 w-4 text-destructive" />
        <span className="text-xs font-semibold">Auto-Debug</span>
        <button
          onClick={diagnose}
          disabled={loading}
          className="ml-auto flex items-center gap-1 rounded bg-primary/10 text-primary px-2 py-0.5 text-[10px] hover:bg-primary/20 disabled:opacity-50"
        >
          {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : "Diagnose"}
        </button>
      </div>

      {report && (
        <div className="space-y-2">
          {/* Root cause */}
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-3.5 w-3.5 text-destructive shrink-0 mt-0.5" />
            <div>
              <p className="text-[10px] font-semibold text-destructive">Root Cause</p>
              <p className="text-[10px] text-muted-foreground">{report.root_cause}</p>
            </div>
          </div>

          {/* Suggested fix */}
          <div className="flex items-start gap-2">
            <CheckCircle className="h-3.5 w-3.5 text-green-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-[10px] font-semibold text-green-500">
                Suggested Fix ({Math.round(report.confidence * 100)}% confidence)
              </p>
              <p className="text-[10px] text-muted-foreground">{report.suggested_fix}</p>
            </div>
          </div>

          {/* Alternative fixes */}
          {report.alternative_fixes.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold text-blue-500 flex items-center gap-1 mb-1">
                <Lightbulb className="h-3 w-3" /> Alternative Fixes
              </p>
              <ul className="space-y-0.5">
                {report.alternative_fixes.map((fix, i) => (
                  <li key={i} className="text-[10px] text-muted-foreground flex items-start gap-1.5">
                    <span className="text-blue-500 mt-0.5">•</span> {fix}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
