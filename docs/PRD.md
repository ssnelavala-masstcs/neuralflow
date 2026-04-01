# NeuralFlow - Product Requirements Document and Technical Architecture

**App Name: NeuralFlow**

Rationale: "Neural" signals AI intelligence. "Flow" signals visual workflows and the flow-based programming paradigm. It is short, memorable, domain-appropriate, and not yet taken as a major open-source project. Alternatives if NeuralFlow is taken: **FlowMind** (second choice) or **Conduktor AI** (third).

---

## 1. Product Vision and Positioning

### Vision Statement

NeuralFlow is an open-source, local-first desktop application that makes multi-agent AI orchestration as accessible as drawing a flowchart. It bridges the gap between the power of code-first frameworks (CrewAI, LangGraph) and the accessibility of visual tools (Flowise, Dify), without requiring cloud infrastructure, Docker, or a computer science degree.

### The Core Problem

Every existing agent-building tool forces a painful trade-off:

| Tool | Visual | Multi-Agent Quality | Local/Desktop | Any Model | Good DX | Cost Tracking | Debug/Replay |
|---|---|---|---|---|---|---|---|
| CrewAI | No (code only) | Excellent | Yes | Partial | Moderate | No | No |
| LangFlow | Yes | Weak | No (web-only) | Partial | Poor | No | No |
| Flowise | Yes | Weak | Partial | Yes | Poor | No | No |
| Dify | Yes | Good | No (needs Docker) | Yes | Good | Partial | No |
| AutoGen Studio | Yes (immature) | Good | Partial | No (MS-locked) | Poor | No | No |
| n8n | Yes | No (not AI-native) | Yes | No | Good | No | No |
| **NeuralFlow** | **Yes** | **Excellent** | **Yes (Tauri)** | **Yes (LiteLLM)** | **Excellent** | **Yes** | **Yes** |

### Positioning Statement

NeuralFlow is for the technically-comfortable non-engineer: someone who can obtain an API key, install a desktop app, and wants to build powerful multi-agent workflows without writing Python or wrestling with Docker. It is also deeply useful for developers who want to prototype and debug agent systems visually before shipping them as code.

### What NeuralFlow is NOT

- Not a cloud SaaS product
- Not a code editor or IDE
- Not a replacement for writing production agent code (it can export to code, but is not a code runner)
- Not a general automation tool (it is AI-agent-specific)

---

## 2. Target User Personas

### Persona 1: "The Power User" - Alex, Product Manager at a Mid-Size Tech Company

- Background: Non-engineer, uses ChatGPT daily, has an OpenAI API key, understands what LLMs can do
- Goal: Build an internal research assistant that can browse the web, summarize documents, and draft reports autonomously
- Pain point: Can't use CrewAI (requires Python), Dify is too complex to self-host, cloud tools are expensive and raise data privacy concerns
- NeuralFlow fit: Drag-and-drop workflow, local execution, no cloud required, built-in cost tracking per run

### Persona 2: "The Prototype Builder" - Priya, ML Engineer / AI Developer

- Background: Writes Python, knows LangChain and CrewAI, builds internal tools
- Goal: Rapidly prototype multi-agent pipelines, test different model providers, debug agent behavior
- Pain point: CrewAI/LangGraph require full code setups; no way to visually inspect agent interaction; no replay of failed runs
- NeuralFlow fit: Visual canvas as a prototyping layer, export to CrewAI/LangGraph code, run replay and step-through debugger

### Persona 3: "The Independent Researcher" - Marcus, PhD Student in Computational Linguistics

- Background: Intermediate Python skills, runs models locally via Ollama, privacy-conscious
- Goal: Build document analysis pipelines that run entirely offline, using local Llama models
- Pain point: Existing tools phone home, require internet, or are too complex
- NeuralFlow fit: 100% local execution, Ollama support via LiteLLM, SQLite persistence, no telemetry by default

### Persona 4: "The Small Agency" - Sofia, Founder of a 5-Person Digital Agency

- Background: Non-technical, manages a small team, budget-conscious
- Goal: Deploy AI agents to automate client research, social media scheduling, and competitive analysis
- Pain point: SaaS tools are expensive per seat; wants to own her data; wants to share workflows with her team
- NeuralFlow fit: Export/import workflows as JSON, share via Git, built-in cost tracking to understand ROI

---

## 3. Complete Feature List

### 3.1 Core Canvas (P0 - Phase 1)

**Visual Workflow Canvas**
- Infinite zoomable/pannable canvas built on React Flow (xyflow)
- Drag nodes from a left sidebar palette onto the canvas
- Connect nodes with typed edges (data flow, control flow, message passing)
- Mini-map for large workflows
- Auto-layout button (Dagre/ELK layout algorithm)
- Canvas snapping grid with toggle
- Multi-select and group nodes
- Undo/redo with full history (Zustand + immer)
- Copy/paste nodes and sub-graphs
- Canvas zoom controls (keyboard shortcuts + scroll wheel)

**Node Types**
- Agent Node: Represents a single AI agent with a model, system prompt, and tool set
- Task Node: A discrete unit of work assigned to an agent
- Tool Node: An MCP tool, built-in tool, or custom Python function
- Trigger Node: HTTP webhook, cron schedule, file watch, manual button
- Router Node: Conditional branching (if/else, switch) based on agent output
- Memory Node: Shared memory store (vector search, key-value, conversation history)
- Human-in-the-loop Node: Pause execution and request human input/approval
- Aggregator Node: Collect outputs from parallel branches and merge them
- Output Node: Emit final workflow output (to file, webhook, clipboard, etc.)
- Subflow Node: Embed another workflow as a reusable node

**Edge Types**
- Data edge: Pass structured output from one node to the next
- Control edge: Determine execution order without passing data
- Conditional edge: Route based on boolean or expression evaluation

### 3.2 Agent Configuration (P0 - Phase 1)

**Model Provider Management**
- Provider panel with add/edit/remove entries
- Supported via LiteLLM: OpenAI, Anthropic, DeepSeek, Groq, Mistral, Cohere, Ollama (local), LM Studio (local), Azure OpenAI, AWS Bedrock, Google Gemini
- Per-provider API key storage (stored in OS keychain via Tauri keyring plugin, never in plaintext on disk)
- Connection test button with latency and model list verification
- Model selector with filtering by provider, context window size, and estimated cost per 1M tokens
- Custom base URL support for any OpenAI-compatible endpoint

**Agent Node Properties Panel**
- Name and description
- Model selector (with provider badge)
- System prompt editor (Monaco editor with markdown highlighting)
- Temperature, max tokens, top-p sliders
- Tool assignment (drag tools from palette or check from list)
- Memory attachment (select a Memory Node from canvas)
- Max iterations / recursion depth (guard against infinite loops)
- Verbose mode toggle (stream all inner thoughts to run log)
- Role selector: Researcher, Writer, Critic, Planner, Executor, Custom
- Allow delegation toggle (can this agent spawn sub-agents?)

### 3.3 Tool and MCP Management (P0 - Phase 1)

**Built-in Tools**
- Web search (via Serper, Tavily, or DuckDuckGo API)
- Web browser / scraper (Playwright headless, local execution)
- File read/write (sandboxed to user-specified directory)
- Python code executor (sandboxed subprocess via RestrictedPython or Docker if available)
- HTTP request tool (GET/POST with headers, auth)
- Calculator / data transformation (pandas, numpy in sidecar)
- Email reader/sender (IMAP/SMTP config)
- SQLite query tool (read from any local SQLite database)

**MCP Protocol Integration**
- MCP Server Manager: add stdio, SSE, HTTP MCP servers
- Transport support: stdio (local process), SSE, HTTP Streamable (MCP 2025-03-26 spec)
- Automatic capability discovery and tool registration
- MCP server status indicators (connected / failed / needs-auth)
- Official MCP registry browser (fetch from modelcontextprotocol/servers)
- Per-tool permission approval UI (approve once / approve always / deny)
- Tool result inspector: see raw JSON in/out for any tool call

**Custom Tool Builder**
- Simple Python function editor (Monaco) for quick custom tools
- JSON schema input/output definition
- Test harness: run the tool with sample input before attaching to an agent

