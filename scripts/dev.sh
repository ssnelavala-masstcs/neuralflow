#!/usr/bin/env bash
set -euo pipefail

echo "==> Starting NeuralFlow development server"

# Start Python sidecar in background
echo "==> Starting Python sidecar on :7411"
cd packages/sidecar
uv run uvicorn neuralflow.main:app --host 127.0.0.1 --port 7411 --reload &
SIDECAR_PID=$!
cd ../..

# Give sidecar a moment to start
sleep 2

# Start Tauri dev (also starts Vite)
echo "==> Starting Tauri dev server"
cd apps/desktop
pnpm tauri dev

# On exit, kill sidecar
kill $SIDECAR_PID 2>/dev/null || true
