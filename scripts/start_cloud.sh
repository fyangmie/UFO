#!/usr/bin/env bash
set -euo pipefail

backend_port="${UFO_BACKEND_PORT:-8000}"
backend_url="${UFO_BACKEND_URL:-http://127.0.0.1:${backend_port}}"
export UFO_BACKEND_URL="${backend_url}"

backend_pid=""
frontend_pid=""

cleanup() {
  if [[ -n "${frontend_pid}" ]]; then
    kill "${frontend_pid}" 2>/dev/null || true
  fi
  if [[ -n "${backend_pid}" ]]; then
    kill "${backend_pid}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

uvicorn backend.main:app --host 127.0.0.1 --port "${backend_port}" &
backend_pid=$!

backend_ready=0
for _ in $(seq 1 45); do
  if ! kill -0 "${backend_pid}" 2>/dev/null; then
    wait "${backend_pid}"
    exit $?
  fi

  if python - "${backend_url}" <<'PY'
import json
import sys
import urllib.request

url = sys.argv[1].rstrip("/") + "/health"
try:
    with urllib.request.urlopen(url, timeout=2) as response:
        payload = json.load(response)
except Exception:
    raise SystemExit(1)

raise SystemExit(0 if payload.get("model_loaded") else 1)
PY
  then
    backend_ready=1
    break
  fi

  sleep 1
done

if [[ "${backend_ready}" -ne 1 ]]; then
  echo "FastAPI backend did not become healthy within 45 seconds." >&2
  exit 1
fi

python app.py &
frontend_pid=$!

set +e
wait -n "${backend_pid}" "${frontend_pid}"
status=$?
set -e
exit "${status}"
