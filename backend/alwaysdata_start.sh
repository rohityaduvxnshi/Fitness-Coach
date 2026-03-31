#!/usr/bin/env bash
set -e

# alwaysdata User Program helper for FastAPI
# Working directory should be the backend/ folder.
# If the platform provides PORT, it will be used.

python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
