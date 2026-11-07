import streamlit as st
from rag import get_rag_answer
from okf_aware import get_okf_answer

st.set_page_config(page_title="OKF HR Knowledge Agent", layout="wide")

st.title("OKF HR Knowledge Agent")
st.markdown("Ask an HR policy question and see how **Plain RAG** vs **OKF-Aware RAG** respond differently.")

st.markdown("---")

# sample questions
sample_questions = [
    "How many annual leave days do employees get?",
    "Can I work remotely?",
    "How do I claim expenses for internet at home?",
    "What happens during a performance review?",
    "What is the code of conduct around confidentiality?",
]

st.markdown("**Try a sample question:**")
cols = st.columns(len(sample_questions))
selected_sample = None
for i, q in enumerate(sample_questions):
    if cols[i].button(q, key=f"sample_{i}"):
        selected_sample = q

question = st.text_input(
    "Or type your own question:",
    value=selected_sample if selected_sample else "",
    placeholder="e.g. How many leave days do I get?"
)

if st.button("Ask", type="primary") and question:
    left, right = st.columns(2)

    with left:
        st.subheader("Plain RAG")
        st.caption("Retrieves by similarity only. No metadata filtering. May return superseded policies.")
        with st.spinner("Retrieving and generating..."):
            rag_answer, rag_sources = get_rag_answer(question)
        st.markdown(rag_answer)
        st.markdown("**Sources retrieved:**")
        for s in rag_sources:
            st.markdown(f"- `{s}`")

    with right:
        st.subheader("OKF-Aware RAG")
        st.caption("Filters to `status: stable` only. Follows markdown links. Shows provenance signals.")
        with st.spinner("Retrieving stable policies and generating..."):
            okf_answer, okf_sources, okf_signals = get_okf_answer(question)
        st.markdown(okf_answer)
        st.markdown("**Sources retrieved:**")
        for s in okf_sources:
            st.markdown(f"- `{s}`")

        st.markdown("**OKF Signals used:**")
        for sig in okf_signals:
            with st.expander(f"{sig['source_file']}"):
                st.markdown(f"- **Status:** `{sig['status']}`")
                st.markdown(f"- **Version:** `{sig['version']}`")
                st.markdown(f"- **Verified by:** `{sig['verified_by']}`")
                st.markdown(f"- **Verified at:** `{sig['verified_at']}`")
                st.markdown(f"- **Stale after:** `{sig['stale_after']}`")

st.markdown("---")
st.caption("Built with LangChain · ChromaDB · Nomic Embed · Qwen2.5 via Ollama · OKF v0.2")
