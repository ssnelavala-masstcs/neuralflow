import { create } from "zustand";
import { NeuralFlowError, resolveError } from "@/types/errors";

interface QueuedError extends NeuralFlowError {
  id: string;
}

interface ErrorState {
  errors: QueuedError[];
  criticalError: NeuralFlowError | null;
  addError: (raw: unknown) => void;
  dismissError: (id: string) => void;
  dismissAll: () => void;
  setCriticalError: (err: NeuralFlowError) => void;
  clearCritical: () => void;
}

let _counter = 0;

export const useErrorStore = create<ErrorState>((set) => ({
  errors: [],
  criticalError: null,

  addError: (raw: unknown) => {
    const err = resolveError(raw);
    const queued: QueuedError = { ...err, id: `err-${Date.now()}-${_counter++}` };
    set((state) => ({
      errors: [...state.errors.slice(-49), queued],
      criticalError: err.severity === "critical" ? err : state.criticalError,
    }));
  },

  dismissError: (id: string) => {
    set((state) => ({
      errors: state.errors.filter((e) => e.id !== id),
    }));
  },

  dismissAll: () => {
    set({ errors: [], criticalError: null });
  },

  setCriticalError: (err: NeuralFlowError) => {
    set({ criticalError: err });
  },

  clearCritical: () => {
    set({ criticalError: null });
  },
}));
