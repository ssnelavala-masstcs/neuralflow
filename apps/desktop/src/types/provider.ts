export type ProviderType =
  | "openai"
  | "anthropic"
  | "openrouter"
  | "groq"
  | "mistral"
  | "deepseek"
  | "google"
  | "ollama"
  | "lm_studio"
  | "azure"
  | "bedrock"
  | "custom";

export type ConnectionStatus = "ok" | "error" | "untested" | "testing";

export interface Provider {
  id: string;
  name: string;
  provider_type: ProviderType;
  base_url: string | null;
  api_key_ref: string | null;
  default_model: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  context_window: number | null;
  input_cost_per_1m: number | null;
  output_cost_per_1m: number | null;
}
