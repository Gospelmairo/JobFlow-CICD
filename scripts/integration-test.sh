#!/usr/bin/env bash
set -euo pipefail

TIMEOUT=60
BASE_URL="http://localhost:3000"

echo "=== Integration test: submit job and wait for completion ==="

RESPONSE=$(curl -sf -X POST "$BASE_URL/submit" \
  -H "Content-Type: application/json" -d '{}')
JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "Submitted job: $JOB_ID"

elapsed=0
while [ "$elapsed" -lt "$TIMEOUT" ]; do
  STATUS=$(curl -sf "$BASE_URL/status/$JOB_ID" | \
    python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))")
  echo "[$elapsed/${TIMEOUT}s] status: $STATUS"
  if [ "$STATUS" = "completed" ]; then
    echo "Job completed successfully"
    exit 0
  fi
  sleep 3
  elapsed=$((elapsed + 3))
done

echo "Job did not complete within ${TIMEOUT}s"
exit 1
