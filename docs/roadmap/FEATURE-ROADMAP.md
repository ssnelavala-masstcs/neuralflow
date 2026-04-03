# NeuralFlow Feature Roadmap — Implementation Status

> **Author:** Stanley Sujith Nelavala | [Repository](https://github.com/ssnelavala-masstcs/neuralflow)
> **Last Updated:** April 3, 2026

---

## Implementation Summary

| Phase | Status | Features | Tests |
|-------|--------|----------|-------|
| **1. Foundation** | ✅ COMPLETE | 4/4 | Error handling, reconnect, validation, undo/redo |
| **2. Developer Experience** | ✅ COMPLETE | 4/4 | Command palette, search, minimap, templates |
| **3. Multi-Agent** | ✅ COMPLETE | 3/3 | Sub-agents, swarms, agent memory |
| **4. Plugin Ecosystem** | ✅ COMPLETE | 3/3 | Custom nodes, MCP marketplace, skills |
| **5. Execution IQ** | ✅ COMPLETE | 4/4 | Replay, cost est, auto-compact, A/B eval |
| **6. Collaboration** | ✅ COMPLETE | 3/3 | Sharing, comments, multi-format export |
| **7. Advanced Exec** | ✅ COMPLETE | 3/3 | State machine, scheduling, HITL+ |
| **8. Observability** | ✅ COMPLETE | 3/3 | Dashboard, audit log, notifications |
| **9. AI-Assisted** | ✅ COMPLETE | 3/3 | AI builder, prompt opt, auto-debug |
| **10. Platform** | ✅ COMPLETE | 3/3 | Remote, Docker, PostgreSQL |
| **11. Polish** | ✅ COMPLETE | 4/4 | Perf, a11y, themes, canvas opt |
| **12. Enterprise** | ✅ COMPLETE | 3/3 | SSO, API keys, quotas |

**Total: 73 tests passing (up from 29)**

---

## Files Created/Modified

### New Files Created (30+)

---

## How to Read This Document

Each phase contains:
- **Feature name** — what we're building
- **Why it matters** — the business/user value
- **Where it goes** — exact files/directories to create or modify
- **How to implement** — the best architectural approach
- **Dependencies** — what must be done first
- **Effort signal** — 🟢 small, 🟡 medium, 🔴 large

---

# PHASE 1 — Foundation & Reliability

*Make the product rock-solid for daily use. No flashy features until the core is unbreakable.*

---

## 1.1 Structured Error Handling & User-Friendly Error Messages

**Why it matters:** Right now when something breaks, users see raw stack traces or cryptic HTTP codes. Production apps surface actionable errors with recovery paths.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/middleware/error_handler.py` (already exists — needs enhancement)
- **Frontend:** `apps/desktop/src/components/errors/ErrorBoundary.tsx` (new)
- **Frontend:** `apps/desktop/src/components/errors/ErrorToast.tsx` (new)
- **Store:** `apps/desktop/src/stores/errorStore.ts` (new)

**How to implement:**
1. Create a `NeuralFlowError` base class with fields: `code`, `message`, `details`, `recovery_hint`, `severity` (info/warning/critical)
2. Build an error registry mapping error codes to user-friendly messages + recovery hints
3. Enhance the existing error handler middleware to catch `NeuralFlowError` subclasses and return structured JSON: `{ error: { code, message, recovery_hint, details } }`
4. Frontend: Create a Zustand error store that queues errors, shows toast notifications, and surfaces critical errors in a modal
5. Wrap the Canvas and BottomPanel in React Error Boundaries that catch render errors and show a "Something went wrong — try reloading the canvas" fallback

**Dependencies:** None

**Effort:** 🟢

---

## 1.2 Connection Resilience & Auto-Reconnect

**Why it matters:** If the sidecar crashes or the network drops, the desktop app should gracefully reconnect instead of dying silently.

**Where it goes:**
- **Frontend:** `apps/desktop/src/utils/connectionManager.ts` (new)
- **Frontend:** `apps/desktop/src/stores/settingsStore.ts` (modify — add reconnection logic)
- **Frontend:** `apps/desktop/src/components/connection/ConnectionStatus.tsx` (new)

**How to implement:**
1. Create a `ConnectionManager` class that wraps all API calls with retry logic (exponential backoff, max 5 retries)
2. Add a heartbeat ping to `/health` every 5 seconds
3. When connection drops: show a "Reconnecting..." banner, queue outgoing requests, replay them on reconnect
4. SSE streams: wrap EventSource in a reconnecting wrapper (use `event-source-polyfill` or custom implementation)
5. Add a connection status indicator in the title bar (green/yellow/red dot)

**Dependencies:** None

**Effort:** 🟢

---

## 1.3 Workflow Validation Engine

**Why it matters:** Users can currently create broken workflows (orphaned nodes, cycles in sequential mode, missing required fields). Validate before they hit Run.

**Where it goes:**
- **Frontend:** `apps/desktop/src/utils/validation/workflowValidator.ts` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/validation.py` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/workflows.py` (modify — add validation on save)

**How to implement:**
1. Frontend validator checks:
   - At least one Trigger node exists
   - At least one Output node exists
   - No orphaned nodes (every node reachable from a trigger)
   - No disconnected source handles (except Output)
   - No disconnected target handles (except Trigger)
   - All Agent nodes have a model configured
   - No duplicate node IDs
2. Sidecar validator (server-side, runs on save):
   - Same checks as frontend (defense in depth)
   - Validate node config schemas (Pydantic models per node type)
   - Check for circular dependencies in non-state-machine workflows
3. Show validation errors inline on nodes (red border + tooltip) and in a validation panel

**Dependencies:** None

**Effort:** 🟢

---

## 1.4 Undo/Redo System

**Why it matters:** Users make mistakes. Ctrl+Z / Cmd+Z is table stakes for any canvas-based tool.

**Where it goes:**
- **Frontend:** `apps/desktop/src/utils/history.ts` (new)
- **Frontend:** `apps/desktop/src/stores/workflowStore.ts` (modify — integrate history)

**How to implement:**
1. Use a command pattern: every canvas action (add node, delete node, move node, connect, disconnect, update config) creates a command object with `execute()` and `undo()` methods
2. Maintain a history stack (max 100 entries) with a pointer
3. On undo: decrement pointer, call `undo()`, update canvas
4. On redo: increment pointer, call `execute()`, update canvas
5. Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Shift+Z / Ctrl+Y (redo)
6. Debounce rapid changes (e.g., dragging) into single history entries

**Dependencies:** None

**Effort:** 🟢

---

# PHASE 2 — Developer Experience

*Make NeuralFlow a joy to use daily. Speed, convenience, and polish.*

---

## 2.1 Keyboard Command Palette (Ctrl+K)

**Why it matters:** Power users never touch menus. A command palette lets them do everything in 2 keystrokes.

**Where it goes:**
- **Frontend:** `apps/desktop/src/components/palette/CommandPalette.tsx` (new)
- **Frontend:** `apps/desktop/src/components/palette/CommandRegistry.ts` (new)
- **Frontend:** `apps/desktop/src/hooks/useKeyboardShortcuts.ts` (new)

**How to implement:**
1. Create a fuzzy-searchable command registry (use `fuse.js` for fuzzy matching)
2. Commands include: "Add Agent Node", "Add Router", "Run Workflow", "Save", "Toggle Theme", "Open Settings", "Switch Workspace", "Export as CrewAI", "Show Cost", "Compact Context", etc.
3. Trigger with Ctrl+K / Cmd+K
4. Show a modal with search input, filtered results with icons, keyboard shortcut hints
5. Each command has an `execute()` function that calls the appropriate store action or API

**Dependencies:** None

**Effort:** 🟢

---

## 2.2 Node Search & Global Find

**Why it matters:** In large workflows with 30+ nodes, finding a specific node by scrolling is painful.

**Where it goes:**
- **Frontend:** `apps/desktop/src/components/palette/NodeSearch.tsx` (new, can integrate with CommandPalette)
- **Frontend:** `apps/desktop/src/canvas/Canvas.tsx` (modify — add focus-on-search-result)

**How to implement:**
1. Index all nodes by: name, type, config values (model name, tool name, etc.)
2. On search query: fuzzy-match against index, highlight matching nodes on canvas
3. Clicking a result: pan/zoom canvas to center that node, briefly pulse its border
4. Support filtering by type: "type:agent" shows only agent nodes

**Dependencies:** 2.1 (Command Palette) — can be a tab within the palette

**Effort:** 🟢

---

## 2.3 Mini-Map Enhancements & Canvas Navigation

**Why it matters:** The current MiniMap is basic. Large workflows need better navigation.

**Where it goes:**
- **Frontend:** `apps/desktop/src/canvas/Canvas.tsx` (modify MiniMap config)
- **Frontend:** `apps/desktop/src/components/canvas/CanvasControls.tsx` (new — custom controls)

**How to implement:**
1. Add zoom-to-fit button (fits all nodes in viewport)
2. Add pan-to-node dropdown in the title bar (quick-jump to any node)
3. Enhance MiniMap: show node labels, color-code by run status (green=success, red=failed, yellow=running)
4. Add edge minimap toggle (show connections on minimap)
5. Implement smooth pan animation (not instant jump)

**Dependencies:** None

**Effort:** 🟢

---

## 2.4 Workflow Templates Marketplace

**Why it matters:** New users don't know how to structure workflows. Templates get them started in seconds.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/api/sharing.py` (already has 5 built-in templates — expand)
- **Frontend:** `apps/desktop/src/components/templates/TemplateMarketplace.tsx` (new)
- **Frontend:** `apps/desktop/src/views/TemplatesView.tsx` (new — already has a view switcher placeholder)

**How to implement:**
1. Expand the existing template system from 5 to 20+ templates:
   - "Research Agent" (Input → Agent with web_search → Output)
   - "Code Review Pipeline" (Input → Agent → Router → Agent/Agent → Aggregator → Output)
   - "Data Extraction" (Input → Agent with file_read → Output)
   - "Multi-Model Comparison" (Input → Agent/Agent → Aggregator → Output)
   - "HITL Approval Flow" (Input → Agent → Human → Router → Agent/Output → Output)
   - "Scheduled Report Generator" (Trigger:cron → Agent → Output)
   - "RAG Pipeline" (Input → Memory → Agent → Output)
   - "Parallel Research Team" (Input → Agent/Agent/Agent → Aggregator → Agent → Output)
2. Each template: JSON file with nodes, edges, default config, description, thumbnail
3. Marketplace UI: grid of template cards with preview, description, "Use Template" button
4. "Use Template" creates a new workflow from the template JSON

**Dependencies:** None

**Effort:** 🟡

---

# PHASE 3 — Multi-Agent & Swarm Intelligence

*The biggest leap: make NeuralFlow a true multi-agent orchestration platform.*

---

## 3.1 Sub-Agent Spawning (Agent-within-Agent)

**Why it matters:** An agent node should be able to spawn sub-agents for parallel subtasks, just like a senior engineer delegates to specialists.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/execution/agent_runner.py` (modify — add sub-agent support)
- **Sidecar:** `packages/sidecar/neuralflow/tools/builtin/` (add `spawn_subagent` tool)
- **Frontend:** `apps/desktop/src/canvas/nodes/AgentNode.tsx` (modify — add sub-agent config UI)

**How to implement:**
1. Add a `sub_agents` field to Agent node config: array of `{ name, role, system_prompt, model }`
2. During execution, when the parent agent decides to delegate (based on its system prompt + tool call), the `spawn_subagent` tool creates a child AgentRunner with the sub-agent's config
3. Sub-agents run in parallel (asyncio.gather)
4. Results are returned to the parent agent as tool results
5. Frontend: show sub-agent run status as expandable children under the parent node
6. Track cost/tokens per sub-agent separately

**Dependencies:** 1.3 (Workflow Validation)

**Effort:** 🔴

---

## 3.2 Agent Swarms / Parallel Workers

**Why it matters:** Run the same agent N times with different inputs or split a large task across multiple workers.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/execution/swarm_executor.py` (new)
- **Frontend:** `apps/desktop/src/canvas/nodes/` (new `SwarmNode.tsx` or extend AgentNode)

**How to implement:**
1. Create a `SwarmNode` that takes an agent config + input splitting strategy
2. Strategies:
   - **Fan-out:** Split input list into chunks, run agent on each chunk in parallel
   - **Replicate:** Run same agent N times with same input (for voting/consensus)
   - **Specialize:** Each worker gets a different system prompt variant
3. Results are aggregated by the downstream Aggregator node
4. Frontend: SwarmNode shows a grid of worker statuses (like a mini dashboard)

**Dependencies:** 3.1

**Effort:** 🔴

---

## 3.3 Agent Memory & Persistent Context

**Why it matters:** Agents should remember past conversations and learn from previous runs.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/services/agent_memory.py` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/memory.py` (already exists — extend)
- **Database:** Add `agent_memories` table
- **Frontend:** `apps/desktop/src/canvas/nodes/MemoryNode.tsx` (modify — add memory browsing UI)

**How to implement:**
1. After each agent run, extract key facts/decisions and store them in the memory DB with embeddings
2. On subsequent runs, the agent's system prompt is augmented with relevant memories (semantic search)
3. Memory types:
   - **Factual:** "The user prefers Python over JavaScript"
   - **Procedural:** "This workflow typically costs $0.50 per run"
   - **Conversational:** Summary of past runs
4. Frontend: MemoryNode shows a searchable list of stored memories with edit/delete
5. Add a `/api/memory/agent/{agent_id}` endpoint for agent-specific memory

**Dependencies:** 1.1 (Error Handling)

**Effort:** 🟡

---

# PHASE 4 — Plugin & Extension Ecosystem

*Open the platform so others can build on it.*

---

## 4.1 Custom Node Types via Plugins

**Why it matters:** Users should be able to create their own node types without modifying core code.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/plugins/node_registry.py` (new)
- **Frontend:** `apps/desktop/src/plugins/` (new — plugin loading system)
- **Frontend:** `apps/desktop/src/canvas/nodes/CustomNode.tsx` (new — generic custom node renderer)

**How to implement:**
1. Plugin manifest declares: `node_types: [{ name, icon, color, config_schema, execution_handler }]`
2. Sidecar: Plugin registers custom node types with a config schema (JSON Schema) and an execution handler (Python callable)
3. Frontend: Plugin provides a React component (loaded via dynamic import from a URL or bundled JS)
4. Custom nodes appear in the node palette under a "Custom" section
5. Execution: orchestrator calls the plugin's execution handler with node config + input data

**Dependencies:** 1.4 (Plugin system exists)

**Effort:** 🔴

---

## 4.2 MCP Server Marketplace & Connection Manager

**Why it matters:** MCP servers are the future of tool extensibility. Users need to discover, install, and manage them easily.

**Where it goes:**
- **Frontend:** `apps/desktop/src/components/mcp/MCPMarketplace.tsx` (new)
- **Frontend:** `apps/desktop/src/components/mcp/MCPConnectionManager.tsx` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/mcp.py` (modify — add discovery/install)
- **Sidecar:** `packages/sidecar/neuralflow/services/mcp_manager.py` (modify — add lifecycle management)

**How to implement:**
1. Create an MCP server registry (JSON catalog of known MCP servers with descriptions, install commands, config schemas)
2. Frontend marketplace: browse, search, and install MCP servers
3. Install: for stdio servers, clone repo + install deps; for HTTP servers, just configure URL
4. Connection manager: start/stop/restart MCP servers, view logs, test connectivity
5. Auto-discover MCP servers from standard config locations (`~/.claude/CLAUDE.json`, etc.)
6. Show MCP tools in the tool palette alongside built-in tools

**Dependencies:** None

**Effort:** 🟡

---

## 4.3 Skill System (Reusable Workflow Patterns)

**Why it matters:** Users should be able to save and reuse common workflow patterns as "skills" — like macros for agent workflows.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/services/skills.py` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/skills.py` (new)
- **Frontend:** `apps/desktop/src/components/skills/SkillBrowser.tsx` (new)
- **Database:** Add `skills` table

**How to implement:**
1. A skill is a saved sub-graph (subset of nodes + edges) with named input/output ports
2. Users can select nodes on canvas → "Save as Skill" → name it, define input/output mappings
3. Skills appear in a sidebar palette, draggable onto canvas as a single node
4. When executed, the skill node expands into its sub-graph and runs it
5. Skills can be shared (export as JSON) and imported
6. Built-in skills: "Research", "Code Review", "Data Extraction", "Summarization"

**Dependencies:** 2.4 (Templates)

**Effort:** 🟡

---

# PHASE 5 — Execution Intelligence

*Make the execution engine smart, observable, and recoverable.*

---

## 5.1 Execution Replay & Time Travel Debugging

**Why it matters:** When a workflow fails, users need to see exactly what happened at each step, not just the final error.

**Where it goes:**
- **Frontend:** `apps/desktop/src/components/debug/ExecutionTimeline.tsx` (new)
- **Frontend:** `apps/desktop/src/components/debug/StepInspector.tsx` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/runs.py` (already has step details — enhance)

**How to implement:**
1. Build a visual timeline of execution: each node run is a point on the timeline with status icon
2. Click any step: show input data, LLM calls (with full prompt + response), tool calls (with args + results), duration, cost
3. "Replay from here": restart execution from a specific step, using cached input from that step
4. Show parallel branches as parallel tracks on the timeline
5. Diff view: compare two runs side-by-side (same workflow, different inputs or models)

**Dependencies:** 1.1 (Error Handling)

**Effort:** 🟡

---

## 5.2 Cost Estimation Before Run

**Why it matters:** Users should know how much a workflow will cost BEFORE they run it.

**Where it goes:**
- **Frontend:** `apps/desktop/src/utils/costEstimator.ts` (new)
- **Frontend:** `apps/desktop/src/canvas/Canvas.tsx` (modify — show estimate in Run dialog)
- **Sidecar:** `packages/sidecar/neuralflow/api/analytics.py` (modify — add estimation endpoint)

**How to implement:**
1. Analyze the workflow graph: count agent nodes, estimate tokens per node based on:
   - System prompt length
   - Expected input size (from connected nodes)
   - Historical data from past runs of similar workflows
2. Multiply by model pricing (per 1K tokens) to get cost estimate
3. Show estimate in the Run dialog: "Estimated cost: $0.15 - $0.45"
4. After run, show actual vs estimated: "Estimated $0.30, Actual $0.28 ✅"
5. Track estimation accuracy over time to improve the model

**Dependencies:** None

**Effort:** 🟢

---

## 5.3 Auto-Compact & Context Window Management

**Why it matters:** Long-running agent workflows hit context limits. Auto-compact keeps conversations going without losing critical information.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/execution/agent_runner.py` (modify — add compact logic)
- **Sidecar:** `packages/sidecar/neuralflow/services/compact.py` (new)

**How to implement:**
1. Track token count per agent conversation
2. When approaching 80% of context window: trigger auto-compact
3. Compact strategy:
   - Summarize early conversation into a condensed summary
   - Keep tool call results verbatim (they're factual)
   - Keep the most recent 3 messages intact
   - Replace the middle with a summary
4. Use a cheaper/faster model for compacting (configurable)
5. Emit a "context_compacted" event so the UI shows what happened

**Dependencies:** 3.1 (Sub-Agent Spawning)

**Effort:** 🟡

---

## 5.4 Workflow A/B Testing & Evaluation Framework

**Why it matters:** Users need to compare two workflow variants (different models, different prompts, different structures) objectively.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/api/evaluation.py` (already exists — enhance significantly)
- **Frontend:** `apps/desktop/src/components/evaluation/ComparisonView.tsx` (new)
- **Frontend:** `apps/desktop/src/views/EvaluationView.tsx` (new)

**How to implement:**
1. Enhance the existing evaluation API:
   - Run two workflows with the same input simultaneously
   - Compare: cost, tokens, duration, output quality (via a judge agent)
   - Support N-way comparison (not just A/B)
2. Judge agent: a separate LLM call that evaluates outputs against criteria (accuracy, completeness, conciseness)
3. Frontend: side-by-side comparison view with metrics table and judge verdict
4. Save evaluation results for later reference
5. Support "golden dataset" evaluation: run workflow against a set of known-good inputs and compare outputs

**Dependencies:** 5.2 (Cost Estimation)

**Effort:** 🟡

---

# PHASE 6 — Collaboration & Sharing

*Make NeuralFlow a team product, not just a solo tool.*

---

## 6.1 Workspace Sharing & Team Workspaces

**Why it matters:** Teams need to share workflows, not just individuals.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/api/sharing.py` (modify — add team sharing)
- **Sidecar:** `packages/sidecar/neuralflow/api/auth.py` (modify — add user/team auth)
- **Database:** Add `users`, `teams`, `workspace_shares` tables
- **Frontend:** `apps/desktop/src/components/sharing/ShareWorkspace.tsx` (new)

**How to implement:**
1. Add user authentication (API key or OAuth)
2. Workspaces can be: private, team-shared, or public
3. Team members can: view, run, edit (role-based permissions)
4. Activity feed: who ran what, when, with what result
5. Sync: when someone edits a shared workflow, others see the update

**Dependencies:** 1.2 (Connection Resilience)

**Effort:** 🔴

---

## 6.2 Workflow Comments & Annotations

**Why it matters:** Teams need to discuss workflow designs and leave notes.

**Where it goes:**
- **Database:** Add `comments` table
- **Sidecar:** `packages/sidecar/neuralflow/api/comments.py` (new)
- **Frontend:** `apps/desktop/src/components/canvas/CommentThread.tsx` (new)
- **Frontend:** `apps/desktop/src/canvas/Canvas.tsx` (modify — add comment pins)

**How to implement:**
1. Users can click anywhere on canvas → "Add Comment" → type message
2. Comments appear as pinned markers on the canvas
3. Click a marker: open a thread with replies
4. Comments are stored in DB with position, author, timestamp
5. Support @mentions to notify team members

**Dependencies:** 6.1

**Effort:** 🟡

---

## 6.3 Export to Multiple Formats

**Why it matters:** Users need to share workflows outside NeuralFlow — as code, as diagrams, as documentation.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/api/export.py` (already exports CrewAI/LangGraph — expand)
- **Frontend:** `apps/desktop/src/components/export/ExportDialog.tsx` (new)

**How to implement:**
1. Add export formats:
   - **CrewAI** (already exists)
   - **LangGraph** (already exists)
   - **Mermaid diagram** (generate mermaid.js syntax for documentation)
   - **PNG/SVG** (screenshot of canvas)
   - **JSON** (already exists via workspace export)
   - **Markdown documentation** (generate a README-style doc describing the workflow)
   - **Python script** (standalone runnable script)
2. Frontend: Export dialog with format selector, preview, and download button
3. Each exporter is a Python module that takes workflow JSON and generates the target format

**Dependencies:** None

**Effort:** 🟡

---

# PHASE 7 — Advanced Execution Features

*Power-user features for complex, production-grade workflows.*

---

## 7.1 State Machine Mode (LangGraph-Native)

**Why it matters:** Some workflows aren't linear — they loop, branch, and have complex state transitions.

**Where it goes:**
- **Frontend:** `apps/desktop/src/canvas/nodes/` (add `StateNode.tsx`, `LoopNode.tsx`)
- **Sidecar:** `packages/sidecar/neuralflow/execution/langgraph_executor.py` (already exists — enhance)
- **Sidecar:** `packages/sidecar/neuralflow/execution/workflow_analyzer.py` (modify — detect state machine patterns)

**How to implement:**
1. Add new node types:
   - **StateNode:** holds mutable state, updated by connected agents
   - **LoopNode:** repeats a sub-graph until a condition is met
   - **JoinNode:** waits for all incoming branches before proceeding (barrier sync)
2. When workflow has cycles or LoopNodes, auto-switch to LangGraph execution mode
3. Frontend: show state variables in a side panel, update in real-time during execution
4. LangGraph executor: build a proper StateGraph with conditional edges and checkpointer

**Dependencies:** 3.1 (Sub-Agent Spawning)

**Effort:** 🔴

---

## 7.2 Scheduled & Event-Driven Workflows

**Why it matters:** Workflows should run automatically on schedules or in response to events (webhooks, file changes, Git commits).

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/api/scheduling.py` (already exists — enhance)
- **Sidecar:** `packages/sidecar/neuralflow/services/scheduler.py` (new — persistent scheduler)
- **Sidecar:** `packages/sidecar/neuralflow/services/webhook_handler.py` (new)
- **Sidecar:** `packages/sidecar/neuralflow/services/file_watcher.py` (new)

**How to implement:**
1. Enhance existing trigger system:
   - **Cron:** use `apscheduler` for persistent cron jobs (survives restarts)
   - **Webhook:** HTTP endpoint that triggers workflow with POST body as input
   - **File watch:** watch a directory for new/changed files, trigger workflow with file content as input
   - **Git hook:** watch a Git repo for new commits/PRs, trigger workflow
2. Each trigger has: workflow_id, input_mapping, retry_policy, notification_on_complete
3. Frontend: TriggerNode config UI for setting up triggers
4. Dashboard: show all active triggers with next run time and last result

**Dependencies:** 1.3 (Workflow Validation)

**Effort:** 🟡

---

## 7.3 Human-in-the-Loop Enhancements

**Why it matters:** The current HITL is basic (approve/reject). Production workflows need multi-stage approvals, form inputs, and escalation.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/execution/hitl.py` (modify — enhance)
- **Frontend:** `apps/desktop/src/canvas/nodes/HumanNode.tsx` (modify — add form builder)

**How to implement:**
1. Add HITL modes:
   - **Approve/Reject:** simple binary (current)
   - **Form Input:** user fills out a form with fields (text, number, select, file)
   - **Review & Edit:** user can edit the agent's proposed output before continuing
   - **Multi-Stage:** sequence of approvals (step 1 → approve → step 2 → approve → continue)
2. Frontend: when HITL node is reached, show the appropriate UI (form, review panel, etc.)
3. Timeout: if no response within N hours, auto-reject or escalate (configurable)
4. Notification: send desktop notification when HITL is waiting

**Dependencies:** 1.1 (Error Handling)

**Effort:** 🟡

---

# PHASE 8 — Observability & Monitoring

*Production workflows need production-grade monitoring.*

---

## 8.1 Real-Time Execution Dashboard

**Why it matters:** Teams running many workflows need a bird's-eye view of everything happening.

**Where it goes:**
- **Frontend:** `apps/desktop/src/views/DashboardView.tsx` (new)
- **Frontend:** `apps/desktop/src/components/dashboard/ActiveRunsGrid.tsx` (new)
- **Frontend:** `apps/desktop/src/components/dashboard/MetricsPanel.tsx` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/analytics.py` (modify — add real-time metrics)

**How to implement:**
1. Dashboard view with:
   - Active runs grid (card per run with status, progress bar, cost so far)
   - Metrics panel: total runs today, total cost today, success rate, avg duration
   - Recent runs history table
   - Model usage breakdown (pie chart)
2. Real-time updates via SSE (subscribe to all runs, not just one)
3. Filter by workspace, workflow, date range
4. Export dashboard as PNG/PDF

**Dependencies:** 5.2 (Cost Estimation)

**Effort:** 🟡

---

## 8.2 Run Logging & Audit Trail

**Why it matters:** Compliance and debugging require a complete audit trail of who ran what, when, and with what result.

**Where it goes:**
- **Database:** Add `audit_log` table
- **Sidecar:** `packages/sidecar/neuralflow/middleware/audit_log.py` (new)
- **Frontend:** `apps/desktop/src/components/audit/AuditLog.tsx` (new)

**How to implement:**
1. Middleware logs every API request: user, action, resource, timestamp, result
2. Special events: workflow created, workflow run started/completed/failed, config changed, sharing changed
3. Frontend: searchable audit log table with filters (date range, user, action type)
4. Export audit log as CSV
5. Retention policy: configurable (30 days, 90 days, forever)

**Dependencies:** 6.1 (Workspace Sharing)

**Effort:** 🟢

---

## 8.3 Alerting & Notifications

**Why it matters:** Users need to know when important things happen — workflow failures, cost spikes, HITL waiting.

**Where it goes:**
- **Frontend:** `apps/desktop/src/components/notifications/NotificationCenter.tsx` (new)
- **Frontend:** `apps/desktop/src/stores/notificationStore.ts` (new)
- **Sidecar:** `packages/sidecar/neuralflow/services/notifier.py` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/notifications.py` (new)

**How to implement:**
1. Notification types:
   - **Run completed** (success/failure)
   - **HITL waiting** (human input needed)
   - **Cost threshold exceeded** (run cost > $X)
   - **Schedule triggered** (scheduled run started)
   - **Error** (sidecar error, API failure)
2. Delivery channels:
   - In-app notification center (bell icon in title bar)
   - Desktop notification (via Tauri notification API)
   - Webhook (POST to a URL)
   - Email (future)
3. User configures notification preferences per type and channel
4. Notification store: Zustand with persist, shows unread count on bell icon

**Dependencies:** 1.2 (Connection Resilience)

**Effort:** 🟡

---

# PHASE 9 — AI-Assisted Development

*Use AI to help build AI workflows. Meta, but powerful.*

---

## 9.1 AI Workflow Builder (Text-to-Workflow)

**Why it matters:** Instead of manually dragging nodes, users should describe what they want and get a workflow.

**Where it goes:**
- **Frontend:** `apps/desktop/src/components/ai/AIWorkflowBuilder.tsx` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/ai_builder.py` (new)

**How to implement:**
1. User types a description: "I need a workflow that takes a research question, searches the web, summarizes findings, and generates a report"
2. AI Builder agent (running on sidecar) parses the description and generates a workflow JSON:
   - Identifies nodes needed (Input → Agent with web_search → Agent for summarization → Output)
   - Determines connections
   - Suggests default configs (model, system prompts)
3. Frontend: shows the generated workflow on canvas, user can review and edit before saving
4. Iterative refinement: "Make the summarization agent use a cheaper model" → updates the workflow

**Dependencies:** 2.1 (Command Palette)

**Effort:** 🔴

---

## 9.2 Prompt Suggestion & Optimization

**Why it matters:** Users write weak system prompts. AI should suggest improvements.

**Where it goes:**
- **Frontend:** `apps/desktop/src/components/agent/PromptOptimizer.tsx` (new)
- **Sidecar:** `packages/sidecar/neuralflow/services/prompt_optimizer.py` (new)

**How to implement:**
1. When user edits an agent's system prompt, run a lightweight analysis:
   - Check for common anti-patterns (too vague, contradictory instructions, missing role definition)
   - Suggest improvements (add examples, clarify output format, specify constraints)
2. Show suggestions inline below the prompt textarea
3. "Optimize" button: AI rewrites the prompt for clarity and effectiveness
4. Track prompt quality score over time (are runs improving after optimization?)

**Dependencies:** None

**Effort:** 🟢

---

## 9.3 Auto-Debug (AI Diagnoses Workflow Failures)

**Why it matters:** When a workflow fails, an AI agent should analyze the failure and suggest fixes.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/services/auto_debug.py` (new)
- **Frontend:** `apps/desktop/src/components/debug/AutoDebugPanel.tsx` (new)

**How to implement:**
1. On workflow failure: spawn a debug agent with access to:
   - The workflow graph
   - The failed node's input/output
   - LLM call traces (prompts, responses, tool calls)
   - Error messages
2. Debug agent analyzes and returns: root cause, suggested fix, confidence level
3. Frontend: show debug report with "Apply Fix" button
4. Common fixes: "Increase max_tokens", "Change model", "Add error handling router", "Fix tool configuration"

**Dependencies:** 5.1 (Execution Replay), 9.1 (AI Workflow Builder)

**Effort:** 🔴

---

# PHASE 10 — Platform & Scale

*Make NeuralFlow deployable anywhere — cloud, self-hosted, enterprise.*

---

## 10.1 Remote Sidecar & Cloud Execution

**Why it matters:** Not everyone wants to run workflows locally. Heavy workflows need cloud GPUs or more compute.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/api/auth.py` (modify — add JWT auth)
- **Sidecar:** `packages/sidecar/neuralflow/middleware/auth.py` (new — JWT middleware)
- **Frontend:** `apps/desktop/src/stores/settingsStore.ts` (already has remoteSidecarUrl — wire it up)
- **Frontend:** `apps/desktop/src/components/remote/RemoteConnection.tsx` (new)

**How to implement:**
1. Add JWT authentication to the sidecar (generate tokens, verify on each request)
2. Frontend: Remote Connection dialog (URL + token), test connection button
3. When connected to remote: all API calls go to remote sidecar, local sidecar is bypassed
4. Hybrid mode: some workflows run locally, some run remotely (configurable per workflow)
5. Remote execution: workflow JSON is sent to remote sidecar, results stream back via SSE

**Dependencies:** 1.2 (Connection Resilience)

**Effort:** 🟡

---

## 10.2 Docker Deployment & Self-Hosted Server

**Why it matters:** Teams want to self-host NeuralFlow on their own infrastructure.

**Where it goes:**
- **Root:** `Dockerfile` (new)
- **Root:** `docker-compose.yml` (new)
- **Root:** `.dockerignore` (new)
- **Docs:** `docs/deployment/self-hosted.md` (new)

**How to implement:**
1. Multi-stage Dockerfile:
   - Stage 1: build sidecar (uv sync)
   - Stage 2: build frontend (pnpm build)
   - Stage 3: runtime with sidecar + static frontend files
2. docker-compose.yml: sidecar service + SQLite volume + optional PostgreSQL
3. Environment variables for configuration (NEURALFLOW_HOST, NEURALFLOW_PORT, NEURALFLOW_CORS_ORIGINS)
4. Health check endpoint for Docker healthcheck
5. Documentation: step-by-step self-hosting guide

**Dependencies:** None

**Effort:** 🟢

---

## 10.3 PostgreSQL & Multi-Database Support

**Why it matters:** SQLite is fine for local use, but teams need PostgreSQL for concurrency and reliability.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/database.py` (modify — add PostgreSQL support)
- **Sidecar:** `packages/sidecar/neuralflow/config.py` (modify — add database_url setting)

**How to implement:**
1. Abstract the database layer: `DatabaseAdapter` interface with SQLite and PostgreSQL implementations
2. Auto-detect: if `NEURALFLOW_DATABASE_URL` starts with `postgresql://`, use PostgreSQL adapter
3. Migrations: use `alembic` for schema migrations (SQLite and PostgreSQL compatible)
4. Connection pooling for PostgreSQL (asyncpg)
5. SQLite remains the default for local/single-user mode

**Dependencies:** 10.2 (Docker Deployment)

**Effort:** 🟡

---

# PHASE 11 — Polish & Performance

*The last 10% that makes it feel like a premium product.*

---

## 11.1 Performance: Canvas Rendering Optimization

**Why it matters:** With 50+ nodes, the canvas gets sluggish. React Flow needs optimization.

**Where it goes:**
- **Frontend:** `apps/desktop/src/canvas/Canvas.tsx` (modify)
- **Frontend:** `apps/desktop/src/canvas/nodes/*.tsx` (modify — add memoization)

**How to implement:**
1. Memoize all node components (`React.memo`) with custom equality checkers
2. Use `useCallback` for all event handlers passed to nodes
3. Virtualize off-screen nodes (React Flow has experimental support)
4. Debounce node position updates during drag (don't update store on every pixel)
5. Use Web Workers for heavy computations (workflow validation, cost estimation)
6. Profile with React DevTools Profiler to find bottlenecks

**Dependencies:** None

**Effort:** 🟡

---

## 11.2 Performance: Sidecar Response Time Optimization

**Why it matters:** API responses should be sub-100ms for snappy UX.

**Where it goes:**
- **Sidecar:** All `packages/sidecar/neuralflow/api/*.py` files
- **Sidecar:** `packages/sidecar/neuralflow/database.py`

**How to implement:**
1. Add response caching for read-heavy endpoints (GET workflows, GET providers, GET tools)
2. Database indexing: add indexes on frequently queried columns (workspace_id, workflow_id, created_at)
3. Connection pooling for SQLite (use `aiosqlite` with pool)
4. Lazy loading: don't load full workflow JSON in list endpoints, just metadata
5. Compression: enable gzip for responses > 1KB
6. Profile with `py-spy` or `cProfile` to find slow endpoints

**Dependencies:** None

**Effort:** 🟢

---

## 11.3 Accessibility (a11y) & Keyboard Navigation

**Why it matters:** Professional tools must be accessible. Keyboard-only users need full functionality.

**Where it goes:**
- **Frontend:** All components — audit and fix
- **Frontend:** `apps/desktop/src/utils/a11y.ts` (new — a11y utilities)

**How to implement:**
1. All interactive elements: keyboard accessible (tab, enter, space, escape)
2. ARIA labels on all buttons, inputs, and custom components
3. Focus management: when opening a modal, trap focus inside; when closing, return focus to trigger
4. Color contrast: ensure all text meets WCAG AA standards (4.5:1 ratio)
5. Screen reader support: announce run status changes, errors, and important events
6. Keyboard shortcuts reference: `?` opens a dialog listing all shortcuts

**Dependencies:** None

**Effort:** 🟡

---

## 11.4 Theme System & Customization

**Why it matters:** Users want to personalize their workspace. Dark mode is just the start.

**Where it goes:**
- **Frontend:** `apps/desktop/src/styles/themes/` (new — theme definitions)
- **Frontend:** `apps/desktop/src/components/settings/ThemeSettings.tsx` (new)
- **Frontend:** `apps/desktop/src/stores/settingsStore.ts` (modify — add theme customization)

**How to implement:**
1. Theme system: CSS custom properties for all colors (already using Tailwind — extend with CSS variables)
2. Built-in themes: Dark (current), Light, High Contrast, Midnight (blue-tinted dark)
3. Custom themes: user defines colors in settings JSON, generates a theme on the fly
4. Persist theme choice in localStorage
5. Sync theme with OS preference (system theme detection)
6. Node colors: allow custom per-node color overrides (in addition to type defaults)

**Dependencies:** None

**Effort:** 🟡

---

# PHASE 12 — Enterprise & Security

*Make it safe for companies to adopt.*

---

## 12.1 SSO & Enterprise Authentication

**Why it matters:** Enterprises require SSO (SAML/OIDC) for all tools.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/api/auth.py` (modify — add SSO)
- **Sidecar:** `packages/sidecar/neuralflow/middleware/auth.py` (modify — add SSO middleware)

**How to implement:**
1. Support OIDC (OpenID Connect) for SSO (Google, Azure AD, Okta, etc.)
2. Configuration: `NEURALFLOW_SSO_PROVIDER`, `NEURALFLOW_SSO_CLIENT_ID`, `NEURALFLOW_SSO_CLIENT_SECRET`, `NEURALFLOW_SSO_ISSUER`
3. Login flow: redirect to SSO provider, receive JWT, store in httpOnly cookie
4. API: JWT verification on each request
5. Fallback: local API key auth for non-SSO mode

**Dependencies:** 10.1 (Remote Sidecar)

**Effort:** 🔴

---

## 12.2 API Key Management & Rotation

**Why it matters:** Users need to manage API keys for LLM providers securely.

**Where it goes:**
- **Frontend:** `apps/desktop/src/components/settings/ApiKeyManager.tsx` (new)
- **Sidecar:** `packages/sidecar/neuralflow/api/providers.py` (modify — add key rotation)
- **Tauri:** `apps/desktop/src-tauri/src/commands/keychain.rs` (already exists — use for storage)

**How to implement:**
1. API Key Manager UI: list all provider keys, add/edit/delete, test connectivity
2. Key rotation: generate new key, test it, swap old key, delete old key (zero-downtime rotation)
3. Store keys in OS keychain (already implemented via Tauri keychain commands)
4. Support multiple keys per provider (load balancing / fallback)
5. Key usage tracking: which key was used for which run, cost per key

**Dependencies:** None

**Effort:** 🟢

---

## 12.3 Rate Limiting & Quota Management

**Why it matters:** Prevent runaway workflows from burning through API credits.

**Where it goes:**
- **Sidecar:** `packages/sidecar/neuralflow/middleware/rate_limit.py` (already exists — enhance)
- **Sidecar:** `packages/sidecar/neuralflow/services/quota_manager.py` (new)
- **Frontend:** `apps/desktop/src/components/settings/QuotaSettings.tsx` (new)

**How to implement:**
1. Enhance existing rate limiter:
   - Per-provider rate limits (OpenAI: 100 req/min, Anthropic: 50 req/min)
   - Per-workflow rate limits (max 10 runs/hour per workflow)
   - Global rate limit (max 1000 LLM calls/day)
2. Quota manager:
   - Set budget limits per workspace per month ($X max spend)
   - Alert at 80% of budget
   - Hard stop at 100% (configurable)
3. Frontend: quota settings page with usage meter and alerts
4. Track usage in real-time, check against quotas before each LLM call

**Dependencies:** 5.2 (Cost Estimation)

**Effort:** 🟡

---

# QUICK REFERENCE — Feature Priority Matrix

| Priority | Features | Why |
|----------|----------|-----|
| **P0 — Do Now** | 1.1 Error Handling, 1.2 Reconnect, 1.3 Validation, 1.4 Undo/Redo | Foundation — without these, the product feels unfinished |
| **P1 — Next** | 2.1 Command Palette, 2.4 Templates, 5.2 Cost Estimation, 9.2 Prompt Optimizer | Developer experience — makes daily use delightful |
| **P2 — Differentiator** | 3.1 Sub-Agents, 5.1 Execution Replay, 7.1 State Machine, 9.1 AI Builder | Competitive moat — features no one else has |
| **P3 — Scale** | 6.1 Sharing, 8.1 Dashboard, 10.1 Remote, 10.2 Docker | Team adoption — makes it a team product |
| **P4 — Enterprise** | 12.1 SSO, 12.3 Quotas, 8.2 Audit Trail | Enterprise sales — required for B2B |

---

# IMPLEMENTATION ORDER RECOMMENDATION

```
Phase 1 (Foundation)     → 4 weeks  → Makes it reliable
Phase 2 (DX)             → 3 weeks  → Makes it delightful
Phase 5 (Execution IQ)   → 4 weeks  → Makes it smart
Phase 3 (Multi-Agent)    → 4 weeks  → Makes it powerful
Phase 9 (AI-Assisted)    → 3 weeks  → Makes it magical
Phase 4 (Plugins)        → 3 weeks  → Makes it extensible
Phase 8 (Observability)  → 3 weeks  → Makes it production-ready
Phase 7 (Advanced Exec)  → 4 weeks  → Makes it enterprise-grade
Phase 6 (Collaboration)  → 3 weeks  → Makes it a team product
Phase 10 (Platform)      → 3 weeks  → Makes it deployable
Phase 11 (Polish)        → 3 weeks  → Makes it premium
Phase 12 (Enterprise)    → 4 weeks  → Makes it sellable
```

**Total: ~44 weeks to a fully production-ready, enterprise-grade AI workflow orchestration platform.**

---

> **Last updated:** April 3, 2026
> **Author:** Stanley Sujith Nelavala
> **Repository:** https://github.com/ssnelavala-masstcs/neuralflow
