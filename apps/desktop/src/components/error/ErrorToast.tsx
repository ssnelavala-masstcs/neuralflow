import { useEffect } from "react";
import { X, AlertTriangle, AlertCircle, Info } from "lucide-react";
import { useErrorStore } from "@/stores/errorStore";
import { cn } from "@/lib/utils";

const SEVERITY_ICONS = {
  critical: AlertTriangle,
  warning: AlertCircle,
  info: Info,
};

const SEVERITY_COLORS = {
  critical: "border-destructive bg-destructive/10 text-destructive",
  warning: "border-yellow-500/50 bg-yellow-500/10 text-yellow-500",
  info: "border-blue-500/50 bg-blue-500/10 text-blue-500",
};

export function ErrorToast() {
  const { errors, dismissError, dismissAll } = useErrorStore();

  useEffect(() => {
    if (errors.length === 0) return;
    const timers = errors.map((err) => {
      if (err.severity !== "critical") {
        return setTimeout(() => dismissError(err.id), 8000);
      }
      return null;
    });
    return () => timers.forEach((t) => t && clearTimeout(t));
  }, [errors, dismissError]);

  if (errors.length === 0) return null;

  return (
    <div className="fixed bottom-20 right-4 z-50 flex max-h-80 flex-col gap-2 overflow-y-auto">
      {errors.slice(-5).map((err) => {
        const Icon = SEVERITY_ICONS[err.severity];
        return (
          <div
            key={err.id}
            className={cn(
              "flex max-w-sm items-start gap-3 rounded-md border p-3 shadow-lg",
              SEVERITY_COLORS[err.severity]
            )}
          >
            <Icon className="mt-0.5 h-4 w-4 shrink-0" />
            <div className="flex-1 text-sm">
              <p className="font-medium">{err.message}</p>
              {err.recovery_hint && (
                <p className="mt-1 text-xs opacity-80">{err.recovery_hint}</p>
              )}
            </div>
            <button
              onClick={() => dismissError(err.id)}
              className="shrink-0 opacity-60 hover:opacity-100"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        );
      })}
      {errors.length > 1 && (
        <button
          onClick={dismissAll}
          className="rounded bg-muted px-3 py-1 text-xs text-muted-foreground hover:text-foreground"
        >
          Dismiss all ({errors.length})
        </button>
      )}
    </div>
  );
}
