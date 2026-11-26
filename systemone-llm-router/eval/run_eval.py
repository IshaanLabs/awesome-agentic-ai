import json
import os

import pandas as pd

from router.pipeline import route

PROMPTS_PATH = "eval/prompts.csv"
RESULTS_PATH = "eval/results.csv"


def run_eval():
    prompts = pd.read_csv(PROMPTS_PATH)
    print(f"[eval] loaded {len(prompts)} prompts from {PROMPTS_PATH}")

    rows = []
    for index, row in prompts.iterrows():
        print(f"\n[eval] {index + 1}/{len(prompts)}")
        try:
            decision = route(row["prompt"])
        except RuntimeError as error:
            print(f"[eval] failed: {error}")
            continue
        rows.append({
            "prompt": row["prompt"],
            "expected_route": row["expected_route"],
            "route": decision["route"],
            "correct": decision["route"] == row["expected_route"],
            "reason": decision["reason"],
            "needs_web": decision["needs_web"],
            "task_type": decision["answers"]["task_type"]["choice"],
            "confidence": decision["answers"]["task_type"]["confidence"],
            "complexity": decision["answers"]["complexity"]["score"],
            "fresh_info": decision["answers"]["needs_fresh_info"]["noul"],
            "latency_ms": decision["latency_ms"],
            "answers_json": json.dumps(decision["answers"]),
        })

    results = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    results.to_csv(RESULTS_PATH, index=False)
    print(f"\n[eval] wrote {len(results)} rows to {RESULTS_PATH}")
    return results


def summarize(results):
    print(f"\n[eval] overall accuracy: {results['correct'].mean():.1%}")
    print("\n[eval] accuracy per expected route:")
    print(results.groupby("expected_route")["correct"].mean().map("{:.1%}".format))
    print("\n[eval] confusion table (rows = expected, columns = predicted):")
    print(pd.crosstab(results["expected_route"], results["route"]))
    print(f"\n[eval] latency ms: p50={results['latency_ms'].median():.0f} "
          f"p95={results['latency_ms'].quantile(0.95):.0f}")


if __name__ == "__main__":
    summarize(run_eval())
