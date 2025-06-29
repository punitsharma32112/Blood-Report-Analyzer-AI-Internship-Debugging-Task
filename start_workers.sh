#!/bin/bash

# Blood Test Analysis System - Celery Worker Startup Script

echo "Starting Blood Test Analysis Celery Workers..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: No virtual environment detected. Make sure to activate your venv first:"
    echo "source venv/bin/activate"
    echo ""
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Error: Redis is not running. Please start Redis first:"
    echo "sudo systemctl start redis"
    echo "or"
    echo "redis-server"
    exit 1
fi

echo "Redis is running ✓"

# Start Celery worker
echo "Starting Celery worker..."
celery -A celery_app worker --loglevel=info --concurrency=2 &
WORKER_PID=$!

# Start Celery beat (for periodic tasks)
echo "Starting Celery beat..."
celery -A celery_app beat --loglevel=info &
BEAT_PID=$!

# Start Flower (monitoring)
echo "Starting Flower monitoring on http://localhost:5555"
celery -A celery_app flower --port=5555 &
FLOWER_PID=$!

echo ""
echo "All services started!"
echo "Worker PID: $WORKER_PID"
echo "Beat PID: $BEAT_PID"
echo "Flower PID: $FLOWER_PID"
echo ""
echo "To stop all services, run: kill $WORKER_PID $BEAT_PID $FLOWER_PID"
echo "Or press Ctrl+C to stop this script and all background processes"

# Wait for interrupt
trap "echo 'Stopping all services...'; kill $WORKER_PID $BEAT_PID $FLOWER_PID 2>/dev/null; exit" INT TERM

# Keep script running
wait 