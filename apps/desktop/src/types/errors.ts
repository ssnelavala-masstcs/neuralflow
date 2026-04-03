export type ErrorSeverity = "info" | "warning" | "critical";

export interface NeuralFlowError {
  code: string;
  message: string;
  details?: Record<string, unknown> | null;
  recovery_hint?: string | null;
  severity: ErrorSeverity;
  timestamp?: number;
}

export interface ErrorRegistryEntry {
  message: string;
  recovery_hint: string;
  severity: ErrorSeverity;
}

export const ERROR_REGISTRY: Record<string, ErrorRegistryEntry> = {
  // Connection errors
  ECONNREFUSED: {
    message: "Cannot connect to NeuralFlow sidecar. Is it running?",
    recovery_hint: "Run `./scripts/dev.sh` or restart the sidecar.",
    severity: "critical",
  },
  ETIMEDOUT: {
    message: "Connection to sidecar timed out.",
    recovery_hint: "Check if the sidecar is running and the port is correct.",
    severity: "critical",
  },
  ENOTFOUND: {
    message: "Could not resolve the sidecar address.",
    recovery_hint: "Check your remote connection settings.",
    severity: "critical",
  },

  // API errors
  sidecar_unavailable: {
    message: "NeuralFlow sidecar is not responding.",
    recovery_hint: "Ensure the sidecar is running on the configured port.",
    severity: "critical",
  },
  workflow_not_found: {
    message: "Workflow not found.",
    recovery_hint: "The workflow may have been deleted. Try refreshing the workspace.",
    severity: "warning",
  },
  provider_unreachable: {
    message: "Could not reach the LLM provider.",
    recovery_hint: "Check your API key and network connection.",
    severity: "warning",
  },
  invalid_api_key: {
    message: "Invalid API key.",
    recovery_hint: "Update your provider API key in Settings.",
    severity: "warning",
  },
  payload_too_large: {
    message: "Request body exceeds maximum allowed size.",
    recovery_hint: "Try reducing the size of your input data.",
    severity: "info",
  },
  rate_limited: {
    message: "Too many requests. Please wait a moment.",
    recovery_hint: "You've hit the rate limit. Wait a few seconds and try again.",
    severity: "info",
  },

  // Execution errors
  run_failed: {
    message: "Workflow execution failed.",
    recovery_hint: "Check the Run Log for details. You can replay from a specific step.",
    severity: "critical",
  },
  agent_error: {
    message: "Agent execution encountered an error.",
    recovery_hint: "Check the agent's configuration and model availability.",
    severity: "critical",
  },
  tool_error: {
    message: "A tool call failed during execution.",
    recovery_hint: "Check the tool configuration and try again.",
    severity: "warning",
  },

  // Validation errors
  validation_failed: {
    message: "Workflow validation failed.",
    recovery_hint: "Fix the validation errors before running.",
    severity: "warning",
  },
  missing_trigger: {
    message: "Workflow needs at least one Trigger node.",
    recovery_hint: "Add a Trigger node from the palette to start the workflow.",
    severity: "warning",
  },
  missing_output: {
    message: "Workflow needs at least one Output node.",
    recovery_hint: "Add an Output node from the palette to capture results.",
    severity: "warning",
  },
  orphaned_nodes: {
    message: "Some nodes are not connected to the workflow.",
    recovery_hint: "Connect all nodes from a Trigger to an Output.",
    severity: "info",
  },
  missing_model: {
    message: "An Agent node is missing its model configuration.",
    recovery_hint: "Select a model in the Agent's properties.",
    severity: "warning",
  },

  // Fallback
  unknown: {
    message: "An unexpected error occurred.",
    recovery_hint: "Try refreshing or restarting the application.",
    severity: "critical",
  },
};

export function resolveError(raw: unknown): NeuralFlowError {
  if (raw instanceof Error && 'code' in raw && 'severity' in raw) return raw as NeuralFlowError;

  if (raw instanceof Error) {
    const code = resolveCode(raw.message);
    const entry = ERROR_REGISTRY[code] ?? ERROR_REGISTRY.unknown;
    return {
      code,
      message: entry.message,
      details: { original: raw.message },
      recovery_hint: entry.recovery_hint,
      severity: entry.severity,
      timestamp: Date.now(),
    };
  }

  if (typeof raw === "object" && raw !== null) {
    const obj = raw as Record<string, unknown>;
    const code = typeof obj.code === "string" ? obj.code : "unknown";
    const entry = ERROR_REGISTRY[code] ?? ERROR_REGISTRY.unknown;
    return {
      code,
      message: (obj.message as string) ?? entry.message,
      details: (obj.details as Record<string, unknown>) ?? null,
      recovery_hint: (obj.recovery_hint as string) ?? entry.recovery_hint,
      severity: (obj.severity as ErrorSeverity) ?? entry.severity,
      timestamp: Date.now(),
    };
  }

  return {
    code: "unknown",
    message: String(raw),
    recovery_hint: ERROR_REGISTRY.unknown.recovery_hint,
    severity: "critical",
    timestamp: Date.now(),
  };
}

function resolveCode(message: string): string {
  if (message.includes("ECONNREFUSED")) return "ECONNREFUSED";
  if (message.includes("ETIMEDOUT")) return "ETIMEDOUT";
  if (message.includes("ENOTFOUND")) return "ENOTFOUND";
  return "unknown";
}
