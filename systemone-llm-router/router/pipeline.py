import config
from router.classifier import ask_classifier
from router.rules import choose_route, needs_web


def route(prompt, thresholds=None):
    """Prompt in, routing decision (a plain dict) out. No LLM is called."""
    print(f"\n[pipeline] prompt: {prompt[:80]!r}")

    answers, meta = ask_classifier(prompt)
    route_name, reason = choose_route(answers, thresholds)
    web = needs_web(answers, thresholds)

    decision = {
        "prompt": prompt,
        "route": route_name,
        "model": config.ROUTES[route_name],
        "reason": reason,
        "needs_web": web,
        "answers": answers,
        "latency_ms": meta["latency_ms"],
        "usage": meta["usage"],
    }
    print(f"[pipeline] decision: route={route_name} model={decision['model']} needs_web={web}")
    return decision
