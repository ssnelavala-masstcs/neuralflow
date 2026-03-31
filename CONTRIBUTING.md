# Contributing to NeuralFlow

Thank you for your interest in contributing. This guide covers how to get set up locally and how to submit good PRs.

## Dev Setup

**Prerequisites**
- [Rust](https://rustup.rs/) (stable toolchain)
- [Node.js 20+](https://nodejs.org) + [pnpm](https://pnpm.io)
- [Python 3.11+](https://python.org) + [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/ssnelavala-masstcs/neuralflow
cd neuralflow
./scripts/setup-dev.sh   # installs all deps
./scripts/dev.sh         # starts Tauri dev + Python sidecar
```

## Project Layout

```
apps/desktop/src-tauri/   Rust: keychain, sidecar, IPC commands
apps/desktop/src/         React frontend
packages/sidecar/         Python FastAPI backend
templates/                Starter workflow JSON files
docs/                     Documentation
```

## Where to Contribute

| Area | Path | Difficulty |
|------|------|-----------|
| New built-in tool | `packages/sidecar/neuralflow/tools/` | Easy |
| Starter template | `templates/` | Easy |
| Node UI improvements | `apps/desktop/src/canvas/nodes/` | Medium |
| New execution mode | `packages/sidecar/neuralflow/execution/` | Hard |
| MCP improvements | `packages/sidecar/neuralflow/mcp/` | Medium |

## Pull Request Guidelines

- One PR per feature or fix
- Frontend: `pnpm lint && pnpm typecheck` must pass
- Backend: `uv run pytest` must pass
- Keep PRs small — split large changes into logical commits
- Add a brief description of what changed and why

## Commit Style

```
feat: add web browser tool using Playwright
fix: correct cost calculation for cached tokens
docs: update MCP setup guide
refactor: simplify workflow analyzer topological sort
```

## Reporting Issues

Use GitHub Issues. Include:
- NeuralFlow version
- OS and version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs (Settings → Open Log File)

## License

By contributing, you agree your contributions are licensed under Apache 2.0.
