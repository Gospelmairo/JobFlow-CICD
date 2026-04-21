# Bug Fixes

All issues found in the original starter repository and how they were resolved.

---

## api/main.py

| # | Line | Problem | Fix |
|---|------|---------|-----|
| 1 | 8 | `redis.Redis(host="localhost")` — hardcoded hostname fails inside containers where Redis runs as a separate service | Changed to `os.getenv("REDIS_HOST", "redis")` |
| 2 | 8 | Redis client created without password despite `REDIS_PASSWORD` being defined in `.env` | Added `password=os.getenv("REDIS_PASSWORD") or None` |
| 3 | 13–14 | Race condition — `lpush` (enqueue) runs before `hset` (store metadata). Worker can dequeue a job_id before its metadata exists in Redis | Swapped order: `hset` first, then `lpush` |
| 4 | 19–21 | `get_job` returns HTTP 200 with `{"error": "not found"}` when a job does not exist — clients cannot distinguish success from failure | Replaced with `raise HTTPException(status_code=404, detail="Job not found")` |
| 5 | — | No `/health` endpoint — Dockerfile and docker-compose HEALTHCHECK had nothing to check | Added `GET /health` returning `{"status": "ok"}` |

---

## worker/worker.py

| # | Line | Problem | Fix |
|---|------|---------|-----|
| 6 | 6 | `redis.Redis(host="localhost")` — same hardcoded hostname issue as API | Changed to `os.getenv("REDIS_HOST", "redis")` |
| 7 | 6 | No Redis password supplied | Added `password=os.getenv("REDIS_PASSWORD") or None` |
| 8 | 4 | `import signal` present but never used — no signal handlers implemented, preventing graceful shutdown | Implemented `SIGTERM`/`SIGINT` handlers that set `running = False` to stop the loop cleanly |
| 9 | 8–11 | `process_job` has no error handling — any exception crashes the worker silently | Wrapped body in `try/except`; sets job status to `"failed"` on error |

---

## frontend/app.js

| # | Line | Problem | Fix |
|---|------|---------|-----|
| 10 | 6 | `API_URL = "http://localhost:8000"` — hardcoded, fails in containers | Changed to `process.env.API_URL \|\| "http://localhost:8000"` |
| 11 | 13 | `axios.post(API_URL/jobs)` does not forward `req.body` — any payload sent by the client is silently dropped | Changed to `axios.post(\`${API_URL}/jobs\`, req.body)` |
| 12 | 15, 25 | `catch` blocks return a generic message and swallow the real error — impossible to debug failures | Added `console.error(err.message)` logging in both catch blocks |
| 13 | 15, 25 | Error responses always return HTTP 500 regardless of the upstream status code | Now propagates `err.response.status` when available |

---

## api/.env

| # | Problem | Fix |
|---|---------|-----|
| 14 | `api/.env` containing `REDIS_PASSWORD=supersecretpassword123` was committed to the repository — credentials in version control | Removed from git tracking (`git rm --cached api/.env`), added to `.gitignore`, created `.env.example` with placeholder values |
