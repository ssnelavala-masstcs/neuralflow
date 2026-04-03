# ─── Build stage ───
FROM python:3.12-slim AS sidecar-builder

WORKDIR /build
COPY packages/sidecar/ .
RUN pip install --no-cache-dir uv && uv sync --frozen

# ─── Frontend build stage ───
FROM node:22-alpine AS frontend-builder

WORKDIR /build
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY apps/desktop/package.json apps/desktop/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY apps/desktop/ .
RUN pnpm build

# ─── Runtime stage ───
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy sidecar
COPY --from=sidecar-builder /build/.venv /app/.venv
COPY --from=sidecar-builder /build/neuralflow /app/neuralflow
COPY --from=sidecar-builder /build/pyproject.toml /app/

# Copy frontend static files
COPY --from=frontend-builder /build/dist /app/static

ENV NEURALFLOW_HOST=0.0.0.0
ENV NEURALFLOW_PORT=7411
ENV PYTHONUNBUFFERED=1

EXPOSE 7411

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7411/health || exit 1

CMD ["/app/.venv/bin/uvicorn", "neuralflow.main:app", "--host", "0.0.0.0", "--port", "7411"]
