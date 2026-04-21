#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:?Usage: $0 <service> [timeout_seconds]}"
TIMEOUT="${2:-60}"

echo "=== Rolling deploy: ${SERVICE} (timeout: ${TIMEOUT}s) ==="

# Build new image
docker compose build "${SERVICE}"

# Start new container (replaces old one)
docker compose up -d --no-deps "${SERVICE}"

CONTAINER_ID=$(docker compose ps -q "${SERVICE}" | head -1)

# Wait for health check to pass
elapsed=0
echo "Waiting for ${SERVICE} to become healthy..."

while [ "${elapsed}" -lt "${TIMEOUT}" ]; do
  health=$(docker inspect \
    --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-check{{end}}' \
    "${CONTAINER_ID}" 2>/dev/null || echo "error")

  case "${health}" in
    healthy|no-check)
      echo "✓ ${SERVICE} is ${health} after ${elapsed}s — deploy successful"
      exit 0
      ;;
    unhealthy)
      echo "✗ ${SERVICE} is unhealthy after ${elapsed}s — aborting"
      docker compose logs --tail 30 "${SERVICE}"
      exit 1
      ;;
  esac

  sleep 5
  elapsed=$((elapsed + 5))
  echo "  [${elapsed}/${TIMEOUT}s] status: ${health}"
done

echo "✗ Health check timed out after ${TIMEOUT}s — aborting, old container left running"
docker compose logs --tail 30 "${SERVICE}"
exit 1
