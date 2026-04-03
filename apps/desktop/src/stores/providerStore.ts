import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import type { ConnectionStatus, ModelInfo, Provider } from "@/types/provider";
import { providersApi } from "@/api/providers";

export interface ModelTestResult {
  model: string;
  ok: boolean;
  latency_ms?: number;
  error?: string;
}

interface ProviderState {
  providers: Provider[];
  models: Record<string, ModelInfo[]>;
  connectionStatus: Record<string, ConnectionStatus>;
  modelTestResults: Record<string, ModelTestResult[]>;

  load: () => Promise<void>;
  addProvider: (data: Omit<Provider, "id" | "created_at" | "updated_at" | "is_active">) => Promise<Provider>;
  removeProvider: (id: string) => Promise<void>;
  testProvider: (id: string) => Promise<boolean>;
  listModels: (id: string) => Promise<ModelInfo[]>;
}

export const useProviderStore = create<ProviderState>()(
  immer((set, get) => ({
    providers: [],
    models: {},
    connectionStatus: {},
    modelTestResults: {},

    load: async () => {
      const providers = await providersApi.list();
      set((s) => { s.providers = providers; });
    },

    addProvider: async (data) => {
      const apiData = {
        ...data,
        base_url: data.base_url ?? undefined,
        api_key_ref: data.api_key_ref ?? undefined,
        default_model: data.default_model ?? undefined,
      };
      const p = await providersApi.create(apiData);
      set((s) => { s.providers.push(p); });
      return p;
    },

    removeProvider: async (id) => {
      await providersApi.delete(id);
      set((s) => { s.providers = s.providers.filter((p) => p.id !== id); });
    },

    testProvider: async (id) => {
      set((s) => { s.connectionStatus[id] = "testing"; });
      try {
        const result = await providersApi.test(id);
        set((s) => {
          s.connectionStatus[id] = result.ok ? "ok" : "error";
          if (result.models) s.modelTestResults[id] = result.models;
        });
        return result.ok;
      } catch {
        set((s) => { s.connectionStatus[id] = "error"; });
        return false;
      }
    },

    listModels: async (id) => {
      const models = await providersApi.listModels(id);
      set((s) => { s.models[id] = models; });
      return models;
    },
  }))
);
