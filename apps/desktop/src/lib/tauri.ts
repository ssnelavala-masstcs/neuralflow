// Tauri IPC wrappers — falls back gracefully when running in browser (dev without Tauri)
declare const window: Window & { __TAURI__?: unknown };

function isTauri(): boolean {
  return typeof window !== "undefined" && "__TAURI__" in window;
}

async function invoke<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  if (!isTauri()) {
    throw new Error(`Tauri not available (running in browser). Command: ${cmd}`);
  }
  const { invoke: tauriInvoke } = await import("@tauri-apps/api/core");
  return tauriInvoke<T>(cmd, args);
}

export const keychain = {
  set: (key: string, value: string) => invoke<void>("keychain_set", { key, value }),
  get: (key: string) => invoke<string>("keychain_get", { key }),
  delete: (key: string) => invoke<void>("keychain_delete", { key }),
};
