<div align="center">

# NeuralFlow

**Visual AI Agent Orchestration — Local, Private, Any Model**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Release](https://img.shields.io/github/v/release/ssnelavala-masstcs/neuralflow?color=00ffc8)](https://github.com/ssnelavala-masstcs/neuralflow/releases)
[![Downloads](https://img.shields.io/github/downloads/ssnelavala-masstcs/neuralflow/total?color=00b4ff)](https://github.com/ssnelavala-masstcs/neuralflow/releases)
[![Built with Tauri](https://img.shields.io/badge/Built%20with-Tauri%20v2-orange)](https://tauri.app)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Docs](https://img.shields.io/badge/Docs-GitHub%20Pages-00ffc8)](https://ssnelavala-masstcs.github.io/neuralflow/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> Build multi-agent AI workflows by drawing them. Runs entirely on your machine.

[Download](https://github.com/ssnelavala-masstcs/neuralflow/releases) · [Features](#features) · [Quick Start](#quick-start) · [Architecture](#architecture) · [Docs](https://ssnelavala-masstcs.github.io/neuralflow/) · [Contributing](#contributing)

</div>

---

## What is NeuralFlow?

NeuralFlow is an open-source desktop application for visually orchestrating AI agents. Drag nodes onto a canvas, connect them, pick your model, and run. No Docker. No cloud account. No Python degree required.

| Tool | Visual UI | Multi-Agent | Local/Desktop | Any Model | Debug/Replay | Cost Tracking |
|------|-----------|-------------|---------------|-----------|--------------|---------------|
| CrewAI | No (code only) | Excellent | Yes | Partial | No | No |
| LangFlow | Yes | Weak | No (web) | Partial | No | No |
| Dify | Yes | Good | No (Docker) | Yes | No | Partial |
| **NeuralFlow** | **Yes** | **Excellent** | **Yes** | **Yes** | **Yes** | **Yes** |

---

## Features

### Visual Canvas
- Infinite drag-and-drop canvas powered by [React Flow](https://reactflow.dev)
- **10 node types**: Agent, Router, Human, Tool, MCP, Input, Output, Transform, Filter, Aggregator
- Connect nodes with directed edges — data flows automatically
- Auto-layout, undo/redo, copy/paste, multi-select
- Properties panel for inline editing of every node's configuration

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
| Any OpenAI-compatible API | Custom base URL |

API keys stored in your **OS keychain** — never on disk.

### Multi-Agent Orchestration
- **Sequential** — topological sort, left-to-right execution
- **Hierarchical** — manager agent delegates to workers via [CrewAI](https://github.com/crewAIInc/crewAI)
- **State Machine** — loops and conditional branching via [LangGraph](https://github.com/langchain-ai/langgraph)
- **Auto** — NeuralFlow inspects the graph and picks the right mode

### Built-in Tools
- Web search (Serper / Tavily / DuckDuckGo)
- File read/write (sandboxed to `~/neuralflow-files/`)
- HTTP requests (GET/POST/PUT/DELETE)
- Code execution, shell access
- **MCP Protocol**: connect any [Model Context Protocol](https://modelcontextprotocol.io) server (stdio, SSE)

### Live Run Log
- Real-time SSE stream of all agent activity
- Per-node status badges (idle → running → complete → error)
- Tool call inspection inline
- Cancel mid-execution

### Cost Tracking
- Per-node, per-run cost breakdown from LiteLLM
- Cost charts by day / workflow / model
- CSV export

### Debugging & Observability
- **Step-through Debug Replay**: Load any past run, re-run from any step
- **Run History**: Persistent log with status, duration, and cost
- **Version History**: Snapshot workflows, rollback to previous versions
- **Visual Diff Viewer**: Compare two workflow versions side-by-side
- **Auto-Debug AI**: When a workflow fails, an AI agent diagnoses the root cause and suggests fixes
- **Audit Log**: Complete audit trail of every API request for compliance
- **Notification Center**: Real-time alerts for run completions, failures, budget alerts, and HITL waiting
- **Connection Resilience**: Auto-reconnect with heartbeat monitoring and request queuing

### Cost Intelligence
- **Pre-Run Cost Estimation**: See estimated cost before running based on model pricing
- **Per-node, per-run cost breakdown** from LiteLLM
- **Cost charts** by day / workflow / model
- **Budget Quotas**: Set monthly/daily/per-run budgets with soft alerts and hard stops
- **CSV export**

### Developer Experience
- **Command Palette (Ctrl+K)**: Fuzzy-searchable commands for everything
- **Undo/Redo**: Full canvas history with Ctrl+Z / Ctrl+Shift+Z
- **Workflow Validation**: Real-time validation with inline error indicators
- **Prompt Optimizer**: Analyze system prompts for quality issues and auto-fix them
- **Keyboard Shortcuts**: Full keyboard navigation and operation
- **Enhanced Canvas Navigation**: Zoom controls, fit-view, minimap with node status coloring

### AI-Assisted Development
- **Prompt Optimizer**: Scores prompts 0-100, identifies issues, suggests improvements
- **Auto-Debug**: AI diagnoses workflow failures with root cause analysis and fix suggestions
- **Agent Memory**: Persistent context across runs with semantic search
- **Sub-Agent Spawning**: Agents can delegate to specialized sub-agents in parallel

### Enterprise & Security
- **Quota Management**: Budget limits, rate limiting per provider, spend alerts
- **Audit Logging**: Complete request audit trail with filtering and export
- **Structured Errors**: User-friendly error messages with recovery hints, never stack traces
- **Rate Limiting**: Per-IP sliding window with configurable overrides
- **Request Size Limits**: 10 MB default, 50 MB for upload endpoints

### Self-Hosting & Deployment
- **Docker Support**: Multi-stage Dockerfile with sidecar + frontend
- **Docker Compose**: One-command deployment with optional PostgreSQL
- **Health Checks**: Built-in container health monitoring
- **Reverse Proxy Ready**: Nginx configuration included in docs

### Template Gallery
- 5 built-in templates: Research Assistant, Content Writer, Code Reviewer, Data Analyzer, Web Scraper
- Community templates via GitHub Gist import

### Plugin System
- Install custom node types and tools via Python packages
- Hot-reload plugins without restarting

### Privacy First
- All data stays on your machine
- Sidecar listens only on `127.0.0.1`
- No telemetry by default
- Works fully offline with Ollama

### Security
- Rate limiting: per-IP sliding window
- Request size limits: 10 MB default
- Input validation: Pydantic schemas with `extra="forbid"`
- CORS hardening: explicit methods and headers (no wildcards)
- Structured logging with sensitive data redaction
- Auth tokens: SHA-256 hashed for remote sidecar access
- SQL injection safe: SQLAlchemy ORM with parameterized queries

---

## Quick Start

> 📖 Full documentation: [ssnelavala-masstcs.github.io/neuralflow](https://ssnelavala-masstcs.github.io/neuralflow/)

### Download Pre-built Binaries

Grab the latest release for your platform:

| Platform | Download |
|----------|----------|
| 🐧 Linux | [.deb](https://github.com/ssnelavala-masstcs/neuralflow/releases/latest) |
| 🍎 macOS (Apple Silicon) | [.dmg](https://github.com/ssnelavala-masstcs/neuralflow/releases/latest) |
| 🍎 macOS (Intel) | [.dmg](https://github.com/ssnelavala-masstcs/neuralflow/releases/latest) |
| 🪟 Windows | [.exe](https://github.com/ssnelavala-masstcs/neuralflow/releases/latest) |

### Build from Source

**Prerequisites**
- [Rust](https://rustup.rs/) (stable)
- [Node.js 22+](https://nodejs.org) + [pnpm](https://pnpm.io)
- [Python 3.11+](https://python.org) + [uv](https://github.com/astral-sh/uv)

### Build from Source

```bash
# 1. Clone the repo
git clone https://github.com/ssnelavala-masstcs/neuralflow
cd neuralflow

# 2. Install all dependencies
./scripts/setup-dev.sh

# 3. Launch the app
./scripts/dev.sh
```

The desktop window opens automatically. The Python sidecar starts on `localhost:7411`.

### Starter Templates

Five workflow templates ship out of the box:

| Template | What it does |
|----------|-------------|
| `research-assistant` | Web search → structured summary |
| `content-writer` | Outline planner → SEO blog post |
| `code-reviewer` | Parallel security + quality review |
| `data-analyzer` | File reader → statistical analysis |
| `web-scraper` | HTTP fetch → content extraction |

Load any template via the **Templates** menu in the app.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              NeuralFlow Desktop App              │
│                  (Tauri v2)                      │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │         React Frontend (Webview)          │  │
│  │   Canvas (React Flow) │ UI (Tailwind)    │  │
│  │   State (Zustand)     │ API Client        │  │
│  │   Command Palette     │ Error Handling    │  │
│  │   Undo/Redo           │ Validation        │  │
│  │   Cost Estimator      │ Notifications     │  │
│  │   Prompt Optimizer    │ Auto-Debug        │  │
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
│  ├── Sequential Executor          ✅              │
│  ├── CrewAI Executor (hierarchical) ✅            │
│  └── LangGraph Executor (state machine) ✅        │
│                                                    │
│  Services                                          │
│  ├── Cost Estimator       ✅  Pre-run pricing     │
│  ├── Quota Manager        ✅  Budgets & limits    │
│  ├── Notification Svc     ✅  Alerts & events     │
│  ├── Agent Memory         ✅  Persistent context  │
│  ├── Sub-Agent Manager    ✅  Parallel delegation  │
│  ├── Prompt Optimizer     ✅  Quality scoring     │
│  └── Auto-Debug           ✅  Failure diagnosis   │
│                                                    │
│  Middleware                                        │
│  ├── Rate Limiter         ✅  Sliding window      │
│  ├── Request Size         ✅  Payload limits      │
│  ├── Audit Logger         ✅  Request trail       │
│  └── Error Handler        ✅  Structured JSON     │
│                                                    │
│  LiteLLM · MCP Client · Built-in Tools            │
│  SQLite/PostgreSQL + SQLAlchemy · APScheduler     │
│  Plugin Loader · Replay Engine · Memory + RAG     │
└───────────────────────────────────────────────────┘
```

### Key Design Decisions

**Tauri v2 over Electron**: 3–10 MB binary vs 80–150 MB. OS-native webview. Rust backend for secure keychain access.

**Python sidecar**: Full access to the Python AI ecosystem (CrewAI, LangGraph, LiteLLM). Communicates via localhost HTTP + SSE.

**LiteLLM in-process**: Not a separate proxy — imported directly. Every new model LiteLLM supports is automatically available.

**SQLite only**: No Postgres, no Redis. One `.db` file per workspace. Works offline. Trivial to back up.

---

## Project Structure

```
neuralflow/
├── apps/desktop/              # Tauri v2 desktop app
│   ├── src-tauri/             # Rust backend (keychain, config)
│   └── src/                   # React 19 + TypeScript frontend
│       ├── canvas/            # React Flow nodes, edges, canvas
│       ├── components/        # UI components (cost, debug, properties…)
│       ├── stores/            # Zustand state stores
│       └── api/               # FastAPI client
│
├── packages/sidecar/          # Python FastAPI backend
│   └── neuralflow/
│       ├── api/               # FastAPI routers
│       ├── execution/         # Orchestrator, executors, replay
│       ├── tools/             # Built-in tools + registry
│       ├── mcp/               # MCP connection pool
│       ├── memory/            # RAG pipeline (sqlite-vec)
│       └── plugins/           # Plugin loader
│
├── templates/                 # 5 starter workflow templates
├── docs/                      # Documentation (GitHub Pages)
└── scripts/                   # Dev setup scripts
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop shell | [Tauri v2](https://tauri.app) (Rust) |
| Frontend | React 19 + TypeScript + Vite |
| Canvas | [React Flow / xyflow v12](https://reactflow.dev) |
| UI | [shadcn/ui](https://ui.shadcn.com) + Tailwind CSS v3 |
| State | [Zustand v5](https://zustand-demo.pmnd.rs) + Immer |
| Backend | [FastAPI](https://fastapi.tiangolo.com) + Python 3.11+ |
| Multi-agent | [CrewAI](https://crewai.com) + [LangGraph](https://langchain-ai.github.io/langgraph) |
| Model routing | [LiteLLM](https://litellm.ai) |
| Database | SQLite + [SQLAlchemy 2.0](https://sqlalchemy.org) |
| MCP | [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) |

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

- [React Flow / xyflow](https://github.com/xyflow/xyflow) — the canvas engine
- [Tauri](https://github.com/tauri-apps/tauri) — the desktop shell
- [LiteLLM](https://github.com/BerriAI/litellm) — model routing
- [CrewAI](https://github.com/crewAIInc/crewAI) — multi-agent orchestration
- [LangGraph](https://github.com/langchain-ai/langgraph) — stateful agent workflows
- [shadcn/ui](https://github.com/shadcn-ui/ui) — UI components
- [FastAPI](https://github.com/tiangolo/fastapi) — backend framework

---

<div align="center">

Built by **[Stanley Sujith Nelavala](https://github.com/ssnelavala-masstcs/neuralflow)**

</div>
