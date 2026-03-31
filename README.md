<div align="center">

# NeuralFlow

**Visual AI Agent Orchestration — Local, Private, Any Model**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Built with Tauri](https://img.shields.io/badge/Built%20with-Tauri%20v2-orange)](https://tauri.app)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)

> Build multi-agent AI workflows by drawing them. Runs entirely on your machine.

[Features](#features) · [Quick Start](#quick-start) · [Architecture](#architecture) · [Roadmap](#roadmap) · [Contributing](#contributing)

</div>

---

## What is NeuralFlow?

NeuralFlow is an open-source desktop application for visually orchestrating AI agents. Drag nodes onto a canvas, connect them, pick your model, and run. No Docker. No cloud account. No Python degree required.

It bridges the gap that every existing tool leaves open:

| Tool | Visual UI | Real Multi-Agent | Local/Desktop | Any Model | Debug/Replay | Cost Tracking |
|------|-----------|-----------------|---------------|-----------|--------------|---------------|
| CrewAI | No (code only) | Excellent | Yes | Partial | No | No |
| LangFlow | Yes | Weak | No (web) | Partial | No | No |
| Flowise | Yes | Weak | Partial | Yes | No | No |
| Dify | Yes | Good | No (Docker) | Yes | No | Partial |
| AutoGen Studio | Partial | Good | Partial | No | No | No |
| **NeuralFlow** | **Yes** | **Excellent** | **Yes** | **Yes** | **Yes** | **Yes** |

---

## Features

### Visual Canvas
- Infinite drag-and-drop canvas powered by [React Flow](https://reactflow.dev)
- **10 node types**: Agent, Task, Tool, Trigger, Router, Memory, Human Checkpoint, Aggregator, Output, Subflow
- Connect nodes with typed edges (data, control, conditional)
- Auto-layout, undo/redo, copy/paste, multi-select
- Mini-map for large workflows

### Any Model, Any Provider
Powered by [LiteLLM](https://github.com/BerriAI/litellm) — one interface to all of them:

| Provider | Models |
|----------|--------|
| OpenAI | GPT-4o, GPT-4.1, o3, o4-mini |
| DeepSeek | deepseek-chat, deepseek-reasoner |
| Groq | Llama 3.3 70B, Mixtral 8x7B |
| Mistral | Mistral Large, Codestral |
| Google | Gemini 2.0 Flash, Gemini 2.5 Pro |
| AWS Bedrock | Claude, Llama, Titan |
| Ollama (local) | Llama 3.2, Qwen 2.5, Phi-4, any model |
| LM Studio (local) | Any GGUF model |
| Any OpenAI-compatible API | Custom base URL |

### Multi-Agent Orchestration (4 execution modes)
- **Sequential** — agents run one after another
- **Parallel** — independent branches run concurrently
- **Hierarchical** — manager agent delegates to workers ([CrewAI](https://github.com/crewAIInc/crewAI))
- **State Machine** — loops and conditional branching ([LangGraph](https://github.com/langchain-ai/langgraph))

### Tools and MCP
- **Built-in tools**: web search, web browser (Playwright), file read/write, HTTP requests, Python code execution, SQLite queries, calculator
- **MCP Protocol**: connect any [Model Context Protocol](https://modelcontextprotocol.io) server (stdio, SSE, HTTP)
- **Custom tools**: write a Python function, define its schema, use it immediately

### Step-Through Debugger
Click any past run and step through it node by node:
- See the exact messages sent to and received from every LLM call
- Inspect every tool input and output
- Re-run from any intermediate checkpoint with modified state

### Cost Tracking
- Per-node, per-agent, per-run cost breakdown
- Cumulative cost charts by day / workflow / model
- Budget alerts before running
- Export cost reports as CSV

### Privacy First
- API keys stored in **OS keychain** (macOS Keychain, Windows Credential Manager, Linux libsecret) — never on disk
- Sidecar listens only on `127.0.0.1`
- No telemetry by default
- Works fully offline with Ollama

---

## Quick Start

### Install (Pre-built, coming soon)

Download the latest release for your platform:
- **macOS**: `NeuralFlow_x.x.x_aarch64.dmg` / `NeuralFlow_x.x.x_x64.dmg`
- **Windows**: `NeuralFlow_x.x.x_x64-setup.exe`
- **Linux**: `NeuralFlow_x.x.x_amd64.AppImage` / `.deb`

Double-click, install, open. That's it.

### Build from Source

**Prerequisites**
- [Rust](https://rustup.rs/) (stable)
- [Node.js 20+](https://nodejs.org) + [pnpm](https://pnpm.io)
- [Python 3.11+](https://python.org) + [uv](https://github.com/astral-sh/uv)

```bash
# 1. Clone the repo
git clone https://github.com/neuralflow-ai/neuralflow
cd neuralflow

# 2. Install all dependencies (frontend + sidecar)
./scripts/setup-dev.sh

# 3. Start development server
./scripts/dev.sh
```

The app opens automatically. The Python sidecar starts on `localhost:7411`.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              NeuralFlow Desktop App              │
│                  (Tauri v2)                      │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │         React Frontend (Webview)          │  │
│  │                                           │  │
│  │   Canvas (React Flow) │ UI (shadcn/ui)   │  │
│  │   State (Zustand)     │ API Client        │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │      Tauri Rust Bridge (IPC)              │  │
│  │  Keychain · Filesystem · Process Mgmt    │  │
│  └───────────────────────────────────────────┘  │
└───────────────┬─────────────────────────────────┘
                │ HTTP REST + SSE
                ▼
┌───────────────────────────────────────────────────┐
│          Python Sidecar (FastAPI :7411)            │
│                                                    │
│  Execution Engine                                  │
│  ├── Sequential Executor                           │
│  ├── CrewAI Executor (hierarchical)                │
│  └── LangGraph Executor (state machines)           │
│                                                    │
│  LiteLLM (in-process, all model providers)         │
│  MCP Client (stdio · SSE · HTTP)                   │
│  Memory (sqlite-vec / ChromaDB)                    │
│  SQLite + SQLAlchemy (all persistence)             │
│  APScheduler (cron + webhook triggers)             │
└───────────────────────────────────────────────────┘
```

### Key Design Decisions

**Tauri v2 over Electron**: 3-10 MB binary vs 80-150 MB. OS-native webview. Rust backend for secure keychain access and process management.

**Python sidecar over Node.js backend**: Gives access to the entire Python AI ecosystem (CrewAI, LangGraph, LiteLLM, ChromaDB, Playwright). Spawned by Tauri on startup, communicates via localhost HTTP + SSE.

**LiteLLM in-process**: Not a separate proxy server — imported directly in the sidecar. Every new model provider LiteLLM supports is automatically available in NeuralFlow with zero code changes.

**CrewAI + LangGraph as executors, not reimplemented**: NeuralFlow translates its visual workflow JSON into CrewAI/LangGraph primitives at runtime. When those frameworks add features, NeuralFlow inherits them.

**SQLite only**: No Postgres, no Redis, no external services. One `.db` file per workspace. Works offline. Trivial to back up.

---

## Project Structure

```
neuralflow/
├── apps/
│   └── desktop/              # Tauri application
│       ├── src-tauri/        # Rust backend (keychain, sidecar, IPC)
│       └── src/              # React frontend
│           ├── canvas/       # React Flow nodes, edges, canvas logic
│           ├── components/   # UI components (layout, panels, modals)
│           ├── stores/       # Zustand state stores
│           ├── api/          # FastAPI client
│           └── types/        # TypeScript type definitions
│
├── packages/
│   └── sidecar/              # Python FastAPI backend
│       └── neuralflow/
│           ├── api/          # FastAPI routers
│           ├── execution/    # Orchestrator, CrewAI/LangGraph executors
│           ├── tools/        # Built-in tool implementations
│           ├── mcp/          # MCP client and connection pool
│           └── memory/       # Vector store, RAG pipeline
│
├── templates/                # Starter workflow JSON files
├── docs/                     # Documentation
└── scripts/                  # Dev setup and build scripts
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop shell | [Tauri v2](https://tauri.app) (Rust) |
| Frontend framework | React 19 + TypeScript + Vite |
| Visual canvas | [React Flow / xyflow](https://reactflow.dev) |
| UI components | [shadcn/ui](https://ui.shadcn.com) + Tailwind CSS v4 |
| State management | [Zustand](https://zustand-demo.pmnd.rs) |
| Code editor | Monaco Editor |
| Backend framework | [FastAPI](https://fastapi.tiangolo.com) + Python 3.11+ |
| Multi-agent (hierarchical) | [CrewAI](https://crewai.com) |
| Multi-agent (state machine) | [LangGraph](https://langchain-ai.github.io/langgraph) |
| Model routing | [LiteLLM](https://litellm.ai) |
| Database | SQLite + [SQLAlchemy](https://sqlalchemy.org) + Alembic |
| Vector store | sqlite-vec (Phase 1) → ChromaDB (Phase 2) |
| MCP client | [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) |
| Scheduling | APScheduler |
| Package manager | pnpm (frontend) + uv (Python) |

---

## Roadmap

### Phase 1 — Core MVP (In Progress)
- [ ] Tauri v2 shell + Python sidecar lifecycle
- [ ] React Flow canvas with all 10 node types
- [ ] Model provider management (LiteLLM integration)
- [ ] Sequential workflow execution with SSE streaming
- [ ] Built-in tools (web search, file ops, HTTP, code exec)
- [ ] MCP server integration
- [ ] Run log + per-node status visualization
- [ ] Basic cost tracking
- [ ] Workflow save/load (JSON)
- [ ] 5 starter templates
- [ ] Installers for macOS, Windows, Linux

### Phase 2 — Power Features
- [ ] CrewAI hierarchical executor
- [ ] LangGraph state machine executor
- [ ] Step-through debug replay
- [ ] Memory nodes + RAG pipeline
- [ ] Cost dashboard with charts and alerts
- [ ] Cron + webhook + file-watch triggers
- [ ] Human-in-the-loop nodes

### Phase 3 — Ecosystem
- [ ] Export to CrewAI Python code
- [ ] Export to LangGraph Python code
- [ ] Workflow version history + visual diff
- [ ] Plugin API (custom node types)
- [ ] Community template gallery

### Phase 4 — Scale
- [ ] Evaluation framework (A/B test workflows)
- [ ] Multi-workspace profiles
- [ ] Remote execution option (optional, self-hosted)

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, code style, and the PR process.

**Good first issues** are tagged in the [issue tracker](https://github.com/neuralflow-ai/neuralflow/issues).

Areas where contributions are especially valuable:
- New built-in tool implementations (`packages/sidecar/neuralflow/tools/`)
- Starter workflow templates (`templates/`)
- Node type UI improvements (`apps/desktop/src/canvas/nodes/`)
- Documentation and tutorials

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

You can use NeuralFlow commercially, fork it, build products on top of it. Attribution required.

---

## Acknowledgements

NeuralFlow is built on the shoulders of excellent open-source projects:

- [React Flow / xyflow](https://github.com/xyflow/xyflow) — the canvas engine
- [Tauri](https://github.com/tauri-apps/tauri) — the desktop shell
- [LiteLLM](https://github.com/BerriAI/litellm) — model routing
- [CrewAI](https://github.com/crewAIInc/crewAI) — multi-agent orchestration
- [LangGraph](https://github.com/langchain-ai/langgraph) — stateful agent workflows
- [shadcn/ui](https://github.com/shadcn-ui/ui) — UI components
- [FastAPI](https://github.com/tiangolo/fastapi) — backend framework

---

<div align="center">

Made with care by [S&L Tech](https://github.com/neuralflow-ai)

</div>
