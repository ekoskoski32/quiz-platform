#!/bin/bash
# Start the quiz platform. Run: bash ~/quiz-platform/start.sh

PROJ="$HOME/quiz-platform"
PYTHON="/opt/homebrew/bin/python3.11"
SITE="$PROJ/venv/lib/python3.11/site-packages"

echo "Starting PostgreSQL..."
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
brew services start postgresql@17 2>/dev/null || true
sleep 1

echo "Starting backend..."
cd "$PROJ/backend"
# PYTHONPATH set explicitly — clears any injected paths (e.g. from Hermes)
# PYTHONNOUSERSITE prevents user-level site-packages from leaking in
PYTHONPATH="$SITE" PYTHONNOUSERSITE=1 "$PYTHON" manage.py runserver 8000 &
BACKEND_PID=$!

echo "Starting frontend..."
cd "$PROJ/frontend"
npm run dev &
FRONTEND_PID=$!

echo "Waiting for servers..."
sleep 4

echo ""
echo "✅ Running at http://localhost:5173"
echo "Press Ctrl+C to stop."

open http://localhost:5173

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
