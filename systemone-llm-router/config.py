import os

from dotenv import load_dotenv

load_dotenv()

# --- Ollama / classifier ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CLASSIFIER_MODEL = "tev1:0.8b-bf16"
REQUEST_TIMEOUT_S = 30

# tev1 runs with ~2000 tokens of context, so keep the prompt short
MAX_PROMPT_CHARS = 4000

# --- Routes: route name -> intended model (labels only, nothing is called) ---
ROUTES = {
    "small": "granite4.1:3b",
    "general": "qwen2.5:14b",
    "coding": "ornith-1.5-35b-a3b",
    "frontier": "gemini-flash",
}

# --- Rule thresholds (tune these) ---
THRESHOLDS = {
    "min_confidence": 0.5,      # task_type confidence below this -> escalate to general
    "frontier_complexity": 1.7,  # complexity score (0-2) at or above this -> frontier
    "general_complexity": 1.0,   # complexity score above this -> general
    "web_probability": 0.7,      # needs_fresh_info probability at or above this -> needs_web
}
