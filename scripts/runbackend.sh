#!/bin/bash
cd "$(dirname "$0")"
PYTHONPATH=. uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
