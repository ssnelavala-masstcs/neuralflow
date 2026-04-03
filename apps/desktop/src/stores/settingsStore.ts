import { create } from "zustand";
import { persist } from "zustand/middleware";

interface SettingsState {
  theme: "dark" | "light" | "system";
  sidecarPort: number;
  sidecarReady: boolean;

  // Remote execution
  remoteSidecarUrl: string | null;
  remoteAuthToken: string | null;
  connectionStatus: "disconnected" | "connecting" | "connected" | "error";

  setTheme: (theme: "dark" | "light" | "system") => void;
  setSidecarReady: (ready: boolean) => void;
  setRemoteSidecarUrl: (url: string | null) => void;
  setRemoteAuthToken: (token: string | null) => void;
  setConnectionStatus: (status: "disconnected" | "connecting" | "connected" | "error") => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: "system",
      sidecarPort: 7411,
      sidecarReady: false,

      remoteSidecarUrl: null,
      remoteAuthToken: null,
      connectionStatus: "disconnected",

      setTheme: (theme) => set({ theme }),
      setSidecarReady: (ready) => set({ sidecarReady: ready }),
      setRemoteSidecarUrl: (url) => set({ remoteSidecarUrl: url }),
      setRemoteAuthToken: (token) => set({ remoteAuthToken: token }),
      setConnectionStatus: (status) => set({ connectionStatus: status }),
    }),
    { name: "neuralflow-settings" }
  )
);
