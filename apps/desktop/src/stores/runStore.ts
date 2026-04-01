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
        () => {
          set((s) => { s.isStreaming = false; });
          _cleanup = null;
        }
      );
    },

    cancelRun: async () => {
      const { activeRun } = get();
      if (!activeRun) return;
      _cleanup?.();
      await runsApi.cancel(activeRun.id);
      set((s) => { s.runStatus = "cancelled"; s.isStreaming = false; });
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
