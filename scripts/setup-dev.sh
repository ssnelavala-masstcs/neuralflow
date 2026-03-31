#!/usr/bin/env bash
set -euo pipefail

echo "==> Setting up NeuralFlow development environment"

# Check prerequisites
command -v rustup &>/dev/null || { echo "ERROR: Rust not found. Install from https://rustup.rs"; exit 1; }
command -v node &>/dev/null   || { echo "ERROR: Node.js not found. Install from https://nodejs.org"; exit 1; }
command -v pnpm &>/dev/null   || { echo "ERROR: pnpm not found. Run: npm install -g pnpm"; exit 1; }
command -v python3 &>/dev/null || { echo "ERROR: Python 3 not found. Install from https://python.org"; exit 1; }
command -v uv &>/dev/null     || { echo "ERROR: uv not found. Run: pip install uv"; exit 1; }

echo "==> Installing frontend dependencies"
cd apps/desktop
pnpm install
cd ../..

echo "==> Setting up Python sidecar"
cd packages/sidecar
uv venv
uv sync
cd ../..

echo "==> Done. Run ./scripts/dev.sh to start the app."
