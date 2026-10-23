import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.models.ollama import OllamaModel
from strands.multiagent.a2a import A2AServer
from strands.tools.mcp import MCPClient

from config import (
    OLLAMA_HOST, OLLAMA_MODEL, RESEARCH_AGENT_PORT,
    AWS_DOCS_MCP_COMMAND, AWS_DOCS_MCP_ARGS,
    LANGCHAIN_DOCS_MCP_COMMAND, LANGCHAIN_DOCS_MCP_ARGS,
    TAVILY_MCP_COMMAND, TAVILY_MCP_ARGS,
    TAVILY_API_KEY
)

def create_model():
    print(f"[Research Agent] Connecting to Ollama model: {OLLAMA_MODEL}")
    return OllamaModel(
        model_id=OLLAMA_MODEL,
        host=OLLAMA_HOST
    )

def connect_mcp_servers():
    print("[Research Agent] Connecting to AWS Docs MCP server...")
    aws_docs = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command=AWS_DOCS_MCP_COMMAND,
                args=AWS_DOCS_MCP_ARGS,
            )
        )
    )

    print("[Research Agent] Connecting to LangChain Docs MCP server...")
    langchain_docs = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command=LANGCHAIN_DOCS_MCP_COMMAND,
                args=LANGCHAIN_DOCS_MCP_ARGS,
            )
        )
    )

    print("[Research Agent] Connecting to Tavily MCP server...")
    tavily = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command=TAVILY_MCP_COMMAND,
                args=TAVILY_MCP_ARGS,
                env={"TAVILY_API_KEY": TAVILY_API_KEY},
            )
        )
    )

    return aws_docs, langchain_docs, tavily

def collect_tools(aws_docs, langchain_docs, tavily):
    print("[Research Agent] Collecting tools from all MCP servers...")

    aws_tools = aws_docs.list_tools_sync()
    print(f"[Research Agent] AWS Docs tools: {[t.tool_name for t in aws_tools]}")

    lc_tools = langchain_docs.list_tools_sync()
    print(f"[Research Agent] LangChain Docs tools: {[t.tool_name for t in lc_tools]}")

    tavily_tools = tavily.list_tools_sync()
    print(f"[Research Agent] Tavily tools: {[t.tool_name for t in tavily_tools]}")

    all_tools = aws_tools + lc_tools + tavily_tools
    print(f"[Research Agent] Total tools available: {len(all_tools)}")
    return all_tools

def create_agent(model, tools):
    print("[Research Agent] Creating agent with all MCP tools...")
    return Agent(
        name="Research Agent",
        description="Researches AWS documentation, LangChain documentation, and searches the web using Tavily.",
        model=model,
        tools=tools,
        callback_handler=None,
    )

def start_server():
    print(f"[Research Agent] Starting A2A server on port {RESEARCH_AGENT_PORT}...")
    model = create_model()
    aws_docs, langchain_docs, tavily = connect_mcp_servers()

    with aws_docs, langchain_docs, tavily:
        tools = collect_tools(aws_docs, langchain_docs, tavily)
        agent = create_agent(model, tools)
        print(f"[Research Agent] ✅ Ready and listening on http://localhost:{RESEARCH_AGENT_PORT}")
        A2AServer(agent=agent, port=RESEARCH_AGENT_PORT).serve()

if __name__ == "__main__":
    start_server()
