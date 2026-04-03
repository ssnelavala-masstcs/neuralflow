#!/usr/bin/env bash
# ============================================================
# NeuralFlow — Docs Preview Server
# Serves docs/ locally for live preview while editing.
# Usage: ./scripts/preview-docs.sh
# ============================================================
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS_DIR="$ROOT/docs"
PORT=8080

# Check that docs exist
if [ ! -f "$DOCS_DIR/index.html" ]; then
  echo "ERROR: docs/index.html not found. Run from repo root."
  exit 1
fi

echo ""
echo "  >_ NeuralFlow Docs Preview"
echo "  ─────────────────────────────────"
echo "  Serving: $DOCS_DIR"
echo "  URL:     http://127.0.0.1:$PORT"
echo "  Press Ctrl+C to stop"
echo "  ─────────────────────────────────"
echo ""

# Try python3 http server (always available), fall back to npx
if command -v python3 &>/dev/null; then
  cd "$DOCS_DIR"
  python3 -m http.server "$PORT" --bind 127.0.0.1
elif command -v python &>/dev/null; then
  cd "$DOCS_DIR"
  python -m http.server "$PORT" --bind 127.0.0.1
elif command -v npx &>/dev/null; then
  npx serve "$DOCS_DIR" -l "$PORT"
else
  echo "ERROR: No HTTP server available. Install python3 or node."
  exit 1
fi
