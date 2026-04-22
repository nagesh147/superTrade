#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting superTrade..."
cd "$(dirname "$0")/../.."
ROOT_DIR="$(pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

cleanup() {
  echo ""
  echo "🛑 Stopping services..."
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "❌ Missing required command: $1"
    exit 1
  }
}

require_cmd npm

if command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "❌ Python not found"
  exit 1
fi

echo "🐍 Using Python: $PYTHON_BIN"

cd "$BACKEND_DIR"

if [[ -d ".venv" && ! -x ".venv/bin/python" ]]; then
  echo "⚠️ Existing backend/.venv is broken. Recreating..."
  rm -rf .venv
fi

if [[ ! -d ".venv" ]]; then
  echo "📦 Creating backend virtualenv..."
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate

PY_VER="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
echo "🐍 Virtualenv Python version: $PY_VER"

if [[ "$PY_VER" != "3.12" ]]; then
  echo "❌ This repo should run on Python 3.12 with the current pinned dependencies."
  echo "   Found: Python $PY_VER"
  echo "   Install python3.12 and recreate backend/.venv"
  exit 1
fi

echo "📦 Installing backend dependencies..."
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

if [[ -f ".env.example" && ! -f ".env" ]]; then
  cp .env.example .env
fi

echo "🎨 Installing frontend dependencies..."
cd "$FRONTEND_DIR"
npm install

if [[ -f ".env.example" && ! -f ".env" ]]; then
  cp .env.example .env
fi

echo "✅ Starting backend on :8000..."
cd "$BACKEND_DIR"
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

echo "✅ Starting frontend on :5173..."
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "═══════════════════════════════════════════"
echo "  superTrade"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/api/docs"
echo "═══════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop all services"

wait
