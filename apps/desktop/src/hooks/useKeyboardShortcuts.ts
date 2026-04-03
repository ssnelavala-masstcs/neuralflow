import { useEffect, useRef } from "react";

interface Shortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  handler: (e: KeyboardEvent) => void;
}

interface UseKeyboardShortcutsOptions {
  shortcuts: Shortcut[];
  enabled?: boolean;
}

export function useKeyboardShortcuts({ shortcuts, enabled = true }: UseKeyboardShortcutsOptions) {
  const shortcutsRef = useRef(shortcuts);
  shortcutsRef.current = shortcuts;

  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      for (const shortcut of shortcutsRef.current) {
        const matchesKey = e.key.toLowerCase() === shortcut.key.toLowerCase();
        const matchesCtrl = !shortcut.ctrl || e.ctrlKey || e.metaKey;
        const matchesShift = !shortcut.shift || e.shiftKey;
        const matchesAlt = !shortcut.alt || e.altKey;
        const noExtra = (!shortcut.ctrl && !e.ctrlKey && !e.metaKey) || shortcut.ctrl;
        const noExtraShift = (!shortcut.shift && !e.shiftKey) || shortcut.shift;
        const noExtraAlt = (!shortcut.alt && !e.altKey) || shortcut.alt;

        if (
          matchesKey &&
          matchesCtrl &&
          matchesShift &&
          matchesAlt &&
          noExtra &&
          noExtraShift &&
          noExtraAlt
        ) {
          e.preventDefault();
          shortcut.handler(e);
          break;
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [enabled]);
}
