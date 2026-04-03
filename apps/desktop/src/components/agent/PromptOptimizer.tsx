import { useState } from "react";
import { Wand2, AlertTriangle, CheckCircle, Lightbulb, Copy } from "lucide-react";
import { api } from "@/api/client";
import { cn } from "@/lib/utils";

interface PromptAnalysisResult {
  score: number;
  issues: string[];
  suggestions: string[];
  optimized_prompt: string | null;
}

interface PromptOptimizerProps {
  prompt: string;
  onChange?: (newPrompt: string) => void;
}

export function PromptOptimizer({ prompt, onChange }: PromptOptimizerProps) {
  const [result, setResult] = useState<PromptAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    setLoading(true);
    try {
      const data = await api.post<PromptAnalysisResult>("/api/prompt/analyze", { prompt });
      setResult(data);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  const applyOptimized = () => {
    if (result?.optimized_prompt && onChange) {
      onChange(result.optimized_prompt);
    }
  };

  const scoreColor = result
    ? result.score >= 80 ? "text-green-500"
    : result.score >= 50 ? "text-yellow-500"
    : "text-red-500"
    : "";

  return (
    <div className="space-y-3">
      <button
        onClick={analyze}
        disabled={loading || !prompt.trim()}
        className="flex items-center gap-1.5 rounded-md bg-primary/10 text-primary px-3 py-1.5 text-xs font-medium hover:bg-primary/20 disabled:opacity-50 transition-colors"
      >
        {loading ? (
          <>Analyzing…</>
        ) : (
          <><Wand2 className="h-3.5 w-3.5" /> Analyze Prompt</>
        )}
      </button>

      {result && (
        <div className="rounded-md border border-border bg-card p-3 space-y-3">
          {/* Score */}
          <div className="flex items-center gap-2">
            <span className={cn("text-lg font-bold", scoreColor)}>{result.score}/100</span>
            <span className="text-xs text-muted-foreground">Prompt Quality Score</span>
          </div>

          {/* Issues */}
          {result.issues.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-destructive mb-1 flex items-center gap-1">
                <AlertTriangle className="h-3 w-3" /> Issues ({result.issues.length})
              </h4>
              <ul className="space-y-1">
                {result.issues.map((issue, i) => (
                  <li key={i} className="text-[10px] text-muted-foreground flex items-start gap-1.5">
                    <span className="text-destructive mt-0.5">•</span> {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggestions */}
          {result.suggestions.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-blue-500 mb-1 flex items-center gap-1">
                <Lightbulb className="h-3 w-3" /> Suggestions ({result.suggestions.length})
              </h4>
              <ul className="space-y-1">
                {result.suggestions.map((s, i) => (
                  <li key={i} className="text-[10px] text-muted-foreground flex items-start gap-1.5">
                    <CheckCircle className="h-3 w-3 text-blue-500 shrink-0 mt-0.5" /> {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Apply optimized version */}
          {result.optimized_prompt && (
            <button
              onClick={applyOptimized}
              className="flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-xs text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              <Copy className="h-3 w-3" />
              Apply Optimized Version
            </button>
          )}
        </div>
      )}
    </div>
  );
}
