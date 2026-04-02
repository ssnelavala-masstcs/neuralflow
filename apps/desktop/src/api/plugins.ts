import { api } from "./client";

export interface Plugin {
  name: string;
  version: string;
  description: string;
  author: string;
  node_types: string[];
  tool_names: string[];
  package: string;
  loaded: boolean;
  error: string | null;
}

export function listPlugins(): Promise<Plugin[]> {
  return api.get<Plugin[]>("/api/plugins");
}

export function reloadPlugins(): Promise<Plugin[]> {
  return api.post<Plugin[]>("/api/plugins/reload");
}
