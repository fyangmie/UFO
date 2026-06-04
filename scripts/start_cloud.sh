#!/usr/bin/env bash
set -euo pipefail

uvicorn backend.main:app --host 127.0.0.1 --port "${UFO_BACKEND_PORT:-8000}" &

streamlit run frontend/streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT:-7860}" \
  --server.headless true \
  --browser.gatherUsageStats false