### 3.4 Workflow Execution (P0 - Phase 1 / Phase 2)

**Run Panel**
- Run button with configurable input (JSON or natural language)
- Real-time streaming log of all agent activity
- Per-node status indicators (idle / running / waiting / complete / error)
- Animated edge highlighting showing active data flow
- Cancel / pause / resume execution
- Run progress timeline at bottom of canvas

**Execution Modes**
- Sequential: agents run one after another in topological order
- Parallel: independent branches run concurrently
- Hierarchical: a manager agent delegates to worker agents (CrewAI hierarchical process)
- State machine: LangGraph-backed stateful workflows with conditional transitions

**Input/Output**
- Run modal: user provides initial input before each run
- Scheduled runs: cron-based triggers fire without user input
- Webhook trigger: expose a local HTTP endpoint that starts a run
- Output viewer: formatted markdown/JSON result displayed in a side panel
- Export run output to file (Markdown, JSON, TXT)

### 3.5 Debugging and Observability (P0 - Phase 2)

**Run History**
- Persistent SQLite log of every run (start time, duration, cost, status)
- Click any past run to view its full trace
- Compare two runs side-by-side

**Step Debugger (Replay Mode)**
- Load a past run and step through it node by node
- See exact messages sent to and received from each model
- See exact tool calls and their results
- Inspect memory state at each step
- Re-run from any intermediate step (forks the run with new state)

**Token and Cost Dashboard**
- Per-run cost breakdown: total, per-agent, per-model
- Cumulative cost graph over time
- Token usage (input/output/cache read/cache write) per agent per run
- Estimated cost preview before running (based on prompt sizes and model pricing)
- Monthly spend summary

**Prompt Inspection**
- View the exact system prompt + message history sent to each LLM call
- Copy any prompt to clipboard
- Diff two prompts from different runs

### 3.6 Memory and RAG (Phase 2)

**Memory Node Types**
- Short-term: in-run conversation history (automatically managed)
- Long-term: ChromaDB or sqlite-vec vector store, persists across runs
- Shared buffer: key-value store, any agent in the workflow can read/write
- Entity memory: structured facts extracted from agent outputs, stored and queried

**RAG Pipeline**
- Document ingestion: PDF, TXT, Markdown, HTML, DOCX
- Chunk size and overlap configuration
- Embedding model selection (local via Ollama nomic-embed-text, or OpenAI text-embedding-3-small)
- Similarity search with threshold configuration
- Knowledge Base manager: view, search, and delete indexed documents

### 3.7 Workflow Management (P0 - Phase 1)

**Project System**
- Workspace: top-level container, one SQLite database per workspace
- Workflow: a named canvas, belongs to a workspace
- Multiple workflows per workspace, tabbed interface
- Workflow metadata: name, description, tags, last run, run count

**Import/Export**
- Export workflow to JSON (portable, version-controllable)
- Import workflow from JSON file
- Export workflow to CrewAI Python code (code generation)
- Export workflow to LangGraph Python code (code generation)
- Workflow template library: ship 10+ starter templates (research assistant, content pipeline, code review pipeline, etc.)
- Share to community (copy JSON to clipboard or open GitHub Gist)

**Version Control (Phase 3)**
- Built-in workflow versioning: snapshot on every save
- Diff viewer: visual diff between two versions of a workflow
- Rollback to any previous snapshot

### 3.8 Triggers and Scheduling (Phase 2)

- Manual trigger (button click)
- HTTP Webhook trigger (expose local port, configurable path and secret)
- Cron schedule trigger (visual cron builder)
- File watch trigger (watch a directory for new files)
- Inter-workflow trigger (one workflow calls another)

### 3.9 Settings and Configuration (P0 - Phase 1)

- Dark/light theme (system default respected)
- Keyboard shortcut reference panel
- Telemetry opt-in/out (default: off, fully anonymous if opted in)
- Python sidecar path configuration (for advanced users who want to use their own venv)
- Proxy settings (for corporate environments)
- Log level selector for debugging

---

## 4. Technical Architecture

### 4.1 High-Level Architecture

```
+-------------------------------------------------------------------+
|                        NEURALFLOW DESKTOP APP                     |
|                         (Tauri v2 Shell)                          |
|                                                                   |
|  +-------------------------------------------------------------+  |
|  |                   REACT FRONTEND (Webview)                  |  |
|  |                                                             |  |
|  |   +------------------+   +-----------------------------+   |  |
|  |   |  Canvas Layer    |   |   UI Shell Layer            |   |  |
|  |   |  (React Flow)    |   |   (shadcn/ui + Tailwind)    |   |  |
|  |   |                  |   |                             |   |  |
|  |   |  - Node renderer |   |  - Sidebar palette          |   |  |
|  |   |  - Edge renderer |   |  - Properties panel         |   |  |
|  |   |  - Canvas state  |   |  - Run log panel            |   |  |
|  |   |  - Interaction   |   |  - Settings modal           |   |  |
|  |   +------------------+   +-----------------------------+   |  |
|  |                                                             |  |
|  |   +-----------------------------------------------------+  |  |
|  |   |              STATE MANAGEMENT (Zustand)             |  |  |
|  |   |  workflowStore | runStore | settingsStore |         |  |  |
|  |   |  providerStore | mcpStore | costStore      |         |  |  |
|  |   +-----------------------------------------------------+  |  |
|  |                                                             |  |
|  |   +-----------------------------------------------------+  |  |
|  |   |           FRONTEND API CLIENT (REST + SSE)          |  |  |
|  |   |   Calls Python sidecar on localhost:7411            |  |  |
|  |   +-----------------------------------------------------+  |  |
|  +-------------------------------------------------------------+  |
|                                                                   |
|  +-------------------------------------------------------------+  |
|  |              TAURI RUST BRIDGE (IPC Commands)               |  |
|  |  - Sidecar process manager (spawn/kill Python FastAPI)      |  |
|  |  - OS Keychain access (API key storage)                     |  |
|  |  - File system access (read/write files)                    |  |
|  |  - System tray integration                                  |  |
|  |  - Auto-updater                                             |  |
|  +-------------------------------------------------------------+  |
|                                                                   |
+-------------------------------------------------------------------+
         |                              |
         | HTTP REST + SSE              | Tauri IPC
         v                              v
+-------------------+          +--------------------+
|  PYTHON SIDECAR   |          |  RUST NATIVE LAYER |
|  (FastAPI :7411)  |          |  (Tauri Commands)  |
|                   |          |                    |
|  /api/runs        |          |  - keyring get/set |
|  /api/workflows   |          |  - fs read/write   |
|  /api/providers   |          |  - process spawn   |
|  /api/mcp         |          |  - shell open      |
|  /api/memory      |          +--------------------+
|  /api/tools       |
|  /api/cost        |
|                   |
|  +-------------+  |
|  | Execution   |  |
|  | Engine      |  |
|  |             |  |
|  | CrewAI      |  |
|  | LangGraph   |  |
|  | LiteLLM     |  |
|  +-------------+  |
|                   |
|  +-------------+  |
|  | Persistence |  |
|  |             |  |
|  | SQLite      |  |
|  | SQLAlchemy  |  |
|  | ChromaDB /  |  |
|  | sqlite-vec  |  |
|  +-------------+  |
|                   |
|  +-------------+  |
|  | MCP Client  |  |
|  |             |  |
|  | stdio/SSE/  |  |
|  | HTTP        |  |
|  +-------------+  |
+-------------------+
         |
         v
+-------------------+         +---------------------+
| LiteLLM Proxy     |         | External MCP Servers|
| (in-process)      |         | (stdio / HTTP)      |
|                   |         |                     |
| - OpenAI          |         | - Filesystem MCP    |
| - Anthropic       |         | - Browser MCP       |
| - DeepSeek        |         | - GitHub MCP        |
| - Groq            |         | - Slack MCP         |
| - Ollama          |         | - Custom servers    |
| - LM Studio       |         +---------------------+
| - Azure OpenAI    |
| - AWS Bedrock     |
+-------------------+
```

### 4.2 Execution Engine Architecture

