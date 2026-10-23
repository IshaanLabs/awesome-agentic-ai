# ─────────────────────────────────────────────
#  config.py  —  single source of truth
#  Update your keys, ports, and URLs here only
# ─────────────────────────────────────────────

# ── Ollama ────────────────────────────────────
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "granite4.1:3b"

# ── Tavily ────────────────────────────────────
TAVILY_API_KEY = "your-tavily-api-key-here"



# ── Agent Ports ───────────────────────────────
RESEARCH_AGENT_PORT   = 9000
CALCULATOR_AGENT_PORT = 9001
TIME_AGENT_PORT       = 9002

# ── Agent URLs (used by orchestrator) ─────────
RESEARCH_AGENT_URL   = f"http://localhost:{RESEARCH_AGENT_PORT}"
CALCULATOR_AGENT_URL = f"http://localhost:{CALCULATOR_AGENT_PORT}"
TIME_AGENT_URL       = f"http://localhost:{TIME_AGENT_PORT}"

# ── MCP Servers ───────────────────────────────
AWS_DOCS_MCP_COMMAND  = "uvx"
AWS_DOCS_MCP_ARGS     = ["awslabs.aws-documentation-mcp-server@latest"]

LANGCHAIN_DOCS_MCP_COMMAND = "uvx"
LANGCHAIN_DOCS_MCP_ARGS    = ["langchain-docs-mcp@latest"]

TAVILY_MCP_COMMAND = "uvx"
TAVILY_MCP_ARGS    = ["tavily-mcp@latest"]

# ── Streamlit ─────────────────────────────────
STREAMLIT_PORT = 8501
