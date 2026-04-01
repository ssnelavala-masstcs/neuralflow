<div align="center">

# NeuralFlow

**Visual AI Agent Orchestration — Local, Private, Any Model**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Built with Tauri](https://img.shields.io/badge/Built%20with-Tauri%20v2-orange)](https://tauri.app)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Phase 1 Complete](https://img.shields.io/badge/Phase%201-Complete-brightgreen)](docs/PRD.md)

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
| Anthropic | Claude Opus/Sonnet/Haiku |
| DeepSeek | deepseek-chat, deepseek-reasoner |
| Groq | Llama 3.3 70B, Mixtral 8x7B |
| Mistral | Mistral Large, Codestral |
| Google | Gemini 2.0 Flash, Gemini 2.5 Pro |
| AWS Bedrock | Claude, Llama, Titan |
| Ollama (local) | Llama 3.2, Qwen 2.5, Phi-4, any model |
| LM Studio (local) | Any GGUF model |
| Any OpenAI-compatible API | Custom base URL |

### Multi-Agent Orchestration
- **Sequential** — agents run one after another (Phase 1, live)
- **Parallel** — independent branches run concurrently (Phase 1, live)
- **Hierarchical** — manager agent delegates to workers via [CrewAI](https://github.com/crewAIInc/crewAI) (Phase 2)
- **State Machine** — loops and conditional branching via [LangGraph](https://github.com/langchain-ai/langgraph) (Phase 2)

### Built-in Tools
- Web search (Serper / Tavily / DuckDuckGo)
- File read/write (sandboxed to `~/neuralflow-files/`)
- HTTP requests (GET/POST/PUT/DELETE)
- Calculator (safe expression evaluator)
- **MCP Protocol**: connect any [Model Context Protocol](https://modelcontextprotocol.io) server (stdio, SSE, HTTP)

### Live Run Log
- Real-time SSE stream of all agent activity as it happens
- Per-node status badges (idle / running / complete / error)
- Tool call and result inspection inline
- Run cancel mid-execution

### Cost Tracking
- Per-node, per-agent, per-run cost breakdown from LiteLLM usage data
- Cumulative cost charts by day / workflow / model (Phase 2)
- Budget alerts before running (Phase 2)

### Privacy First
- API keys stored in **OS keychain** (macOS Keychain, Windows Credential Manager, Linux libsecret) — never on disk
- Sidecar listens only on `127.0.0.1`
- No telemetry by default
- Works fully offline with Ollama

---

## Quick Start

### Build from Source

**Prerequisites**
- [Rust](https://rustup.rs/) (stable)
- [Node.js 20+](https://nodejs.org) + [pnpm](https://pnpm.io)
- [Python 3.11+](https://python.org) + [uv](https://github.com/astral-sh/uv)

```bash
# 1. Clone the repo
git clone https://github.com/ssnelavala-masstcs/neuralflow
cd neuralflow

# 2. Install all dependencies (frontend + sidecar)
./scripts/setup-dev.sh

# 3. Start development server
./scripts/dev.sh
```

The app opens automatically. The Python sidecar starts on `localhost:7411`.

### Starter Templates

Five workflow templates are included out of the box:

| Template | What it does |
|----------|-------------|
| `research-assistant` | Web search → structured summary report |
| `content-writer` | Outline planner → SEO-optimized blog post |
| `code-reviewer` | Parallel security + quality review → consolidated report |
| `data-analyzer` | File reader → statistical analysis report |
| `web-scraper` | HTTP fetch → content extraction → saved summary |

Load any template via the **Templates** menu or the API:
```bash
curl -X POST "http://localhost:7411/api/templates/research-assistant.json/import?workspace_id=<id>"
```

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
│  ├── Sequential/Parallel Executor  ✅              │
│  ├── CrewAI Executor (hierarchical)  🔜 Phase 2   │
│  └── LangGraph Executor (state machines) 🔜 P2   │
│                                                    │
│  LiteLLM (in-process, all model providers) ✅      │
│  MCP Client (stdio · SSE · HTTP)  ✅               │
│  Built-in Tools (search, file, HTTP, calc) ✅      │
│  SQLite + SQLAlchemy (all persistence)  ✅         │
│  APScheduler (triggers)  🔜 Phase 2               │
└───────────────────────────────────────────────────┘
```

### Key Design Decisions

**Tauri v2 over Electron**: 3-10 MB binary vs 80-150 MB. OS-native webview. Rust backend for secure keychain access and process management.

**Python sidecar over Node.js backend**: Gives access to the entire Python AI ecosystem (CrewAI, LangGraph, LiteLLM, ChromaDB, Playwright). Started by `scripts/dev.sh`, communicates via localhost HTTP + SSE.

**LiteLLM in-process**: Not a separate proxy server — imported directly in the sidecar. Every new model provider LiteLLM supports is automatically available in NeuralFlow with zero code changes.

**CrewAI + LangGraph as executors, not reimplemented**: NeuralFlow translates its visual workflow JSON into CrewAI/LangGraph primitives at runtime. When those frameworks add features, NeuralFlow inherits them.

**SQLite only**: No Postgres, no Redis, no external services. One `.db` file per workspace at `~/.neuralflow/workspaces/default/data.db`. Works offline. Trivial to back up.

---

## Project Structure

```
neuralflow/
├── apps/
│   └── desktop/              # Tauri application
│       ├── src-tauri/        # Rust backend (keychain IPC, Tauri config)
│       └── src/              # React frontend
│           ├── canvas/       # React Flow nodes, edges, canvas logic
│           ├── components/   # UI components (layout, palette, run log)
│           ├── stores/       # Zustand state stores
│           ├── api/          # FastAPI client
│           └── types/        # TypeScript type definitions
│
├── packages/
│   └── sidecar/              # Python FastAPI backend
│       └── neuralflow/
│           ├── api/          # FastAPI routers (workflows, runs, providers, mcp, tools, templates)
│           ├── execution/    # Orchestrator, sequential executor, agent runner, SSE emitter
│           ├── tools/        # Built-in tool implementations + registry
│           ├── mcp/          # MCP connection pool (stdio + SSE/HTTP)
│           ├── models/       # SQLAlchemy ORM models
│           └── schemas/      # Pydantic request/response schemas
│
├── templates/                # 5 starter workflow JSON files
├── docs/                     # PRD and architecture docs
│   └── PRD.md
└── scripts/                  # Dev setup and build scripts
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop shell | [Tauri v2](https://tauri.app) (Rust) |
| Frontend framework | React 19 + TypeScript + Vite |
| Visual canvas | [React Flow / xyflow v12](https://reactflow.dev) |
| UI components | [shadcn/ui](https://ui.shadcn.com) + Tailwind CSS v3 |
| State management | [Zustand v5](https://zustand-demo.pmnd.rs) + Immer |
| Backend framework | [FastAPI](https://fastapi.tiangolo.com) + Python 3.11+ |
| Multi-agent (hierarchical) | [CrewAI](https://crewai.com) |
| Multi-agent (state machine) | [LangGraph](https://langchain-ai.github.io/langgraph) |
| Model routing | [LiteLLM](https://litellm.ai) |
| Database | SQLite + [SQLAlchemy 2.0](https://sqlalchemy.org) + aiosqlite |
| MCP client | [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) |
| Scheduling | APScheduler |
| Package manager | pnpm (frontend) + uv (Python) |

---

## Roadmap

### Phase 1 — Core MVP ✅ Complete
- [x] Tauri v2 shell + Python sidecar lifecycle
- [x] React Flow canvas with all 10 node types
- [x] Model provider management (LiteLLM integration)
- [x] Sequential workflow execution with SSE streaming
- [x] Built-in tools (web search, file ops, HTTP, calculator)
- [x] MCP server integration (stdio + SSE/HTTP)
- [x] Live run log + per-node status visualization
- [x] Basic cost tracking (per-node, per-run)
- [x] Workflow save/load (JSON)
- [x] 5 starter templates
- [x] OS keychain API key storage

### Phase 2 — Power Features
- [ ] PropertiesPanel: inline editing of agent model/prompt/temperature
- [ ] Provider settings modal UI
- [ ] CrewAI hierarchical executor
- [ ] LangGraph state machine executor
- [ ] Step-through debug replay
- [ ] Memory nodes + RAG pipeline (sqlite-vec)
- [ ] Cost dashboard with charts and alerts
- [ ] Cron + webhook triggers
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

**Good first issues** are tagged in the [issue tracker](https://github.com/ssnelavala-masstcs/neuralflow/issues).

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

Built by **Stanley Sujith Nelavala** with assistance from **Claude Sonnet 4.6** (`claude-sonnet-4-6`) · [S&L Tech](https://github.com/ssnelavala-masstcs/neuralflow)

</div>
