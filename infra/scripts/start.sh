#!/bin/bash
set -e
echo "🚀 Starting superTrade..."

cd "$(dirname "$0")/../.."

# Backend
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt --quiet
cp -n .env.example .env 2>/dev/null || true
cd ..

# Frontend
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install --silent
cp -n .env.example .env 2>/dev/null || true
cd ..

echo "✅ Starting backend on :8000..."
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

echo "✅ Starting frontend on :5173..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "═══════════════════════════════════════════"
echo "  APEX — superTrade"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/api/docs"
echo "═══════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
