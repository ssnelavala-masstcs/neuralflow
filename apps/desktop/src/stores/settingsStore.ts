import { create } from "zustand";
import { persist } from "zustand/middleware";

interface SettingsState {
  theme: "dark" | "light" | "system";
  sidecarPort: number;
  sidecarReady: boolean;

  setTheme: (theme: "dark" | "light" | "system") => void;
  setSidecarReady: (ready: boolean) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: "system",
      sidecarPort: 7411,
      sidecarReady: false,

      setTheme: (theme) => set({ theme }),
      setSidecarReady: (ready) => set({ sidecarReady: ready }),
    }),
    { name: "neuralflow-settings" }
  )
);
