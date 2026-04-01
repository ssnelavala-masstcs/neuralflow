# NeuralFlow — Project Instructions

## What this is
Visual AI agent orchestration desktop app. Tauri v2 (Rust) + React 19 + Python FastAPI sidecar.
Full PRD at: `/home/stanley-sujith-nelavala/Desktop/neuralflow-prd/PRD.md`

## Structure
```
apps/desktop/          Tauri + React frontend (port 1420 in dev)
  src/                 React app
  src-tauri/           Rust IPC commands (keychain, etc.)
packages/sidecar/      Python FastAPI sidecar (port 7411)
  neuralflow/
    api/               FastAPI routers
    execution/         Orchestrator, sequential executor, agent runner
    models/            SQLAlchemy ORM
    schemas/           Pydantic request/response
    tools/             Built-in tools + registry
    mcp/               MCP connection pool
templates/             Starter workflow JSONs
```

## Dev startup
```bash
./scripts/dev.sh       # starts sidecar + Tauri dev in one command
```
Or manually:
```bash
cd packages/sidecar && uv run uvicorn neuralflow.main:app --host 127.0.0.1 --port 7411 --reload
cd apps/desktop && pnpm tauri dev
```

## Phase status
- **Phase 1 (M1.1–M1.7)**: COMPLETE — sidecar, canvas, execution engine, tools, MCP, templates
- **Phase 2 next**: CrewAI executor, LangGraph executor, step-through debugger, memory nodes, cost dashboard

## Key conventions
- API keys: never stored in SQLite. `api_key_ref` is a keychain key reference. Actual key retrieval via Tauri `keychain_get` IPC or `NEURALFLOW_KEY_<PROVIDER>` env var.
- SQLite only. One workspace = one `.db` file at `~/.neuralflow/workspaces/default/data.db`
- SSE streaming: per-run `asyncio.Queue` in `api/runs.py`, consumed by `EventSource` in `api/runs.ts`
- Node drag-to-canvas: `dataTransfer` key = `"application/neuralflow-node"`
