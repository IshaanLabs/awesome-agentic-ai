import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strands import Agent
from strands.models.ollama import OllamaModel
from strands.multiagent.a2a import A2AServer
from strands_tools import current_time

from config import OLLAMA_HOST, OLLAMA_MODEL, TIME_AGENT_PORT

def create_model():
    print(f"[Time Agent] Connecting to Ollama model: {OLLAMA_MODEL}")
    return OllamaModel(
        model_id=OLLAMA_MODEL,
        host=OLLAMA_HOST
    )

def create_agent(model):
    print("[Time Agent] Creating agent with current_time tool...")
    return Agent(
        name="Time Agent",
        description="Tells the current time in any city or timezone around the world.",
        model=model,
        tools=[current_time],
        callback_handler=None,
    )

def start_server():
    print(f"[Time Agent] Starting A2A server on port {TIME_AGENT_PORT}...")
    model = create_model()
    agent = create_agent(model)
    print(f"[Time Agent] ✅ Ready and listening on http://localhost:{TIME_AGENT_PORT}")
    A2AServer(agent=agent, port=TIME_AGENT_PORT).serve()

if __name__ == "__main__":
    start_server()
