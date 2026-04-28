# JobFlow-CICD

A containerized microservices job-processing system with a full CI/CD pipeline  built with Docker, FastAPI, Redis, and GitHub Actions.

---

## Overview

JobFlow-CICD is a distributed job queue platform where users submit jobs via a web dashboard, an API queues them into Redis, and background workers process them asynchronously. Every code change is automatically linted, tested, security-scanned, and deployed through a multi-stage GitHub Actions pipeline.

![Job Processor Dashboard](screenshots/dashboard.png)

---

## Architecture

```
Browser
  │
  ▼
Frontend (Node.js/Express :3000)
  │  HTTP proxy
  ▼
API (Python/FastAPI :8000)
  │  enqueue / dequeue
  ▼
Redis :6379 ◄──── Worker (Python)
```

| Service | Technology | Port | Role |
|---------|-----------|------|------|
| `frontend` | Node.js / Express | 3000 | Web dashboard + API proxy |
| `api` | Python / FastAPI | 8000 | Job creation & status retrieval |
| `worker` | Python | — | Background job processor |
| `redis` | Redis 7 | 6379 | Job queue + state store |

---

## Quick Start

**Prerequisites:** Docker Desktop v24+ with Docker Compose v2

```bash
# 1. Clone the repository
git clone https://github.com/Gospelmairo/JobFlow-CICD.git
cd JobFlow-CICD

# 2. Set up environment variables
cp .env.example .env
# Edit .env — set a strong REDIS_PASSWORD

# 3. Build and start the full stack
docker compose up -d --build --wait

# 4. Open the dashboard
open http://localhost:3000
```

Successful startup output:
```
✔ Container jobflow-redis-1     Healthy
✔ Container jobflow-api-1       Healthy
✔ Container jobflow-worker-1    Healthy
✔ Container jobflow-frontend-1  Healthy
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `REDIS_PASSWORD` | Redis authentication password | Yes |
| `FRONTEND_PORT` | Host port for the frontend UI | No (default: `3000`) |

---

## API Reference

### Frontend (port 3000)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/submit` | Submit a new job |
| GET | `/status/:id` | Poll job status by ID |

### API Service (internal port 8000)

| Method | Path | Response |
|--------|------|----------|
| POST | `/jobs` | `{"job_id": "<uuid>"}` |
| GET | `/jobs/:id` | `{"job_id": "...", "status": "queued\|completed\|failed"}` |
| GET | `/health` | `{"status": "ok"}` |

---

## CI/CD Pipeline

![Pipeline Success](screenshots/pipeline-success.png)

Every push and pull request runs through a six-stage GitHub Actions pipeline:

```
lint → test → build → security-scan → integration-test → deploy
```

| Stage | Tool | What it does |
|-------|------|-------------|
| **lint** | flake8, eslint, hadolint | Checks Python style, JS style, and Dockerfile best practices |
| **test** | pytest + coverage | Runs unit tests with mocked Redis; uploads coverage report as artifact |
| **build** | Docker | Builds all 3 images, tags with git SHA + `latest`, pushes to registry |
| **security-scan** | Trivy | Scans all images for CRITICAL CVEs; fails the pipeline on fixable findings |
| **integration-test** | curl + bash | Brings full stack up, submits a job, polls until `completed`, tears down |
| **deploy** | SSH + rolling deploy | Rolling update on production server — triggered on push to `main` only |

### Rolling Deploy

The deploy stage updates each service one at a time (api → worker → frontend):
1. Build new image
2. Start new container
3. Wait up to 60 s for health check to pass
4. Abort and roll back logs if health check fails

### GitHub Secrets (required for deploy)

| Secret | Description |
|--------|-------------|
| `SERVER_HOST` | Production server IP or hostname |
| `SSH_PRIVATE_KEY` | Private key for the deploy user |
| `REDIS_PASSWORD` | Production Redis password |

---

## Project Structure

```
JobFlow-CICD/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .flake8
├── FIXES.md
│
├── api/                    # FastAPI backend
│   ├── main.py
│   ├── healthcheck.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
│       └── test_main.py
│
├── worker/                 # Background job processor
│   ├── worker.py
│   ├── healthcheck.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/               # Express dashboard + proxy
│   ├── app.js
│   ├── healthcheck.js
│   ├── Dockerfile
│   ├── package.json
│   └── views/
│       └── index.html
│
└── scripts/
    ├── rolling-deploy.sh   # Per-service rolling update
    └── integration-test.sh # End-to-end job flow test

.github/workflows/
└── ci.yml                  # Full CI/CD pipeline definition
```

---

## Useful Commands

```bash
docker compose logs -f            # Stream all service logs
docker compose logs -f api        # Stream API logs only
docker compose ps                 # Check service health status
docker compose down -v            # Stop stack and remove volumes
```

---

## Running Tests

```bash
cd api
pip install -r requirements.txt
pytest tests/ -v --cov=.
```

---

## Bug Fixes

See [FIXES.md](FIXES.md) for a full breakdown of all bugs found and fixed across the API, worker, and frontend services.

---

## Author

**Mairo Gospel**  
GitHub: [@Gospelmairo](https://github.com/Gospelmairo)
