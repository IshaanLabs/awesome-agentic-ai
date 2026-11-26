from router.rules import choose_route, needs_web


def make_answers(task="simple_chat", confidence=0.9, complexity=0.2, fresh=0.0):
    return {
        "task_type": {"choice": task, "confidence": confidence},
        "complexity": {"score": complexity},
        "needs_fresh_info": {"noul": fresh},
    }


def test_simple_chat_goes_small():
    assert choose_route(make_answers())[0] == "small"


def test_general_task_goes_general():
    assert choose_route(make_answers(task="general"))[0] == "general"


def test_coding_goes_coding():
    assert choose_route(make_answers(task="coding"))[0] == "coding"


def test_reasoning_goes_general():
    assert choose_route(make_answers(task="reasoning"))[0] == "general"


def test_agentic_goes_frontier():
    assert choose_route(make_answers(task="agentic"))[0] == "frontier"


def test_very_complex_goes_frontier():
    assert choose_route(make_answers(task="simple_chat", complexity=1.9))[0] == "frontier"


def test_heavy_simple_chat_goes_general():
    assert choose_route(make_answers(task="simple_chat", complexity=1.3))[0] == "general"


def test_low_confidence_beats_coding():
    assert choose_route(make_answers(task="coding", confidence=0.3))[0] == "general"


def test_low_confidence_beats_agentic():
    assert choose_route(make_answers(task="agentic", confidence=0.3))[0] == "general"


def test_threshold_override_changes_route():
    answers = make_answers(task="simple_chat", complexity=1.3)
    assert choose_route(answers, {"general_complexity": 1.5})[0] == "small"


def test_needs_web_above_threshold():
    assert needs_web(make_answers(fresh=0.8)) is True


def test_needs_web_below_threshold():
    assert needs_web(make_answers(fresh=0.2)) is False
