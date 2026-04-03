import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import type { NodeRunStatus, Run, RunStatus, StreamEvent } from "@/types/run";
import { runsApi } from "@/api/runs";

interface RunState {
  activeRun: Run | null;
  runStatus: RunStatus | "idle";
  nodeStatuses: Record<string, NodeRunStatus>;
  streamEvents: StreamEvent[];
  runHistory: Run[];
  isStreaming: boolean;
  output: unknown;

  startRun: (workflowId: string, inputData?: Record<string, unknown>) => Promise<void>;
  cancelRun: () => Promise<void>;
  clearRun: () => void;
  loadHistory: (workflowId?: string) => Promise<void>;
}

let _cleanup: (() => void) | null = null;
let _isCancelling = false;

export const useRunStore = create<RunState>()(
  immer((set, get) => ({
    activeRun: null,
    runStatus: "idle",
    nodeStatuses: {},
    streamEvents: [],
    runHistory: [],
    isStreaming: false,
    output: null,

    startRun: async (workflowId, inputData) => {
      set((s) => {
        s.activeRun = null;
        s.runStatus = "queued";
        s.nodeStatuses = {};
        s.streamEvents = [];
        s.isStreaming = true;
        s.output = null;
      });

      const run = await runsApi.start(workflowId, inputData);
      set((s) => { s.activeRun = run; });

      _cleanup = runsApi.stream(
        run.id,
        (event) => {
          set((s) => {
            s.streamEvents.push(event);
            switch (event.type) {
              case "run_started":
                s.runStatus = "running";
                break;
              case "run_completed":
                s.runStatus = "complete";
                s.output = event.output;
                s.isStreaming = false;
                break;
              case "run_failed":
                s.runStatus = "error";
                s.isStreaming = false;
                break;
              case "cancelled":
                s.runStatus = "cancelled";
                s.isStreaming = false;
                break;
              case "node_started":
                if (event.node_id) s.nodeStatuses[event.node_id] = "running";
                break;
              case "node_completed":
                if (event.node_id) s.nodeStatuses[event.node_id] = "complete";
                break;
              case "node_failed":
                if (event.node_id) s.nodeStatuses[event.node_id] = "error";
                break;
            }
          });
        },
        async () => {
          set((s) => { s.isStreaming = false; });
          _cleanup = null;
          // Skip the status fetch if we're in the middle of a manual cancel —
          // cancelRun sets the status itself after this fires.
          if (_isCancelling) return;
          // Safety net: if status is still stuck in an active state after SSE closes
          // (e.g. run completed before SSE connected), fetch the final status.
          const state = get();
          if (state.activeRun && (state.runStatus === "queued" || state.runStatus === "running")) {
            try {
              const finalRun = await runsApi.get(state.activeRun.id);
              set((s) => { s.runStatus = finalRun.status as RunStatus; });
            } catch { /* ignore */ }
          }
        }
      );
    },

    cancelRun: async () => {
      const { activeRun } = get();
      if (!activeRun) return;
      _isCancelling = true;
      try {
        await runsApi.cancel(activeRun.id);
      } catch { /* already finished — still close cleanly */ }
      _cleanup?.();
      _cleanup = null;
      set((s) => { s.runStatus = "cancelled"; s.isStreaming = false; });
      _isCancelling = false;
    },

    clearRun: () =>
      set((s) => {
        _cleanup?.();
        s.activeRun = null;
        s.runStatus = "idle";
        s.nodeStatuses = {};
        s.streamEvents = [];
        s.isStreaming = false;
        s.output = null;
      }),

    loadHistory: async (workflowId) => {
      const runs = await runsApi.list(workflowId);
      set((s) => { s.runHistory = runs; });
    },
  }))
);
