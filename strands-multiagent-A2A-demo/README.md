# 🤖 Strands Multi-Agent A2A Demo

A hands-on demonstration of building a **multi-agent AI system** using the [Strands Agents SDK](https://strandsagents.com), powered entirely by a **local Ollama model** (no cloud costs, no API keys for the LLM). The system showcases **Agent-to-Agent (A2A)** communication, **Model Context Protocol (MCP)** integrations, and a **Streamlit** web interface — all running on your machine.

---

## Tech Stack

| Layer                 | Technology                                             |
| --------------------- | ------------------------------------------------------ |
| Agent Framework       | [Strands Agents SDK](https://strandsagents.com)           |
| LLM                   | [Ollama](https://ollama.com) — `granite4.1:3b` (local) |
| Agent Communication   | A2A Protocol (Agent-to-Agent)                          |
| External Integrations | MCP (Model Context Protocol)                           |
| MCP Servers           | AWS Docs MCP, LangChain Docs MCP, Tavily MCP           |
| Web Search            | [Tavily](https://tavily.com)                              |
| UI                    | [Streamlit](https://streamlit.io)                         |
| Language              | Python 3.10+                                           |

---

## Project Structure

```
strands-multiagent-A2A-demo/
├── agents/
│   ├── research_agent.py      # Fetches AWS docs, LangChain docs, web search via MCP
│   ├── calculator_agent.py    # Performs numeric calculations and cost estimates
│   └── time_agent.py          # Tells current time in any city or timezone
├── orchestrator.py            # Routes user questions to the right specialist agent(s)
├── app.py                     # Streamlit web UI
├── config.py                  # All configuration — keys, ports, URLs, model settings
├── requirements.txt           # Python dependencies
├── start.sh                   # One-command startup script
└── README.md
```

---

## Installation

**1. Clone the repository**

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/awesome-agentic-ai.git
cd awesome-agentic-ai
git sparse-checkout set strands-multiagent-A2A-demo
git checkout
cd strands-multiagent-A2A-demo
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
pip install "strands-agents[a2a]" "a2a-sdk"
```

**4. Install and start Ollama**

Download Ollama from [ollama.com](https://ollama.com), then:

```bash
ollama serve
ollama pull granite4.1:3b
```

**5. Install `uvx` (required for MCP servers)**

```bash
pip install uv
```

---

## Configuration

All configuration lives in `config.py`. Open it and update the following:

```python
# Ollama — change model here anytime
OLLAMA_HOST  = "http://localhost:11434"
OLLAMA_MODEL = "granite4.1:3b"

# Tavily — paste your API key here
# Get a free key at https://tavily.com (1000 searches/month free)
TAVILY_API_KEY = "your-tavily-api-key-here"

# Agent ports — change if any port is already in use
RESEARCH_AGENT_PORT   = 9000
CALCULATOR_AGENT_PORT = 9001
TIME_AGENT_PORT       = 9002
```

> No other file needs to be touched for configuration.

---

## Usage

### Option 1 — One command (recommended)

```bash
bash start.sh
```

This will:

- Activate the virtual environment
- Start all 3 specialist agents in the background
- Wait 10 seconds for agents to be ready
- Launch the Streamlit UI

Then open your browser at **http://localhost:8501**

### Option 2 — Manual (4 terminals)

```bash
# Terminal 1
python agents/research_agent.py

# Terminal 2
python agents/calculator_agent.py

# Terminal 3
python agents/time_agent.py

# Terminal 4 — after all agents are ready
streamlit run app.py
```

### Example Questions to Try

- `"What is Amazon S3 and how much would it cost to store 500GB?"`
- `"What is LangChain and what can I build with it?"`
- `"What time is it in Lagos and Nairobi right now?"`
- `"Search the web for the latest news on AI agents"`
- `"What is 15% of 48,000?"`
- `"Compare AWS Lambda vs EC2 for 1 million requests per month"`

---

## How It Works

```
User (Streamlit UI :8501)
          │
          ▼
  Orchestrator Agent
  (decides who handles what)
          │
    ┌─────┼──────┐
    ▼     ▼      ▼
Research  Calc  Time
Agent    Agent  Agent
:9000    :9001  :9002
  │
  ├──► AWS Docs MCP Server
  ├──► LangChain Docs MCP Server
  └──► Tavily MCP Server (web search)
```

1. User types a question in the Streamlit UI
2. Orchestrator receives it and decides which specialist(s) to call via A2A
3. Specialist agents use their tools (MCP / calculator / current_time) to get real answers
4. Orchestrator combines the results into one clear response
5. Answer appears in the UI

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) file for details.
