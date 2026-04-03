import { useState } from "react";
import { Globe, Loader2, Plug, PlugZap, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSettingsStore } from "@/stores/settingsStore";
import { api, ApiError } from "@/api/client";

interface RemoteConnectionSettingsProps {
  open: boolean;
  onClose: () => void;
}

export function RemoteConnectionSettings({ open, onClose }: RemoteConnectionSettingsProps) {
  const {
    remoteSidecarUrl,
    remoteAuthToken,
    connectionStatus,
    setRemoteSidecarUrl,
    setRemoteAuthToken,
    setConnectionStatus,
  } = useSettingsStore();

  const [urlInput, setUrlInput] = useState(remoteSidecarUrl ?? "");
  const [tokenInput, setTokenInput] = useState(remoteAuthToken ?? "");
  const [testing, setTesting] = useState(false);

  if (!open) return null;

  const handleTestConnection = async () => {
    setTesting(true);
    setConnectionStatus("connecting");
    try {
      // Temporarily set the store values so the API client uses them
      setRemoteSidecarUrl(urlInput || null);
      setRemoteAuthToken(tokenInput || null);
      await api.get<{ status: string }>("/api/health");
      setConnectionStatus("connected");
    } catch (err) {
      setConnectionStatus("error");
    } finally {
      setTesting(false);
    }
  };

  const handleSave = () => {
    setRemoteSidecarUrl(urlInput || null);
    setRemoteAuthToken(tokenInput || null);
    onClose();
  };

  const handleDisconnect = () => {
    setRemoteSidecarUrl(null);
    setRemoteAuthToken(null);
    setUrlInput("");
    setTokenInput("");
    setConnectionStatus("disconnected");
    onClose();
  };

  const status = connectionStatus as "disconnected" | "connecting" | "connected" | "error";

  const statusIcon: Record<string, React.ReactNode> = {
    disconnected: <Plug className="h-4 w-4 text-muted-foreground" />,
    connecting: <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />,
    connected: <PlugZap className="h-4 w-4 text-green-500" />,
    error: <X className="h-4 w-4 text-red-500" />,
  };

  const statusLabel: Record<string, string> = {
    disconnected: "Disconnected",
    connecting: "Connecting…",
    connected: "Connected",
    error: "Connection failed",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-96 rounded-lg border border-border bg-card shadow-xl">
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <div className="flex items-center gap-2">
            <Globe className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-semibold">Remote Connection</h3>
          </div>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Status indicator */}
          <div className="flex items-center gap-2 rounded-md border border-border px-3 py-2">
            {statusIcon[status]}
            <span className="text-xs font-medium">{statusLabel[status]}</span>
            {status === "connected" && (
              <button onClick={handleDisconnect} className="ml-auto text-xs text-muted-foreground hover:text-destructive transition-colors">
                Disconnect
              </button>
            )}
          </div>

          <div>
            <label className="block text-xs text-muted-foreground mb-1">Sidecar URL</label>
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="http://remote-host:7411"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs text-muted-foreground mb-1">Auth Token (optional)</label>
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="nf_..."
              type="password"
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleTestConnection}
              disabled={testing || !urlInput.trim()}
              className="flex items-center gap-1.5 rounded-md border border-border px-3 py-2 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-accent disabled:opacity-50 transition-colors"
            >
              {testing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Plug className="h-3.5 w-3.5" />}
              Test
            </button>
            <button
              onClick={handleSave}
              className="flex-1 rounded-md bg-primary text-primary-foreground px-3 py-2 text-xs font-medium hover:bg-primary/90 transition-colors"
            >
              Save & Connect
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
