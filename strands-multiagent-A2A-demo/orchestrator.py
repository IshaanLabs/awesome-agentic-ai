from strands import Agent
from strands.models.ollama import OllamaModel
from strands_tools.a2a_client import A2AClientToolProvider

from config import (
    OLLAMA_HOST, OLLAMA_MODEL,
    RESEARCH_AGENT_URL, CALCULATOR_AGENT_URL, TIME_AGENT_URL
)

SYSTEM_PROMPT = """You are a helpful research assistant that answers questions about AWS, LangChain, and general topics.

You have access to three specialist agents:
- Research Agent: fetches AWS docs, LangChain docs, and searches the web
- Calculator Agent: performs any numeric calculations or cost estimates
- Time Agent: tells the current time in any city or timezone

For each user question:
1. Identify which specialist(s) are needed
2. Call them in the right order
3. Combine their answers into one clear, concise response

Always delegate to specialists, do not answer from memory alone."""

def create_model():
    print(f"[Orchestrator] Connecting to Ollama model: {OLLAMA_MODEL}")
    return OllamaModel(
        model_id=OLLAMA_MODEL,
        host=OLLAMA_HOST
    )

def connect_specialists():
    print("[Orchestrator] Discovering specialist agents via A2A...")
    provider = A2AClientToolProvider(
        known_agent_urls=[
            RESEARCH_AGENT_URL,
            CALCULATOR_AGENT_URL,
            TIME_AGENT_URL,
        ]
    )
    print(f"[Orchestrator] Specialists found: {[t.tool_name for t in provider.tools]}")
    return provider.tools

def create_orchestrator(model, tools):
    print("[Orchestrator] Creating orchestrator agent...")
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
    )

def ask(orchestrator, question):
    print(f"\n[Orchestrator] Received question: {question}")
    print("[Orchestrator] Routing to specialist(s)...")
    response = orchestrator(question)
    print("[Orchestrator] ✅ Response ready")
    return response

def build_orchestrator():
    model = create_model()
    tools = connect_specialists()
    orchestrator = create_orchestrator(model, tools)
    print("[Orchestrator] ✅ Ready to receive questions")
    return orchestrator

if __name__ == "__main__":
    orchestrator = build_orchestrator()
    print("\n[Orchestrator] Running in terminal mode. Type 'exit' to quit.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() == "exit":
            break
        response = ask(orchestrator, question)
        print(f"\nAssistant: {response}")
