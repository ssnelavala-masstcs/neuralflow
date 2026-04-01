import { api } from "./client";
import type { ModelInfo, Provider } from "@/types/provider";

export const providersApi = {
  list: () => api.get<Provider[]>("/api/providers"),
  create: (data: {
    name: string;
    provider_type: string;
    base_url?: string;
    api_key_ref?: string;
    default_model?: string;
  }) => api.post<Provider>("/api/providers", data),
  update: (id: string, data: Partial<Provider>) =>
    api.patch<Provider>(`/api/providers/${id}`, data),
  delete: (id: string) => api.delete<void>(`/api/providers/${id}`),
  listModels: (id: string) => api.get<ModelInfo[]>(`/api/providers/${id}/models`),
  test: (id: string) => api.post<{ ok: boolean; error?: string; latency_ms?: number }>(`/api/providers/${id}/test`),
};
