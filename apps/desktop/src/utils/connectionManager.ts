import { useErrorStore } from "@/stores/errorStore";
import { useSettingsStore } from "@/stores/settingsStore";

const PING_INTERVAL_MS = 5000;
const MAX_RETRIES = 5;
const BASE_BACKOFF_MS = 1000;

type ConnectionState = "connected" | "disconnected" | "reconnecting" | "error";

interface QueuedRequest {
  path: string;
  init?: RequestInit;
  resolve: (value: unknown) => void;
  reject: (reason: unknown) => void;
}

export class ConnectionManager {
  private _state: ConnectionState = "disconnected";
  private _pingTimer: ReturnType<typeof setInterval> | null = null;
  private _retryCount = 0;
  private _queue: QueuedRequest[] = [];
  private _listeners: Set<(state: ConnectionState) => void> = new Set();

  get state(): ConnectionState {
    return this._state;
  }

  start() {
    this._state = "reconnecting";
    this._notify();
    this._startPing();
  }

  stop() {
    if (this._pingTimer) clearInterval(this._pingTimer);
    this._pingTimer = null;
    this._state = "disconnected";
    this._notify();
  }

  onStateChange(listener: (state: ConnectionState) => void): () => void {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  /** Wrap a fetch call with reconnection logic. */
  async request<T>(path: string, init?: RequestInit): Promise<T> {
    if (this._state === "disconnected") {
      this.start();
    }

    return new Promise<T>((resolve, reject) => {
      this._queue.push({
        path,
        init,
        resolve: resolve as (value: unknown) => void,
        reject,
      });
      this._flushQueue();
    });
  }

  private async _flushQueue() {
    if (this._state !== "connected" || this._queue.length === 0) return;

    const queue = [...this._queue];
    this._queue = [];

    for (const req of queue) {
      try {
        const baseUrl = this._getBaseUrl();
        const res = await fetch(`${baseUrl}${req.path}`, {
          headers: {
            "Content-Type": "application/json",
            ...this._getAuthHeaders(),
            ...(req.init?.headers ?? {}),
          },
          ...req.init,
        });
        if (!res.ok) {
          const text = await res.text().catch(() => res.statusText);
          req.reject(new Error(`HTTP ${res.status}: ${text}`));
        } else if (res.status === 204) {
          req.resolve(undefined);
        } else {
          req.resolve(await res.json());
        }
      } catch (err) {
        req.reject(err);
      }
    }
  }

  private _startPing() {
    if (this._pingTimer) clearInterval(this._pingTimer);
    this._pingTimer = setInterval(() => this._ping(), PING_INTERVAL_MS);
    this._ping();
  }

  private async _ping() {
    try {
      const baseUrl = this._getBaseUrl();
      const res = await fetch(`${baseUrl}/health`, { method: "GET" });
      if (res.ok) {
        if (this._state !== "connected") {
          this._state = "connected";
          this._retryCount = 0;
          useSettingsStore.getState().setSidecarReady(true);
          this._notify();
          await this._flushQueue();
        }
      } else {
        this._onPingFailure();
      }
    } catch {
      this._onPingFailure();
    }
  }

  private _onPingFailure() {
    if (this._state === "connected" || this._state === "reconnecting") {
      this._retryCount++;
      if (this._retryCount > MAX_RETRIES) {
        this._state = "error";
        useSettingsStore.getState().setSidecarReady(false);
        useErrorStore.getState().addError({
          code: "sidecar_unavailable",
          message: "NeuralFlow sidecar is not responding.",
          recovery_hint: "Ensure the sidecar is running on the configured port.",
          severity: "critical",
        });
        this._notify();
      } else {
        this._state = "reconnecting";
        this._notify();
      }
    }
  }

  private _getBaseUrl(): string {
    const { remoteSidecarUrl } = useSettingsStore.getState();
    return remoteSidecarUrl ?? "http://127.0.0.1:7411";
  }

  private _getAuthHeaders(): Record<string, string> {
    const { remoteAuthToken } = useSettingsStore.getState();
    if (remoteAuthToken) {
      return { Authorization: `Bearer ${remoteAuthToken}` };
    }
    return {};
  }

  private _notify() {
    for (const listener of this._listeners) {
      listener(this._state);
    }
  }
}

export const connectionManager = new ConnectionManager();
