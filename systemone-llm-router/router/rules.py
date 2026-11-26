import config


def get_thresholds(overrides=None):
    return {**config.THRESHOLDS, **(overrides or {})}


def needs_web(answers, thresholds=None):
    t = get_thresholds(thresholds)
    fresh = answers["needs_fresh_info"]["noul"]
    result = fresh >= t["web_probability"]
    print(f"[rules] needs_fresh_info={fresh:.2f} (threshold {t['web_probability']}) -> needs_web={result}")
    return result


def choose_route(answers, thresholds=None):
    """Ordered rules, first match wins. Returns (route, reason)."""
    t = get_thresholds(thresholds)
    task = answers["task_type"]["choice"]
    confidence = answers["task_type"]["confidence"]
    complexity = answers["complexity"]["score"]
    print(f"[rules] task_type={task} confidence={confidence:.2f} complexity={complexity:.2f}")

    if confidence < t["min_confidence"]:
        print(f"[rules] 1. confidence {confidence:.2f} < {t['min_confidence']} -> general")
        return "general", f"low confidence ({confidence:.2f}) on task type, escalating"

    if task == "coding":
        print("[rules] 2. task is coding -> coding")
        return "coding", "task is coding"

    if task == "agentic" or complexity >= t["frontier_complexity"]:
        print("[rules] 3. agentic or very complex -> frontier")
        return "frontier", f"task is {task} with complexity {complexity:.2f}"

    if task == "reasoning" or complexity > t["general_complexity"]:
        print("[rules] 4. reasoning or heavy -> general")
        return "general", f"task is {task} with complexity {complexity:.2f}"

    if task == "general":
        print("[rules] 5. general task -> general")
        return "general", "everyday task"

    print("[rules] 6. nothing else matched -> small")
    return "small", "simple request"
