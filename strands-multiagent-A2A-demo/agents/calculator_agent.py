import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strands import Agent
from strands.models.ollama import OllamaModel
from strands.multiagent.a2a import A2AServer
from strands_tools import calculator

from config import OLLAMA_HOST, OLLAMA_MODEL, CALCULATOR_AGENT_PORT

def create_model():
    print(f"[Calculator Agent] Connecting to Ollama model: {OLLAMA_MODEL}")
    return OllamaModel(
        model_id=OLLAMA_MODEL,
        host=OLLAMA_HOST
    )

def create_agent(model):
    print("[Calculator Agent] Creating agent with calculator tool...")
    return Agent(
        name="Calculator Agent",
        description="Performs arithmetic, percentages, cost estimates, and numeric calculations.",
        model=model,
        tools=[calculator],
        callback_handler=None,
    )

def start_server():
    print(f"[Calculator Agent] Starting A2A server on port {CALCULATOR_AGENT_PORT}...")
    model = create_model()
    agent = create_agent(model)
    print(f"[Calculator Agent] ✅ Ready and listening on http://localhost:{CALCULATOR_AGENT_PORT}")
    A2AServer(agent=agent, port=CALCULATOR_AGENT_PORT).serve()

if __name__ == "__main__":
    start_server()
