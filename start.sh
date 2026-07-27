#!/bin/bash
# Start the quiz platform.
# Usage: bash ~/quiz-platform/start.sh

PROJ="$HOME/quiz-platform"
PYTHON="/opt/homebrew/bin/python3.11"
PYPATH="$PROJ/venv/lib/python3.11/site-packages"

echo "Starting PostgreSQL..."
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
brew services start postgresql@17 2>/dev/null || true
sleep 1

echo "Starting backend..."
cd "$PROJ/backend"
PYTHONPATH="$PYPATH" "$PYTHON" manage.py runserver 8000 &
BACKEND_PID=$!

echo "Starting frontend..."
cd "$PROJ/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Waiting for servers..."
sleep 4

echo ""
echo "✅ Quiz platform is running!"
echo "   Open: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop."

open http://localhost:5173

trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
