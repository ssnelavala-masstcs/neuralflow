import { useSettingsStore } from "@/stores/settingsStore";

const DEFAULT_BASE_URL = "http://127.0.0.1:7411";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

function getBaseUrl(): string {
  const { remoteSidecarUrl } = useSettingsStore.getState();
  return remoteSidecarUrl ?? DEFAULT_BASE_URL;
}

function getAuthHeaders(): Record<string, string> {
  const { remoteAuthToken } = useSettingsStore.getState();
  if (remoteAuthToken) {
    return { Authorization: `Bearer ${remoteAuthToken}` };
  }
  return {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrl = getBaseUrl();
  const res = await fetch(`${baseUrl}${path}`, {
    headers: { "Content-Type": "application/json", ...getAuthHeaders(), ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new ApiError(res.status, text);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),

  /** Returns a native EventSource for SSE streams. */
  stream: (path: string): EventSource => {
    const baseUrl = getBaseUrl();
    const { remoteAuthToken } = useSettingsStore.getState();
    // EventSource doesn't support custom headers, so for authenticated SSE
    // we append the token as a query parameter
    const separator = path.includes("?") ? "&" : "?";
    const streamPath = remoteAuthToken ? `${path}${separator}token=${remoteAuthToken}` : path;
    return new EventSource(`${baseUrl}${streamPath}`);
  },
};
