# HNG14 Stage 2 DevOps — Containerised Job Processing System

A microservices job processing application containerised with Docker and deployed via a GitHub Actions CI/CD pipeline.

## Architecture

| Service | Tech | Role |
|---------|------|------|
| `frontend` | Node.js / Express | UI and proxy to API |
| `api` | Python / FastAPI | Creates jobs, serves status |
| `worker` | Python | Processes jobs from the queue |
| `redis` | Redis 7 | Shared job queue and state store |

## Prerequisites

- Docker Desktop (v24+) with Docker Compose v2
- Git

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Gospelmairo/hng14-stage2-devops.git
cd hng14-stage2-devops

# 2. Create your environment file
cp .env.example .env
# Edit .env and set a strong REDIS_PASSWORD

# 3. Build and start the full stack
docker compose up -d --build --wait

# 4. Open the dashboard
open http://localhost:3000
```

### Successful startup looks like

```
✔ Container hng14-stage2-devops-redis-1    Healthy
✔ Container hng14-stage2-devops-api-1      Healthy
✔ Container hng14-stage2-devops-worker-1   Healthy
✔ Container hng14-stage2-devops-frontend-1 Healthy
```

### Useful commands

```bash
docker compose logs -f          # stream all logs
docker compose logs -f api      # stream API logs only
docker compose ps               # check service status
docker compose down -v          # stop and remove volumes
```

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_PASSWORD` | Password for Redis | *(required)* |
| `FRONTEND_PORT` | Host port for the frontend | `3000` |

## API Endpoints

### Frontend (port 3000)
- `POST /submit` — submit a new job
- `GET /status/:id` — check job status

### API service (internal port 8000)
- `POST /jobs` — create a job → `{"job_id": "<uuid>"}`
- `GET /jobs/:id` — get status → `{"job_id": "...", "status": "queued|completed|failed"}`
- `GET /health` → `{"status": "ok"}`

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push and PR:

```
lint → test → build → security-scan → integration-test → deploy
```

| Stage | What it does |
|-------|-------------|
| **lint** | flake8 (Python), eslint (JS), hadolint (Dockerfiles) |
| **test** | pytest with mocked Redis, uploads coverage report artifact |
| **build** | Builds all 3 images, tags with git SHA + latest, pushes to local registry |
| **security-scan** | Trivy scans all images, fails on CRITICAL findings, uploads SARIF artifact |
| **integration-test** | Brings full stack up, submits a job, polls until completed, tears down |
| **deploy** | Rolling update on push to `main` only (requires secrets below) |

### GitHub Secrets required for deploy

| Secret | Value |
|--------|-------|
| `SERVER_HOST` | Your server IP or hostname |
| `SSH_PRIVATE_KEY` | Private key for `hngdevops` user |
| `REDIS_PASSWORD` | Production Redis password |

## Bug Fixes

See [FIXES.md](FIXES.md) for a full list of all bugs found and fixed.
