#!/bin/bash
# Start the Neuromorphic Multi-Agent Reviewer (backend + built-in UI)
cd "$(dirname "$0")/backend"
export PYTHONPATH=.
echo "Starting server at http://localhost:8000"
echo "Open that URL in your browser for the UI."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
