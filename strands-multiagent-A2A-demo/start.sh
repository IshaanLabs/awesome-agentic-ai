#!/bin/bash

# ─────────────────────────────────────────────
#  start.sh — starts all agents and Streamlit UI
#  Uses venv at /your-env-path/
# ─────────────────────────────────────────────

VENV_PATH="/your-env-path"
PROJECT_DIR="strands-multiagent-A2A-demo"

echo "🔧 Activating virtual environment from $VENV_PATH..."
source "$VENV_PATH/bin/activate"

echo "📁 Moving to project directory..."
cd "$PROJECT_DIR"

echo ""
echo "🚀 Starting specialist agents..."

echo "  → Starting Research Agent (port 9000)..."
python agents/research_agent.py &
RESEARCH_PID=$!

echo "  → Starting Calculator Agent (port 9001)..."
python agents/calculator_agent.py &
CALC_PID=$!

echo "  → Starting Time Agent (port 9002)..."
python agents/time_agent.py &
TIME_PID=$!

echo ""
echo "⏳ Waiting for agents to be ready (10 seconds)..."
sleep 10

echo ""
echo "🌐 Starting Streamlit UI..."
streamlit run app.py &
STREAMLIT_PID=$!

echo ""
echo "✅ All services running!"
echo "   Research Agent  → http://localhost:9000  (PID: $RESEARCH_PID)"
echo "   Calculator Agent → http://localhost:9001  (PID: $CALC_PID)"
echo "   Time Agent       → http://localhost:9002  (PID: $TIME_PID)"
echo "   Streamlit UI     → http://localhost:8501  (PID: $STREAMLIT_PID)"
echo ""
echo "Press Ctrl+C to stop all services..."

# ── Stop all on Ctrl+C ──
trap "echo ''; echo '🛑 Stopping all services...'; kill $RESEARCH_PID $CALC_PID $TIME_PID $STREAMLIT_PID; echo '✅ All stopped.'; exit 0" SIGINT

wait
