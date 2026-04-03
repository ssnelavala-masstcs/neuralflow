import { useState, useEffect } from "react";
import { Bell, BellOff, Check, Trash2, X, AlertTriangle, AlertCircle, Info, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/api/client";

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: "info" | "warning" | "critical";
  data: Record<string, unknown>;
  timestamp: number;
  read: boolean;
}

export function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await api.get<{ notifications: Notification[]; unread_count: number }>("/api/notifications");
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch {
      // Notifications endpoint may not be available
    }
  };

  const markRead = async (id: string) => {
    try {
      await api.post(`/api/notifications/${id}/read`);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch { /* ignore */ }
  };

  const markAllRead = async () => {
    try {
      await api.post("/api/notifications/read-all");
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch { /* ignore */ }
  };

  const clearAll = async () => {
    try {
      await api.delete("/api/notifications");
      setNotifications([]);
      setUnreadCount(0);
    } catch { /* ignore */ }
  };

  const SEVERITY_ICONS = {
    critical: AlertTriangle,
    warning: AlertCircle,
    info: Info,
  };

  const formatTime = (ts: number) => {
    const diff = Date.now() / 1000 - ts;
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return new Date(ts * 1000).toLocaleDateString();
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="relative rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
        title="Notifications"
      >
        {unreadCount > 0 ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-destructive text-[9px] font-bold text-destructive-foreground">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-8 z-50 w-80 rounded-lg border border-border bg-card shadow-xl">
            <div className="flex items-center justify-between border-b border-border px-3 py-2">
              <h3 className="text-sm font-semibold">Notifications</h3>
              <div className="flex items-center gap-1">
                {unreadCount > 0 && (
                  <button onClick={markAllRead} className="rounded p-1 text-xs text-muted-foreground hover:text-foreground" title="Mark all read">
                    <Check className="h-3 w-3" />
                  </button>
                )}
                <button onClick={clearAll} className="rounded p-1 text-xs text-muted-foreground hover:text-destructive" title="Clear all">
                  <Trash2 className="h-3 w-3" />
                </button>
                <button onClick={() => setOpen(false)} className="rounded p-1 text-xs text-muted-foreground hover:text-foreground">
                  <X className="h-3 w-3" />
                </button>
              </div>
            </div>
            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 && (
                <p className="py-8 text-center text-xs text-muted-foreground">No notifications</p>
              )}
              {notifications.map((n) => {
                const Icon = SEVERITY_ICONS[n.severity];
                return (
                  <div
                    key={n.id}
                    className={cn(
                      "border-b border-border px-3 py-2.5 text-xs transition-colors",
                      !n.read ? "bg-accent/50" : ""
                    )}
                  >
                    <div className="flex items-start gap-2">
                      <Icon className={cn("mt-0.5 h-3.5 w-3.5 shrink-0", {
                        "text-destructive": n.severity === "critical",
                        "text-yellow-500": n.severity === "warning",
                        "text-blue-500": n.severity === "info",
                      })} />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium">{n.title}</p>
                        <p className="text-muted-foreground mt-0.5">{n.message}</p>
                        <p className="text-[10px] text-muted-foreground mt-1">{formatTime(n.timestamp)}</p>
                      </div>
                      {!n.read && (
                        <button onClick={() => markRead(n.id)} className="shrink-0 text-muted-foreground hover:text-foreground">
                          <CheckCircle className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