```
WORKFLOW EXECUTION REQUEST
         |
         v
+---------------------------+
|   ExecutionOrchestrator   |
|   (FastAPI endpoint)      |
|   POST /api/runs          |
+---------------------------+
         |
         | Analyzes workflow JSON
         | Determines execution strategy
         v
+------------------------------------+
|      WorkflowAnalyzer              |
|  - Topological sort nodes          |
|  - Detect parallel branches        |
|  - Identify execution strategy     |
|    (sequential/parallel/           |
|     hierarchical/state_machine)    |
+------------------------------------+
         |
   +-----+------+----------+
   |             |          |
   v             v          v
+--------+  +--------+  +----------+
|CrewAI  |  |LangGraph|  |Custom    |
|Executor|  |Executor |  |Sequential|
|        |  |         |  |Executor  |
|Handles:|  |Handles: |  |          |
|- hier- |  |- state  |  |Handles:  |
|  archy |  |  machine|  |- simple  |
|- role- |  |- loop   |  |  chains  |
|  based |  |  detect |  |          |
+--------+  +--------+  +----------+
   |             |          |
   +------+------+----------+
          |
          v
+---------------------------+
|    AgentRunner            |
|  - Calls LiteLLM          |
|  - Manages tool calls     |
|  - Streams events         |
|  - Records to SQLite      |
+---------------------------+
          |
     +----+----+
     |         |
     v         v
+--------+  +----------+
|LiteLLM |  |Tool       |
|Router  |  |Dispatcher |
|        |  |           |
|- routes|  |- MCP tools|
|  to any|  |- built-in |
|  model |  |- custom   |
+--------+  +----------+
```

### 4.3 Frontend Component Architecture

```
App.tsx
├── AppShell.tsx
│   ├── TitleBar.tsx (Tauri custom titlebar)
│   ├── Sidebar.tsx
│   │   ├── WorkflowList.tsx
│   │   ├── NodePalette.tsx
│   │   │   ├── AgentPaletteItem.tsx
│   │   │   ├── ToolPaletteItem.tsx
│   │   │   ├── TriggerPaletteItem.tsx
│   │   │   └── MemoryPaletteItem.tsx
│   │   └── ProjectTree.tsx
│   ├── Canvas.tsx (main ReactFlow wrapper)
│   │   ├── nodes/
│   │   │   ├── AgentNode.tsx
│   │   │   ├── TaskNode.tsx
│   │   │   ├── ToolNode.tsx
│   │   │   ├── TriggerNode.tsx
│   │   │   ├── RouterNode.tsx
│   │   │   ├── MemoryNode.tsx
│   │   │   ├── HumanNode.tsx
│   │   │   ├── AggregatorNode.tsx
│   │   │   ├── OutputNode.tsx
│   │   │   └── SubflowNode.tsx
│   │   ├── edges/
│   │   │   ├── DataEdge.tsx
│   │   │   ├── ControlEdge.tsx
│   │   │   └── ConditionalEdge.tsx
│   │   ├── CanvasControls.tsx
│   │   └── MiniMap.tsx
│   ├── PropertiesPanel.tsx (right sidebar)
│   │   ├── AgentProperties.tsx
│   │   ├── ToolProperties.tsx
│   │   ├── TriggerProperties.tsx
│   │   ├── MemoryProperties.tsx
│   │   └── EdgeProperties.tsx
│   └── BottomPanel.tsx
│       ├── RunLog.tsx
│       ├── CostBreakdown.tsx
│       └── RunHistory.tsx
├── Modals/
│   ├── RunModal.tsx
│   ├── ProviderSettingsModal.tsx
│   ├── MCPManagerModal.tsx
│   ├── TemplateLibrary.tsx
│   └── DebugReplayModal.tsx
└── Settings/
    ├── GeneralSettings.tsx
    ├── ProvidersSettings.tsx
    ├── MCPSettings.tsx
    └── KeyboardShortcuts.tsx
```

### 4.4 State Management Architecture (Zustand Stores)

```
workflowStore
  - workflows: Map<id, Workflow>
  - activeWorkflowId: string
  - nodes: Node[] (ReactFlow nodes)
  - edges: Edge[] (ReactFlow edges)
  - selectedNodeId: string | null
  - isDirty: boolean
  - history: WorkflowSnapshot[] (undo/redo)

runStore
  - activeRun: Run | null
  - runStatus: 'idle' | 'running' | 'paused' | 'complete' | 'error'
  - nodeStatuses: Map<nodeId, NodeRunStatus>
  - streamEvents: StreamEvent[]
  - runHistory: RunSummary[]

settingsStore
  - theme: 'dark' | 'light' | 'system'
  - telemetryEnabled: boolean
  - sidecarPort: number
  - pythonPath: string
  - shortcuts: KeybindingMap

providerStore
  - providers: Provider[]
  - selectedProvider: string
  - models: Map<providerId, Model[]>
  - connectionStatus: Map<providerId, 'ok' | 'error' | 'untested'>

mcpStore
  - servers: McpServer[]
  - serverStatus: Map<serverId, McpServerStatus>
  - discoveredTools: Map<serverId, McpTool[]>

costStore
  - currentRunCost: RunCostBreakdown | null
  - totalCostAllTime: number
  - costHistory: CostRecord[]
  - modelPricing: Map<modelId, ModelPricing>
```

---

## 5. Database Schema

The Python sidecar owns the SQLite database. SQLAlchemy is the ORM. One file per workspace: `~/.neuralflow/workspaces/<workspace_id>/data.db`.

### 5.1 Core Tables

