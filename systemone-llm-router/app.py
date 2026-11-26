import pandas as pd
import streamlit as st

import config
from router.pipeline import route

st.title("Prompt-aware model router")
st.caption(f"Classifier: {config.CLASSIFIER_MODEL} at {config.OLLAMA_BASE_URL}")

# sidebar sliders override the thresholds from config.py for this session
st.sidebar.header("Thresholds")
thresholds = {
    "min_confidence": st.sidebar.slider("min confidence", 0.0, 1.0, config.THRESHOLDS["min_confidence"], 0.05),
    "frontier_complexity": st.sidebar.slider("frontier complexity", 0.0, 2.0, config.THRESHOLDS["frontier_complexity"], 0.05),
    "general_complexity": st.sidebar.slider("general complexity", 0.0, 2.0, config.THRESHOLDS["general_complexity"], 0.05),
    "web_probability": st.sidebar.slider("web probability", 0.0, 1.0, config.THRESHOLDS["web_probability"], 0.05),
}

prompt = st.text_area("Prompt", height=150)

if st.button("Route it") and prompt.strip():
    try:
        decision = route(prompt, thresholds)
    except RuntimeError as error:
        st.error(str(error))
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Route", decision["route"])
    col2.metric("Intended model", decision["model"])
    col3.metric("Needs web", "yes" if decision["needs_web"] else "no")
    st.write(f"**Reason:** {decision['reason']}")
    st.caption(f"Classifier latency: {decision['latency_ms']:.0f} ms")

    answers = decision["answers"]
    probabilities = answers["task_type"].get("probabilities", {})
    if probabilities:
        st.subheader("Task type probabilities")
        st.bar_chart(pd.Series(probabilities))

    st.subheader("Raw classifier answers")
    st.json(answers)
