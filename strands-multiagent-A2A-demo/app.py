import streamlit as st
from orchestrator import build_orchestrator, ask

st.set_page_config(page_title="Strands Multi-Agent Demo", page_icon="🤖", layout="centered")

st.title("🤖 Strands Multi-Agent A2A Demo")
st.caption("Powered by Strands Agents + Ollama (granite4.1:3b) + MCP + A2A")

st.markdown("""
**What this demo can do:**
- 📚 Research AWS and LangChain documentation
- 🔍 Search the web via Tavily
- 🧮 Perform calculations and cost estimates
- 🕐 Tell the current time in any timezone
""")

st.divider()

# ── Initialize orchestrator once per session ──
if "orchestrator" not in st.session_state:
    print("[App] Initializing orchestrator for the first time...")
    with st.spinner("Connecting to specialist agents..."):
        st.session_state.orchestrator = build_orchestrator()
    print("[App] ✅ Orchestrator ready")

# ── Chat history ──
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display chat history ──
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ── Sample questions ──
st.sidebar.title("💡 Try these questions")
sample_questions = [
    "What is Amazon S3 and how much would it cost to store 500GB?",
    "What is LangChain and what can I build with it?",
    "What time is it in Lagos and Nairobi right now?",
    "Search the web for the latest news on AI agents",
    "What is 15% of 48,000 naira?",
    "Compare AWS Lambda vs EC2 for 1 million requests per month",
]
for q in sample_questions:
    if st.sidebar.button(q, use_container_width=True):
        st.session_state.prefill = q

# ── Chat input ──
prefill = st.session_state.pop("prefill", "")
prompt = st.chat_input("Ask your agents something...") or prefill

if prompt:
    print(f"[App] User asked: {prompt}")

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agents are working on it..."):
            response = ask(st.session_state.orchestrator, prompt)
            response_text = str(response)

        st.write(response_text)
        print(f"[App] Response delivered to UI")

    st.session_state.messages.append({"role": "assistant", "content": response_text})
