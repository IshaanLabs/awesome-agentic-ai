import json
import time

import httpx

import config
from router.questions import QUESTIONS


def build_request(prompt):
    # the questions refer to the state field by name, so the key must be "prompt"
    return {
        "model": config.CLASSIFIER_MODEL,
        "state": {"prompt": prompt},
        "questions": QUESTIONS,
    }


def ask_classifier(prompt):
    """Send one prompt to the classifier. Returns (answers, meta)."""
    if len(prompt) > config.MAX_PROMPT_CHARS:
        print(f"[classifier] prompt is {len(prompt)} chars, truncating to {config.MAX_PROMPT_CHARS}")
        prompt = prompt[: config.MAX_PROMPT_CHARS]

    url = f"{config.OLLAMA_BASE_URL}/v1/systemone"
    body = build_request(prompt)
    print(f"[classifier] POST {url} model={config.CLASSIFIER_MODEL}")

    start = time.perf_counter()
    try:
        response = httpx.post(url, json=body, timeout=config.REQUEST_TIMEOUT_S)
    except httpx.ConnectError:
        raise RuntimeError(f"Cannot reach Ollama at {config.OLLAMA_BASE_URL}. Is it running?")
    except httpx.TimeoutException:
        raise RuntimeError(f"Ollama did not answer within {config.REQUEST_TIMEOUT_S}s")
    latency_ms = (time.perf_counter() - start) * 1000

    if response.status_code != 200:
        print(f"[classifier] HTTP {response.status_code}: {response.text}")
        raise RuntimeError(f"Classifier returned HTTP {response.status_code}")

    data = response.json()
    print(f"[classifier] raw response: {json.dumps(data, indent=2)}")
    print(f"[classifier] latency: {latency_ms:.0f} ms")

    meta = {"latency_ms": latency_ms, "usage": data.get("usage", {})}
    return data["answers"], meta
