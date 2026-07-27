#!/bin/bash
# Start the quiz platform.
# Usage: bash ~/quiz-platform/start.sh

set -e

PROJ="$HOME/quiz-platform"

echo "Starting PostgreSQL..."
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
brew services start postgresql@17 2>/dev/null || true
sleep 1

echo "Starting backend..."
cd "$PROJ/backend"
source "$PROJ/venv/bin/activate"
python manage.py runserver 8000 &
BACKEND_PID=$!

echo "Starting frontend..."
cd "$PROJ/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Waiting for servers to start..."
sleep 4

echo ""
echo "✅ Quiz platform is running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers."

# Open browser
open http://localhost:5173

# Wait and clean up on Ctrl+C
trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