```sql
-- Workspaces (top-level containers)
CREATE TABLE workspaces (
    id          TEXT PRIMARY KEY,        -- UUID
    name        TEXT NOT NULL,
    description TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    settings    JSON                      -- workspace-level overrides
);

-- Workflows (canvas documents)
CREATE TABLE workflows (
    id              TEXT PRIMARY KEY,     -- UUID
    workspace_id    TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    tags            JSON,                 -- ["research", "production"]
    canvas_data     JSON NOT NULL,        -- full ReactFlow nodes + edges JSON
    execution_mode  TEXT NOT NULL DEFAULT 'sequential',
                                          -- sequential | parallel | hierarchical | state_machine
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_run_at     DATETIME,
    run_count       INTEGER NOT NULL DEFAULT 0,
    is_template     BOOLEAN NOT NULL DEFAULT FALSE
);

-- Workflow snapshots (version history)
CREATE TABLE workflow_snapshots (
    id              TEXT PRIMARY KEY,
    workflow_id     TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    snapshot_number INTEGER NOT NULL,
    canvas_data     JSON NOT NULL,
    change_summary  TEXT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Runs (execution records)
CREATE TABLE runs (
    id              TEXT PRIMARY KEY,     -- UUID
    workflow_id     TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    workflow_snapshot JSON NOT NULL,      -- copy of canvas_data at run time (for replay)
    status          TEXT NOT NULL,        -- queued | running | paused | complete | error | cancelled
    trigger_type    TEXT NOT NULL,        -- manual | scheduled | webhook | inter_workflow
    input_data      JSON,                 -- user-provided input
    output_data     JSON,                 -- final output
    error_message   TEXT,
    started_at      DATETIME,
    completed_at    DATETIME,
    duration_ms     INTEGER,
    total_cost_usd  REAL NOT NULL DEFAULT 0.0,
    total_input_tokens  INTEGER NOT NULL DEFAULT 0,
    total_output_tokens INTEGER NOT NULL DEFAULT 0,
    metadata        JSON
);

-- Node run traces (per-node execution details within a run)
CREATE TABLE node_runs (
    id              TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    node_id         TEXT NOT NULL,        -- references canvas node id
    node_type       TEXT NOT NULL,        -- agent | tool | trigger | router | etc.
    node_name       TEXT NOT NULL,
    status          TEXT NOT NULL,        -- pending | running | complete | error | skipped
    started_at      DATETIME,
    completed_at    DATETIME,
    duration_ms     INTEGER,
    input_data      JSON,
    output_data     JSON,
    error_message   TEXT,
    cost_usd        REAL NOT NULL DEFAULT 0.0,
    input_tokens    INTEGER NOT NULL DEFAULT 0,
    output_tokens   INTEGER NOT NULL DEFAULT 0
);

-- LLM call traces (every single API call within a run)
CREATE TABLE llm_calls (
    id              TEXT PRIMARY KEY,
    node_run_id     TEXT NOT NULL REFERENCES node_runs(id) ON DELETE CASCADE,
    run_id          TEXT NOT NULL,        -- denormalized for fast queries
    provider        TEXT NOT NULL,        -- openai | anthropic | groq | etc.
    model           TEXT NOT NULL,
    call_index      INTEGER NOT NULL,     -- 0-based index of call within node run
    messages        JSON NOT NULL,        -- full messages array sent
    response        JSON NOT NULL,        -- full API response received
    input_tokens    INTEGER NOT NULL DEFAULT 0,
    output_tokens   INTEGER NOT NULL DEFAULT 0,
    cache_read_tokens   INTEGER NOT NULL DEFAULT 0,
    cache_write_tokens  INTEGER NOT NULL DEFAULT 0,
    cost_usd        REAL NOT NULL DEFAULT 0.0,
    latency_ms      INTEGER,
    finish_reason   TEXT,
    error           TEXT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tool call traces
CREATE TABLE tool_calls (
    id              TEXT PRIMARY KEY,
    llm_call_id     TEXT REFERENCES llm_calls(id) ON DELETE CASCADE,
    node_run_id     TEXT NOT NULL REFERENCES node_runs(id) ON DELETE CASCADE,
    run_id          TEXT NOT NULL,        -- denormalized
    tool_name       TEXT NOT NULL,
    tool_source     TEXT NOT NULL,        -- builtin | mcp:<server_name> | custom
    input_data      JSON NOT NULL,
    output_data     JSON,
    error           TEXT,
    latency_ms      INTEGER,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Providers (model provider configurations, API keys stored in OS keychain)
CREATE TABLE providers (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE, -- "My OpenAI", "Local Ollama"
    provider_type   TEXT NOT NULL,        -- openai | anthropic | groq | ollama | litellm_proxy | etc.
    base_url        TEXT,                 -- overrides default for custom endpoints
    api_key_ref     TEXT,                 -- keychain reference key, NOT the actual key
    default_model   TEXT,
    extra_config    JSON,                 -- provider-specific fields
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- MCP server configurations
CREATE TABLE mcp_servers (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    transport       TEXT NOT NULL,        -- stdio | sse | http
    command         TEXT,                 -- for stdio: command to run
    args            JSON,                 -- for stdio: argument list
    url             TEXT,                 -- for sse/http: endpoint URL
    env_vars        JSON,                 -- environment variables to pass
    headers         JSON,                 -- HTTP headers
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_connected_at DATETIME,
    capabilities    JSON,                 -- cached capabilities from last connection
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Memory / Knowledge Base stores
CREATE TABLE memory_stores (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    store_type      TEXT NOT NULL,        -- vector | kv | entity | conversation
    backend         TEXT NOT NULL,        -- chromadb | sqlite_vec | in_memory
    collection_name TEXT,                 -- for ChromaDB
    embedding_model TEXT,                 -- model used for indexing
    embedding_provider TEXT,             -- provider for embedding model
    config          JSON,
    document_count  INTEGER NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Scheduled triggers
CREATE TABLE scheduled_triggers (
    id              TEXT PRIMARY KEY,
    workflow_id     TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    cron_expression TEXT NOT NULL,
    input_data      JSON,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_fired_at   DATETIME,
    next_fire_at    DATETIME,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Webhook triggers
CREATE TABLE webhook_triggers (
    id              TEXT PRIMARY KEY,
    workflow_id     TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    path            TEXT NOT NULL UNIQUE, -- e.g. /hooks/my-workflow
    secret_key_ref  TEXT,                 -- keychain reference for HMAC verification
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_called_at  DATETIME,
    call_count      INTEGER NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Cost summaries (materialized for fast dashboard queries)
CREATE TABLE daily_cost_summaries (
    date            TEXT NOT NULL,        -- YYYY-MM-DD
    provider        TEXT NOT NULL,
    model           TEXT NOT NULL,
    run_count       INTEGER NOT NULL DEFAULT 0,
    total_cost_usd  REAL NOT NULL DEFAULT 0.0,
    total_input_tokens  INTEGER NOT NULL DEFAULT 0,
    total_output_tokens INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (date, provider, model)
);

-- Indexes
CREATE INDEX idx_runs_workflow ON runs(workflow_id, started_at DESC);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_node_runs_run ON node_runs(run_id);
CREATE INDEX idx_llm_calls_run ON llm_calls(run_id);
CREATE INDEX idx_llm_calls_node_run ON llm_calls(node_run_id);
CREATE INDEX idx_tool_calls_run ON tool_calls(run_id);
CREATE INDEX idx_tool_calls_node_run ON tool_calls(node_run_id);
```

---

## 6. Full Tech Stack with Reasoning

### 6.1 Desktop Shell

