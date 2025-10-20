#!/bin/bash
# RunPod startup script
# Starts FastAPI server in background and runs RunPod handler

set -e

echo "Starting Holo1.5-7B VLM API for RunPod Serverless..."

# Start FastAPI server in the background
echo "Starting FastAPI server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Wait for the server to be ready
echo "Waiting for server to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Server is ready"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "✗ Server failed to start within 60 seconds"
        exit 1
    fi
    sleep 1
done

# Keep the process running
echo "✓ RunPod Serverless Handler Ready"
wait $FASTAPI_PID
