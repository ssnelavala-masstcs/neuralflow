import { Wifi, WifiOff, Loader2 } from "lucide-react";
import { useSettingsStore } from "@/stores/settingsStore";
import { connectionManager } from "@/utils/connectionManager";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

export function ConnectionStatus() {
  const { connectionStatus } = useSettingsStore();
  const [connState, setConnState] = useState<"connected" | "disconnected" | "reconnecting" | "error">(
    (connectionStatus === "connecting" ? "reconnecting" : connectionStatus) ?? "disconnected"
  );

  useEffect(() => {
    const unsub = connectionManager.onStateChange(setConnState);
    return unsub;
  }, []);

  const config = {
    connected: { icon: Wifi, color: "text-green-500", label: "Connected" },
    reconnecting: { icon: Loader2, color: "text-yellow-500 animate-spin", label: "Reconnecting…" },
    error: { icon: WifiOff, color: "text-red-500", label: "Disconnected" },
    disconnected: { icon: WifiOff, color: "text-muted-foreground", label: "Offline" },
  };

  const { icon: Icon, color, label } = config[connState];

  return (
    <div className={cn("flex items-center gap-1.5 text-xs", color)} title={label}>
      <Icon className="h-3 w-3" />
      <span className="hidden sm:inline">{label}</span>
    </div>
  );
}
