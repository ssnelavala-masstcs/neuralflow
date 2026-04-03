import { api } from "./client";

export const authApi = {
  generateToken: (label?: string) =>
    api.post<{ token: string; label: string; created_at: number }>("/api/auth/token", { label: label ?? "remote-token" }),
  verifyToken: () =>
    api.post<{ valid: boolean; label: string | null }>("/api/auth/verify"),
  listTokens: () =>
    api.get<Array<{ label: string; created_at: number }>>("/api/auth/tokens"),
  revokeToken: (label: string) =>
    api.delete<void>(`/api/auth/tokens/${label}`),
};
