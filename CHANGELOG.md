# Changelog

All notable changes to NeuralFlow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.1.0] — 2026-04-02

Initial public release.

### Core
- Tauri v2 desktop shell with Python FastAPI sidecar on `localhost:7411`
- React Flow infinite canvas with 10 node types
- OS keychain integration for API key storage (macOS Keychain, Windows Credential Manager, Linux libsecret)
- Process lifecycle management (sidecar auto-start, health checks, graceful shutdown)

### Node Types
- **AgentNode** — LLM inference with configurable model, prompt, temperature, tools
- **RouterNode** — JavaScript expression-based conditional routing
- **HumanNode** — pause-and-resume with human input/approval
- **ToolNode** — deterministic tool invocation (web search, file I/O, HTTP, code exec, shell)
- **McpNode** — Model Context Protocol server integration (stdio + SSE)
- **InputNode** — workflow entry point with optional JSON Schema validation
- **OutputNode** — final output collection (raw, markdown, JSON)
- **TransformNode** — JavaScript data transformation
- **FilterNode** — conditional gate (pass/fail)
- **AggregatorNode** — parallel branch fan-in (merge, array, first)

### Execution
- Sequential executor (topological sort, parallel within levels)
- CrewAI hierarchical executor (manager delegates to workers)
- LangGraph state machine executor (cycles, retry loops, agentic patterns)
- Auto mode — inspects graph shape and picks the right executor
- SSE streaming for real-time run events (node_start, llm_chunk, tool_call, run_complete)
- Run cancel, replay from any step

### Model Providers
- LiteLLM in-process — supports OpenAI, Anthropic, DeepSeek, Groq, Mistral, Google Gemini, AWS Bedrock, Ollama, LM Studio, any OpenAI-compatible API
- Provider settings UI — add, edit, test, remove providers
- API keys stored in OS keychain, never on disk

### Memory & RAG
- Document ingestion (TXT, MD, PDF, DOCX) with configurable chunking
- Embedding via OpenAI `text-embedding-3-small` with FTS5 fallback
- Semantic search via `sqlite-vec` cosine similarity
- Memory panel for collection management

### Observability
- Live run log with per-node status badges
- Step-through debug replay — inspect LLM calls, tool results, re-run from any step
- Run history with status, duration, and cost
- Workflow version history with visual diff viewer
- Per-node, per-run, per-day cost tracking with CSV export

### Templates
- 5 built-in templates: Research Assistant, Content Writer, Code Reviewer, Data Analyzer, Web Scraper
- Community template gallery via GitHub Gist import
- Template import via API or UI

### Plugin System
- Python entry point-based plugin API (`neuralflow_plugins`)
- Register custom node types and tools
- Plugin browser in UI showing installed plugins, node types, tools, load status
- Hot-reload in development mode

### Security
- Rate limiting: per-IP sliding window (100 req/min general, 10 req/min execution)
- Request size limits: 10 MB default, 50 MB for uploads
- Input validation: Pydantic schemas with `extra="forbid"`
- CORS hardening: explicit methods and headers (no wildcards)
- Structured JSON logging with sensitive data redaction
- Auth tokens: SHA-256 hashed for remote sidecar access
- SQL injection safe: SQLAlchemy ORM with parameterized queries

### Documentation
- Full documentation site at [ssnelavala-masstcs.github.io/neuralflow](https://ssnelavala-masstcs.github.io/neuralflow/)
- Getting Started guide, Node Reference, Core Concepts, API Reference, User Guide
- Cyberpunk terminal-themed docs with glitch effects and animated grid background

### CI/CD
- GitHub Actions: cross-platform build (macOS aarch64/x86_64, Linux, Windows) on version tags
- Docs validation CI (HTML structure, internal links, author credits)
- Test CI (TypeScript typecheck, Python pytest)
- GitHub Pages deployment on docs changes

---
