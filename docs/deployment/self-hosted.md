# Self-Hosting NeuralFlow

> **Author:** Stanley Sujith Nelavala | [Repository](https://github.com/ssnelavala-masstcs/neuralflow)

## Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- 2GB+ RAM, 1GB+ disk space

### 1. Clone the repository
```bash
git clone https://github.com/ssnelavala-masstcs/neuralflow.git
cd neuralflow
```

### 2. Start with Docker Compose
```bash
docker compose up -d
```

This starts the NeuralFlow sidecar on port **7411**.

### 3. Verify
```bash
curl http://localhost:7411/health
```

Expected response:
```json
{"status": "ok", "version": "0.1.0"}
```

### 4. Connect the Desktop App
1. Open NeuralFlow Desktop App
2. Click the **Globe** icon (Remote Connection)
3. Enter URL: `http://localhost:7411`
4. Click **Connect**

---

## With PostgreSQL (Multi-User Mode)

```bash
docker compose --profile postgres up -d
```

This starts both the sidecar and a PostgreSQL database.

---

## Manual Installation

### 1. Install dependencies
```bash
# Python sidecar
cd packages/sidecar
pip install uv
uv sync

# Frontend
cd apps/desktop
pnpm install
```

### 2. Start the sidecar
```bash
cd packages/sidecar
uv run uvicorn neuralflow.main:app --host 0.0.0.0 --port 7411 --reload
```

### 3. Start the frontend (dev mode)
```bash
cd apps/desktop
pnpm tauri dev
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEURALFLOW_HOST` | `127.0.0.1` | Host to bind |
| `NEURALFLOW_PORT` | `7411` | Port to listen on |
| `NEURALFLOW_LOG_LEVEL` | `INFO` | Logging level |
| `NEURALFLOW_CORS_ORIGINS` | `*` | Allowed CORS origins |
| `NEURALFLOW_DATABASE_URL` | (SQLite) | PostgreSQL connection string |

---

## Production Deployment

### Using Docker directly
```bash
docker build -t neuralflow .
docker run -d -p 7411:7411 \
  -v neuralflow-data:/root/.neuralflow \
  -e NEURALFLOW_CORS_ORIGINS=https://your-domain.com \
  neuralflow
```

### Behind a reverse proxy (Nginx)
```nginx
server {
    listen 443 ssl;
    server_name neuralflow.example.com;

    location / {
        proxy_pass http://localhost:7411;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
    }
}
```

---

## Backup & Restore

### Backup
```bash
docker run --rm -v neuralflow-data:/data -v $(pwd):/backup alpine tar czf /backup/neuralflow-backup.tar.gz -C /data .
```

### Restore
```bash
docker run --rm -v neuralflow-data:/data -v $(pwd):/backup alpine tar xzf /backup/neuralflow-backup.tar.gz -C /data
```

---

## Health Check

The container includes a health check that polls `/health` every 10 seconds.

```bash
docker inspect --format='{{.State.Health.Status}}' neuralflow-neuralflow-1
```

---

## Troubleshooting

### Sidecar won't start
```bash
docker compose logs neuralflow
```

### Database connection issues
```bash
docker compose logs postgres
docker compose exec postgres pg_isready
```

### Reset everything
```bash
docker compose down -v
docker compose up -d
```