**Tauri v2** (Rust + OS WebView)
- Binary size: 3-10 MB (vs Electron's 80-150 MB)
- Memory footprint: ~30 MB idle (vs Electron's 100-200 MB)
- OS-native: uses WebKit on macOS/Linux, WebView2 on Windows
- Rust layer provides: native file system access, OS keychain (via tauri-plugin-keyring), system tray, auto-updater, process management (sidecar spawning)
- v2 is stable as of January 2025 with a dramatically improved plugin API
- Security: IPC allowlist prevents frontend from calling arbitrary Rust commands; each command is explicitly declared

### 6.2 Frontend

**React 19 + TypeScript**
- React 19's concurrent features (use, Suspense improvements) benefit large canvas renders
- TypeScript provides compile-time safety for the complex node/edge type system

**Vite**
- Sub-second HMR, ideal for UI-heavy development
- Tauri has first-class Vite integration via @tauri-apps/cli

**React Flow / xyflow v12**
- The de facto standard for node-based editors in React
- Handles: infinite canvas, pan/zoom, node dragging, edge routing, mini-map, custom node/edge renderers
- Performance: virtualization via viewport culling handles 500+ nodes
- xyflow is the open-source version (Apache 2.0 license)
- Already used by: Flowise, LangFlow, Stripe Radar, etc.

**Tailwind CSS v4 + shadcn/ui**
- Tailwind v4: CSS-first configuration, faster builds, better IDE support
- shadcn/ui: copy-paste component library (not a dependency), fully customizable, built on Radix UI primitives for accessibility
- Together: rapid UI development without fighting a design system

**Zustand v5**
- Minimal boilerplate, works outside React components (useful for IPC event handlers)
- Excellent DevTools integration
- Immer middleware for immutable state updates (critical for undo/redo)
- Better performance than Redux for this use case (fine-grained subscriptions)

**Monaco Editor**
- Used for: system prompt editing, custom tool code editing, JSON config editing
- Same editor as VS Code, familiar to developers
- Smaller footprint via @monaco-editor/react with lazy loading

### 6.3 Backend Sidecar

**Python 3.11+ FastAPI**
- FastAPI: async-first, automatic OpenAPI docs, Pydantic v2 for request/response validation
- Runs as a sidecar spawned by Tauri on startup, listens on localhost:7411 (configurable)
- Server-Sent Events (SSE) for streaming run logs to the frontend
- WebSocket fallback for bidirectional communication (human-in-the-loop nodes)

**LiteLLM**
- Used in-process (not as a separate server) via `litellm.completion()`
- Provides: unified OpenAI-compatible interface to 100+ LLMs, automatic retry logic, fallback providers, cost tracking via `litellm.get_model_cost_map()`, streaming support
- Key advantage: when a user adds a new provider (e.g. "Together AI"), zero code changes are needed in NeuralFlow - LiteLLM handles the API translation

**CrewAI**
- Used for: hierarchical multi-agent processes, role-based agent definitions, task delegation
- Integration point: the `CrewAIExecutor` converts NeuralFlow's JSON workflow into `Crew`, `Agent`, and `Task` Python objects and executes them
- CrewAI's `Process.hierarchical` is used when the workflow has a designated manager agent

**LangGraph**
- Used for: stateful workflows, cyclic graphs (loops), explicit state machine patterns
- Integration point: the `LangGraphExecutor` compiles the workflow into a `StateGraph`, adds conditional edges from Router Nodes, and streams events via `graph.astream()`
- LangGraph's checkpointer is backed by SQLite for persistence

**SQLAlchemy 2.0 + aiosqlite**
- Async SQLAlchemy for non-blocking database operations in FastAPI
- Single SQLite file per workspace: no installation, no server, works offline
- Alembic for schema migrations (upgrade path for future releases)

**ChromaDB / sqlite-vec**
- Phase 1: sqlite-vec (zero-dependency, embedded in SQLite file, good enough for most use cases)
- Phase 2: ChromaDB as an optional upgrade for users with large knowledge bases (>100K documents)
- Vector dimensions: 1536 (OpenAI) or 768 (nomic-embed-text via Ollama)

**APScheduler**
- Async-capable scheduler for cron triggers
- Persists job state to SQLite so scheduled runs survive app restarts

### 6.4 MCP Integration

**mcp Python SDK** (`mcp>=1.0.0`)
- Official Python MCP client for connecting to stdio/SSE/HTTP MCP servers
- Used inside the Python sidecar to discover tools, send requests, receive results
- Tool results are forwarded to the executing agent via LiteLLM tool_calls mechanism

---

## 7. Development Phases and Roadmap

### Phase 1: Core MVP — ✅ COMPLETE (2026-03-31)

Goal: A working visual agent builder that can run basic multi-agent workflows with any OpenAI-compatible model.

**Milestone 1.1 - Tauri Shell + Sidecar** ✅
- [x] Tauri v2 project scaffold with Vite + React 19 (`apps/desktop/`)
- [x] Python FastAPI sidecar on `localhost:7411`, started via `scripts/dev.sh`
- [x] Health check: frontend polls `GET /health` on startup, shows "Connecting to sidecar…" until ready
- [x] Basic IPC: keychain `get`/`set`/`delete` via Tauri `keyring` crate (`src-tauri/src/commands/keychain.rs`)
- [ ] Settings modal UI (Phase 2 polish item)

**Milestone 1.2 - Canvas Foundation** ✅
- [x] React Flow (xyflow v12) with all **10 custom node types**: Agent, Task, Tool, Trigger, Router, Memory, Human, Aggregator, Output, Subflow
- [x] Node palette sidebar with drag-to-canvas (`dataTransfer "application/neuralflow-node"`)
- [x] DataEdge, ControlEdge, ConditionalEdge with custom bezier renderers
- [x] Save/load canvas JSON via `PATCH /api/workflows/:id`
- [ ] PropertiesPanel (inline editing of agent model/prompt/temperature) — Phase 2

**Milestone 1.3 - Provider and Model Management** ✅
- [x] Provider CRUD REST API (`/api/providers`) + `providerStore` (Zustand)
- [x] `GET /api/providers/:id/models` — live for Ollama, static hints for cloud providers
- [x] Connection test endpoint per provider (`POST /api/providers/:id/test`)
- [x] API keys stored as keychain references only; never written to SQLite

**Milestone 1.4 - Basic Execution Engine** ✅
- [x] `POST /api/runs` → sequential executor → topological sort → LiteLLM agent loop
- [x] Full tool-call iteration loop (up to 20 iterations per agent, guarded)
- [x] SSE event stream (`GET /api/runs/:id/stream`) via asyncio.Queue per run
- [x] Per-node status events: `node_started`, `node_completed`, `node_failed`
- [x] Cost tracking: per-node and per-run totals rolled up from LiteLLM usage data
- [x] Run cancel endpoint (`POST /api/runs/:id/cancel`)

**Milestone 1.5 - Built-in Tools** ✅
- [x] `web_search` — Serper → Tavily → DuckDuckGo fallback chain
- [x] `file_read`, `file_write`, `file_list` — sandboxed to `~/neuralflow-files/`
- [x] `http_request` — GET/POST/PUT/DELETE, JSON + text response handling
- [x] `calculator` — safe AST evaluator (no `eval`)
- [x] Tool registry (`tools/registry.py`) with auto-conversion to LiteLLM tool format

**Milestone 1.6 - MCP Integration** ✅
- [x] MCP server CRUD API (`/api/mcp/servers`)
- [x] stdio and SSE/HTTP transport support via official `mcp` Python SDK
- [x] `POST /api/mcp/servers/:id/connect` — discovers tools, caches capabilities in SQLite
- [x] Module-level connection pool (`mcp/manager.py`)

**Milestone 1.7 - Workflow Management** ✅
- [x] Multiple workflows per workspace, listed and switchable in Sidebar
- [x] Full canvas JSON import/export via REST API
- [x] 5 starter templates: `research-assistant`, `content-writer`, `code-reviewer`, `data-analyzer`, `web-scraper`
- [x] Template API: `GET /api/templates`, `POST /api/templates/:file/import`

**Phase 1 Deliverable**: All core infrastructure shipped. Canvas, execution engine, tools, and MCP are wired end-to-end. Phase 2 work begins next.

---

### Phase 2: Power Features (Months 4-6)

**Milestone 2.1 - CrewAI and LangGraph Executors**
- CrewAI executor for hierarchical workflows (manager + worker agent pattern)
- LangGraph executor for state machine workflows with Router Nodes
- Execution mode selector per workflow
- Documentation: when to use which executor

**Milestone 2.2 - Debugging and Replay**
- Run history list with click-to-inspect
- Step debugger: step through node_runs one at a time
- Message inspector: view exact LLM messages for any llm_call
- Tool call inspector: view exact tool input/output
- Re-run from checkpoint: fork a past run from any intermediate state

**Milestone 2.3 - Memory and RAG**
- MemoryNode canvas node
- Document ingestion panel (PDF, TXT, MD, DOCX)
- sqlite-vec embedded vector store
- Agent memory attachment in properties panel
- Entity memory extraction (auto-extracted from agent outputs)

**Milestone 2.4 - Cost Dashboard**
- Full cost analytics page (separate from canvas)
- Charts: cost per day, cost per workflow, cost per model
- Budget alerts: notify when run exceeds threshold
- Export cost report as CSV

**Milestone 2.5 - Scheduling and Webhooks**
- Cron TriggerNode with visual cron builder
- Webhook TriggerNode with local HTTP server
- File watch TriggerNode
- Scheduled runs managed by APScheduler, persisted in SQLite

**Milestone 2.6 - Human-in-the-Loop**
- HumanNode on canvas: pauses execution and shows approval UI
- Notifications via OS toast (Tauri notification plugin)
- Resume workflow with human input injected into agent context

**Phase 2 Deliverable**: v0.5.0 stable release. Community launch on Product Hunt, Hacker News.

---

### Phase 3: Ecosystem and Polish (Months 7-10)

**Milestone 3.1 - Code Export**
- Export workflow to CrewAI Python script (complete, runnable)
- Export workflow to LangGraph Python script
- Syntax-highlighted preview before export

**Milestone 3.2 - Workflow Version History**
- Visual diff between two workflow snapshots
- Rollback to any snapshot
- Snapshot naming

**Milestone 3.3 - Plugin System**
- Plugin API: third-party developers can ship additional node types
- Node plugin format: Python backend class + React frontend component, packaged as a Python package
- Plugin registry browser in-app

**Milestone 3.4 - Team Workflow Sharing**
- One-click export to GitHub Gist
- Import from URL (Gist or raw JSON)
- Community template gallery (curated, hosted on GitHub)

**Milestone 3.5 - Performance and Scale**
- Canvas performance: virtualization improvements for 200+ node workflows
- Large workflow support: paginated run history
- Streaming optimization: backpressure handling for long-running agents

**Phase 3 Deliverable**: v1.0.0 stable release. Plugin ecosystem seed partnerships.

---

### Phase 4: Enterprise and Advanced Features (Months 11-16)

**Milestone 4.1 - Multi-Workspace and Team Mode**
- Multiple workspace profiles
- Workspace export/import as zip bundle

**Milestone 4.2 - Advanced Memory**
- ChromaDB upgrade path
- Cross-workflow shared memory pools
- Memory visualization: graph of entities and relationships

**Milestone 4.3 - Evaluation Framework**
- Run a workflow against a test set (input/expected output pairs)
- Automated evaluation metrics (ROUGE, LLM-as-judge)
- A/B testing: compare two workflow variants on same test set

**Milestone 4.4 - Remote Execution Option**
- Optional: send workflow to a remote FastAPI instance instead of local sidecar
- This enables team-shared execution without each person running the full Python stack

**Phase 4 Deliverable**: v2.0.0 with enterprise readiness.

---

## 8. File and Folder Structure

```
neuralflow/
├── .github/
│   ├── workflows/
│   │   ├── build.yml              # Tauri build for all platforms
│   │   ├── test.yml               # Frontend + backend tests
│   │   └── release.yml            # Create GitHub release + upload installers
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── apps/
│   └── desktop/                   # Tauri application root
│       ├── src-tauri/             # Rust backend
│       │   ├── src/
│       │   │   ├── main.rs        # Tauri app entry, sidecar spawn, window setup
│       │   │   ├── commands/
│       │   │   │   ├── keychain.rs    # keyring get/set/delete
│       │   │   │   ├── filesystem.rs  # sandboxed file ops
│       │   │   │   └── sidecar.rs     # Python process management
│       │   │   └── lib.rs
│       │   ├── capabilities/
│       │   │   └── default.json   # Tauri v2 capability definitions
│       │   ├── icons/
│       │   ├── tauri.conf.json    # Tauri config: bundle ID, window, sidecar
│       │   └── Cargo.toml
│       │
│       ├── src/                   # React frontend
│       │   ├── main.tsx           # React entry point
│       │   ├── App.tsx
│       │   │
│       │   ├── canvas/            # React Flow canvas layer
│       │   │   ├── Canvas.tsx
│       │   │   ├── nodes/
│       │   │   │   ├── AgentNode.tsx
│       │   │   │   ├── TaskNode.tsx
│       │   │   │   ├── ToolNode.tsx
│       │   │   │   ├── TriggerNode.tsx
│       │   │   │   ├── RouterNode.tsx
│       │   │   │   ├── MemoryNode.tsx
│       │   │   │   ├── HumanNode.tsx
│       │   │   │   ├── AggregatorNode.tsx
│       │   │   │   ├── OutputNode.tsx
│       │   │   │   ├── SubflowNode.tsx
│       │   │   │   └── index.ts   # nodeTypes registry
│       │   │   ├── edges/
│       │   │   │   ├── DataEdge.tsx
│       │   │   │   ├── ControlEdge.tsx
│       │   │   │   ├── ConditionalEdge.tsx
│       │   │   │   └── index.ts   # edgeTypes registry
│       │   │   └── hooks/
│       │   │       ├── useCanvasActions.ts
│       │   │       └── useLayoutEngine.ts
│       │   │
│       │   ├── components/        # UI components
│       │   │   ├── layout/
│       │   │   │   ├── AppShell.tsx
│       │   │   │   ├── TitleBar.tsx
│       │   │   │   ├── Sidebar.tsx
│       │   │   │   └── BottomPanel.tsx
│       │   │   ├── palette/
│       │   │   │   ├── NodePalette.tsx
│       │   │   │   └── PaletteItem.tsx
│       │   │   ├── properties/
│       │   │   │   ├── PropertiesPanel.tsx
│       │   │   │   ├── AgentProperties.tsx
│       │   │   │   ├── ToolProperties.tsx
│       │   │   │   ├── TriggerProperties.tsx
│       │   │   │   └── MemoryProperties.tsx
│       │   │   ├── run/
│       │   │   │   ├── RunLog.tsx
│       │   │   │   ├── RunHistory.tsx
│       │   │   │   └── RunModal.tsx
│       │   │   ├── cost/
│       │   │   │   ├── CostBreakdown.tsx
│       │   │   │   └── CostDashboard.tsx
│       │   │   ├── debug/
│       │   │   │   ├── DebugReplayModal.tsx
│       │   │   │   ├── MessageInspector.tsx
│       │   │   │   └── ToolCallInspector.tsx
│       │   │   └── ui/            # shadcn/ui component copies
│       │   │
│       │   ├── modals/
│       │   │   ├── ProviderSettingsModal.tsx
│       │   │   ├── MCPManagerModal.tsx
│       │   │   └── TemplateLibrary.tsx
│       │   │
│       │   ├── stores/            # Zustand stores
│       │   │   ├── workflowStore.ts
│       │   │   ├── runStore.ts
│       │   │   ├── settingsStore.ts
│       │   │   ├── providerStore.ts
│       │   │   ├── mcpStore.ts
│       │   │   └── costStore.ts
│       │   │
│       │   ├── api/               # Frontend API client
│       │   │   ├── client.ts      # axios/fetch base config
│       │   │   ├── workflows.ts
│       │   │   ├── runs.ts
│       │   │   ├── providers.ts
│       │   │   ├── mcp.ts
│       │   │   ├── memory.ts
│       │   │   └── cost.ts
│       │   │
│       │   ├── hooks/
│       │   │   ├── useRunStream.ts    # SSE hook for run events
│       │   │   ├── useKeyboard.ts
│       │   │   └── useTheme.ts
│       │   │
│       │   ├── types/
│       │   │   ├── workflow.ts    # Workflow, Node, Edge type definitions
│       │   │   ├── run.ts         # Run, NodeRun, LlmCall type definitions
│       │   │   ├── provider.ts
│       │   │   ├── mcp.ts
│       │   │   └── cost.ts
│       │   │
│       │   └── lib/
│       │       ├── tauri.ts       # Tauri IPC wrappers
│       │       ├── layout.ts      # Dagre/ELK auto-layout helpers
│       │       └── utils.ts
│       │
│       ├── index.html
│       ├── vite.config.ts
│       ├── tailwind.config.ts
│       ├── tsconfig.json
│       └── package.json
│
├── packages/
│   └── sidecar/                   # Python FastAPI backend
│       ├── neuralflow/
│       │   ├── __init__.py
│       │   ├── main.py            # FastAPI app, router registration, startup
│       │   ├── config.py          # Settings via pydantic-settings
│       │   ├── database.py        # SQLAlchemy engine, session factory
│       │   │
│       │   ├── api/               # FastAPI routers
│       │   │   ├── workflows.py   # CRUD for workflows
│       │   │   ├── runs.py        # Start, cancel, get runs; SSE stream
│       │   │   ├── providers.py   # Provider CRUD + model listing
│       │   │   ├── mcp.py         # MCP server management + tool discovery
│       │   │   ├── memory.py      # Memory store management + document ingestion
│       │   │   ├── tools.py       # Built-in tool registry + custom tools
│       │   │   ├── cost.py        # Cost analytics endpoints
│       │   │   └── health.py      # Health check
│       │   │
│       │   ├── models/            # SQLAlchemy ORM models
│       │   │   ├── base.py
│       │   │   ├── workspace.py
│       │   │   ├── workflow.py
│       │   │   ├── run.py
│       │   │   ├── provider.py
│       │   │   ├── mcp_server.py
│       │   │   └── memory_store.py
│       │   │
│       │   ├── schemas/           # Pydantic request/response schemas
│       │   │   ├── workflow.py
│       │   │   ├── run.py
│       │   │   ├── provider.py
│       │   │   ├── mcp.py
│       │   │   └── cost.py
│       │   │
│       │   ├── execution/         # Agent execution engine
│       │   │   ├── orchestrator.py        # Top-level run dispatcher
│       │   │   ├── workflow_analyzer.py   # Parse canvas JSON, detect strategy
│       │   │   ├── sequential_executor.py # Simple chain execution
│       │   │   ├── crewai_executor.py     # CrewAI integration
│       │   │   ├── langgraph_executor.py  # LangGraph integration
│       │   │   ├── agent_runner.py        # Single agent execution (LiteLLM loop)
│       │   │   ├── tool_dispatcher.py     # Route tool calls to built-in or MCP
│       │   │   ├── event_emitter.py       # SSE event stream management
│       │   │   └── replay_engine.py       # Replay from SQLite checkpoint
│       │   │
│       │   ├── tools/             # Built-in tool implementations
│       │   │   ├── base.py        # BaseTool abstract class
│       │   │   ├── web_search.py
│       │   │   ├── web_browser.py
│       │   │   ├── file_ops.py
│       │   │   ├── http_request.py
│       │   │   ├── code_executor.py
│       │   │   ├── calculator.py
│       │   │   └── sqlite_query.py
│       │   │
│       │   ├── mcp/               # MCP client management
│       │   │   ├── manager.py     # MCP connection pool
│       │   │   ├── stdio_client.py
│       │   │   ├── http_client.py
│       │   │   └── tool_adapter.py # Convert MCP tools to LiteLLM tool_calls format
│       │   │
│       │   ├── memory/            # Memory and RAG
│       │   │   ├── manager.py
│       │   │   ├── sqlite_vec_store.py
│       │   │   ├── chroma_store.py
│       │   │   ├── kv_store.py
│       │   │   └── entity_extractor.py
│       │   │
│       │   ├── scheduling/
│       │   │   ├── scheduler.py   # APScheduler setup
│       │   │   └── webhook_server.py # Starlette sub-app for webhook endpoints
│       │   │
│       │   └── migrations/        # Alembic migrations
│       │       ├── env.py
│       │       └── versions/
│       │
│       ├── tests/
│       │   ├── test_execution/
│       │   ├── test_mcp/
│       │   └── test_api/
│       │
│       ├── pyproject.toml         # uv / pip dependencies
│       └── requirements.txt       # pinned for reproducibility
│
├── templates/                     # Starter workflow JSON files
│   ├── research-assistant.json
│   ├── content-writer.json
│   ├── code-reviewer.json
│   ├── data-analyzer.json
│   └── web-scraper.json
│
├── docs/
│   ├── architecture.md
│   ├── contributing.md
│   ├── plugin-api.md
│   └── user-guide/
│
├── scripts/
│   ├── build-sidecar.sh           # Build Python into bundled binary (PyInstaller)
│   ├── dev.sh                     # Start both Tauri dev + Python dev server
│   └── setup-dev.sh               # Install all dev dependencies
│
├── LICENSE                        # Apache 2.0
├── README.md
└── CONTRIBUTING.md
```

---

## 9. Key Integration Points

### 9.1 LiteLLM Integration

LiteLLM is used **in-process** inside the Python sidecar, not as a separate proxy server. This is the critical architectural decision that keeps the deployment simple.

```python
# packages/sidecar/neuralflow/execution/agent_runner.py (conceptual)

import litellm
from litellm import completion, acompletion

class AgentRunner:
    async def run_agent_step(
        self,
        agent_config: AgentNodeConfig,
        messages: list[dict],
        tools: list[dict],
        api_key: str,  # retrieved from Tauri keychain, passed per-call
    ) -> AgentStepResult:

        response = await acompletion(
            model=agent_config.model,           # "openai/gpt-4o", "groq/llama-3.3-70b", etc.
            messages=messages,
            tools=tools if tools else None,
            temperature=agent_config.temperature,
            max_tokens=agent_config.max_tokens,
            api_key=api_key,
            api_base=agent_config.provider_base_url,  # for custom/Ollama endpoints
            stream=True,
            # LiteLLM cost tracking:
            metadata={"run_id": run_id, "node_id": node_id},
        )

        # LiteLLM provides usage and cost automatically:
        # response.usage.prompt_tokens, completion_tokens
        # litellm.completion_cost(completion_response=response)
```

**LiteLLM model string format** (no changes needed for new providers):
- `"openai/gpt-4o"` - OpenAI
- `"anthropic/claude-opus-4-5"` - Anthropic
- `"groq/llama-3.3-70b-versatile"` - Groq
- `"ollama/llama3.2"` - Local Ollama (base_url: http://localhost:11434)
- `"openai/my-model"` + custom base_url - LM Studio, vLLM, any OpenAI-compatible

### 9.2 CrewAI Integration

The CrewAI executor translates NeuralFlow's workflow graph into CrewAI primitives at runtime. No YAML, no `.env` files, no code needed from the user.

```
WorkflowGraph (JSON)
       |
       v
workflow_analyzer.py
  - finds nodes of type "agent"
  - finds designated manager agent (AgentNode with role="manager")
  - finds task assignments (edges from TaskNode to AgentNode)
       |
       v
crewai_executor.py
  - Creates crewai.Agent for each AgentNode
      Agent(
          role=node.role,
          goal=node.goal,
          backstory=node.system_prompt,
          llm=LiteLLM(model=node.model, api_key=...),
          tools=[...converted tools...],
          allow_delegation=node.allow_delegation,
          verbose=node.verbose,
      )
  - Creates crewai.Task for each TaskNode
      Task(
          description=node.task_description,
          expected_output=node.expected_output,
          agent=agent_map[node.assigned_agent_id],
          context=[task_map[dep] for dep in node.dependencies],
      )
  - Creates Crew and kicks off
      Crew(
          agents=agents,
          tasks=tasks,
          process=Process.hierarchical if has_manager else Process.sequential,
          manager_agent=manager_agent,
          verbose=True,
      ).kickoff(inputs=run_input)
```

**Event bridging**: CrewAI's callbacks are wrapped to emit SSE events so the frontend can show real-time progress per node.

### 9.3 LangGraph Integration

LangGraph is used when a workflow contains Router Nodes or explicit state machine patterns (cycles/loops).

```
WorkflowGraph (JSON)
       |
       v
workflow_analyzer.py
  - detects cycles (implies LangGraph)
  - detects RouterNode (conditional edges)
       |
       v
langgraph_executor.py
  - Defines TypedDict state schema from workflow's data schema
  - Adds one StateGraph node per AgentNode/ToolNode
  - Adds conditional edges from RouterNode:
      graph.add_conditional_edges(
          "router_node_id",
          routing_function,  # calls LLM or evaluates expression
          {"branch_a": "node_a", "branch_b": "node_b"},
      )
  - Compiles with SQLite checkpointer for persistence
  - Streams via graph.astream(input, config={"configurable": {"thread_id": run_id}})
```

**Checkpointing**: LangGraph's SQLite checkpointer writes state at every step, enabling NeuralFlow's replay feature without additional implementation work.

### 9.4 MCP Protocol Integration

MCP servers are managed by the Python sidecar's `MCPManager`, which maintains a persistent connection pool. The frontend interacts with MCP entirely through the FastAPI REST API; MCP complexity is hidden from the UI.

```
Frontend: "Connect to this MCP server config"
       |  POST /api/mcp/servers
       v
mcp/manager.py
  - For stdio: spawns subprocess, creates mcp.StdioClient
  - For SSE/HTTP: creates mcp.ClientSession with HTTP transport
  - Calls session.initialize() to handshake
  - Calls session.list_tools() to discover tools
  - Stores tool list in SQLite cache
  - Returns tool list to frontend
       |
       v
Frontend: "Show these tools in the palette"

At execution time:
       |
       v
execution/tool_dispatcher.py
  - Receives tool_call from LLM (tool name + arguments)
  - Looks up which MCP server owns this tool
  - Calls mcp_manager.call_tool(server_id, tool_name, arguments)
       |
       v
mcp/manager.py
  - Calls session.call_tool(name, arguments) on the appropriate client
  - Returns result (text, image, embedded resource)
       |
       v
tool_dispatcher.py
  - Returns result to agent_runner as tool result message
```

**MCP Tool naming**: NeuralFlow normalizes MCP tool names to avoid collisions: `mcp__<server_name>__<tool_name>`. This matches the pattern already established in the existing MCP tooling in this codebase.

---

## 10. What to Build vs What to Integrate

### Build (NeuralFlow-native)

| Component | Reason to Build |
|---|---|
| Visual canvas (React Flow nodes/edges/logic) | Core differentiator; existing tools not reusable |
| Workflow JSON schema and serialization | Must own the data format for portability |
| FastAPI sidecar + REST/SSE API | Glue layer between desktop and Python ecosystem |
| Tauri Rust commands (keychain, sidecar) | Tauri-specific, must write |
| SQLite schema and Alembic migrations | App-specific persistence model |
| SSE event streaming layer | Real-time UI updates, app-specific |
| Cost calculation and dashboard | No existing tool tracks cost with this granularity per node |
| Replay/debug engine | Unique feature, no existing tool has it |
| Code export (CrewAI/LangGraph) | Novel feature: visual-to-code generation |
| Zustand store architecture | Frontend state management, always custom |
| Workflow analyzer (JSON-to-executor) | Bridge between visual schema and Python frameworks |
| Template library | Content, not code |

### Integrate (Do Not Reinvent)

| Library | What it Provides | Integration Depth |
|---|---|---|
| React Flow (xyflow) | Infinite canvas, node/edge engine | Deep: all canvas behavior |
| LiteLLM | Multi-provider LLM routing, cost data | Deep: every LLM call goes through it |
| CrewAI | Multi-agent orchestration logic, role delegation | Medium: wrap in executor, use as-is |
| LangGraph | Stateful graph execution, checkpointing | Medium: wrap in executor, use checkpointer |
| MCP Python SDK | MCP transport, handshake, tool discovery | Deep: all MCP communication |
| shadcn/ui | UI components | Deep: all UI primitives |
| Tailwind CSS | Styling system | Deep: all styles |
| Zustand | State management | Deep: all app state |
| SQLAlchemy + Alembic | ORM + migrations | Deep: all database access |
| FastAPI | HTTP framework, SSE | Deep: entire backend API |
| Pydantic v2 | Request/response validation | Deep: all API schemas |
| Monaco Editor | Code editing (system prompts, custom tools) | Medium: specific editor panels |
| APScheduler | Cron scheduling | Medium: scheduling only |
| ChromaDB / sqlite-vec | Vector storage | Medium: swap-in backends behind an interface |
| PyInstaller / uv | Python binary bundling | Light: build tooling only |

### Key Principle: Thin Integration Layer

The NeuralFlow sidecar should be a **thin adapter** around CrewAI and LangGraph, not a re-implementation of their functionality. When CrewAI adds a new feature (e.g., new memory type), NeuralFlow should expose it with minimal code changes by just surfacing new node configuration options. The `WorkflowAnalyzer` is the critical translation layer.

---

## 11. Open Source Strategy

### License: Apache 2.0

Rationale:
- More permissive than GPL: allows commercial use, private forks, SaaS wrappers
- Less permissive than MIT: requires attribution (patent protection clauses)
- Compatible with all dependencies: React (MIT), LiteLLM (MIT), CrewAI (MIT), LangGraph (MIT), xyflow (MIT/Apache)
- Used by major AI projects: LiteLLM itself is Apache 2.0
- Allows future "Enterprise Edition" with proprietary add-ons (open core model if desired)

### Repository Structure

- Single monorepo on GitHub: `neuralflow-ai/neuralflow`
- GitHub Releases with pre-built installers for all platforms (CI/CD via GitHub Actions)
- `main` branch: stable, always releasable
- `dev` branch: active development
- Semantic versioning: MAJOR.MINOR.PATCH

### Community Strategy

**Phase 1 (Launch, Month 3):**
- README with 60-second demo GIF
- 10 starter templates shipped in the app
- Discord server for community support
- "Good first issue" labels on GitHub from day one
- Product Hunt launch with video demo

**Phase 2 (Growth, Month 6):**
- Contributor guide with local dev setup (single script: `./scripts/setup-dev.sh`)
- Plugin API documentation
- Weekly blog posts (case studies, tutorials)
- Hacker News "Show HN" post when v0.5 ships
- Integration announcements with CrewAI and LangGraph communities

**Phase 3 (Ecosystem, Month 10):**
- Community template gallery (GitHub-hosted JSON files, browseable in-app)
- Plugin registry (PyPI-published node packages)
- "Built with NeuralFlow" showcase page
- Conference talks at AI Engineer World's Fair, LangChain community events

### Telemetry Policy

- Telemetry: OFF by default
- If opted in: anonymous, aggregate-only (run count, node types used, error rates)
- Zero PII: no API keys, no prompts, no outputs, no file paths ever leave the machine
- Telemetry code is open source and auditable
- Powered by: Plausible Analytics (privacy-friendly, self-hostable) or PostHog (self-hosted instance)

### Monetization Path (Optional, Future)

NeuralFlow core stays 100% free and open source. Potential premium additions:
- **NeuralFlow Cloud** (optional SaaS): hosted execution, team sharing, no local Python required - not required to use the desktop app
- **NeuralFlow Pro** (optional desktop add-on): advanced debugging tools, priority support
- **Enterprise License**: audit logging, SSO, managed deployment support

The desktop app itself must always be fully functional without any account or payment.

---

## 12. Non-Functional Requirements

### Performance
- App startup time: < 3 seconds from launch to canvas-ready on SSD
- Sidecar startup: < 5 seconds (PyInstaller binary, no pip install at runtime)
- Canvas: smooth 60fps interaction with up to 200 nodes
- Run log streaming: < 100ms latency from agent event to UI update

### Security
- API keys: stored exclusively in OS keychain (macOS Keychain, Windows Credential Manager, Linux libsecret)
- API keys are never written to SQLite, never logged, never included in crash reports
- Sidecar listens only on `127.0.0.1`, never on `0.0.0.0`
- MCP tool execution: sandboxed subprocess for code execution tools
- File system access: scoped to user-selected directories only

### Privacy
- All data stored locally in `~/.neuralflow/` (configurable)
- No mandatory network calls (works fully offline with Ollama)
- Telemetry opt-in only, documented in UI

### Portability
- Workflow JSON is self-contained: can be run on any NeuralFlow installation
- No proprietary binary formats
- Database migrations: always forward-compatible (Alembic), with export-all-data option

### Accessibility
- Keyboard-first navigation: every action reachable by keyboard
- Screen reader support: ARIA labels on all canvas nodes and interactive elements
- High contrast theme option
- Minimum font size: 13px

---

## Summary: What Makes NeuralFlow Win

1. **No infrastructure tax**: No Docker, no Postgres, no Redis. Double-click and it works.
2. **Visual debugging nobody else has**: Step-by-step replay of any past agent run is a feature no competitor offers.
3. **First-class cost visibility**: Per-node, per-run, per-day cost tracking with budget alerts.
4. **Any model, forever**: LiteLLM integration means every new model provider is supported automatically.
5. **Escape hatch to code**: Export to CrewAI or LangGraph Python means power users are never locked in.
6. **Desktop-native trust**: API keys in OS keychain, data in local SQLite. Enterprises and privacy-conscious users can adopt without IT approval nightmares.
7. **Open source with commercial DNA**: Apache 2.0 encourages adoption; clean architecture enables a paid tier if needed without a painful fork.

---

### Critical Files for Implementation

These are the most architecturally load-bearing files to build first, as all other components depend on them:

- `/apps/desktop/src-tauri/src/main.rs` - Tauri application entry point, sidecar spawn lifecycle, IPC command registration, and all Rust-side system integration (keychain, filesystem, window management)
- `/packages/sidecar/neuralflow/execution/orchestrator.py` - Central dispatcher that receives a run request, invokes the workflow analyzer, selects the correct executor (sequential/CrewAI/LangGraph), manages the SSE event stream, and writes all trace data to SQLite
- `/packages/sidecar/neuralflow/execution/workflow_analyzer.py` - Parses the ReactFlow canvas JSON into an execution plan; this is the translation layer that determines whether a workflow runs as a simple chain, a CrewAI crew, or a LangGraph state machine
- `/apps/desktop/src/canvas/nodes/index.ts` - Node type registry mapping string identifiers to React components; all canvas rendering depends on this file being the single source of truth for what node types exist
- `/apps/desktop/src/stores/workflowStore.ts` - Zustand store that owns the canonical workflow state (nodes, edges, history, dirty flag); the canvas, properties panel, and run system all read/write through this store
