# SystemOne-LLM-Router

A prompt-aware model router where a small **decision model** classifies each prompt and plain Python rules turn that classification into a routing decision. The router never writes a word and never calls the downstream LLMs. It only decides which one should answer.

Built with Tev1 0.8B served via Ollama's `/v1/systemone` endpoint, Streamlit, pandas and httpx. The decision model returns typed answers — a `choice`, a `score` and a `noul` probability — with confidence values. The routing policy lives in readable rules with explicit thresholds, so tuning the router means changing a number, not rewording a prompt.

---

## The Problem This Router Addresses

Not every prompt needs the same LLM. A greeting does not need a frontier model, and a request to build and deploy a whole application is too much for a 3B model.

Ask a simple question: **"What does HTTP stand for?"**

A fixed setup sends it to one model. Either that model is large and you overpay for every greeting, or it is small and the hard prompts suffer.

A decision model sits in front and makes the quick judgement first. It reads the prompt once and answers three typed questions about it. Plain code then picks a route:

| Prompt                                       | Task type   | Complexity | Route        |
| -------------------------------------------- | ----------- | ---------- | ------------ |
| What does HTTP stand for?                    | simple_chat | 0.07       | `small`    |
| Fix the off-by-one error in my binary search | coding      | 1.45       | `coding`   |
| Build a full-stack todo app with auth and CI | agentic     | 1.98       | `frontier` |

**The decision model states the facts. Your code sets the policy.** Typed answers mean there is no JSON to parse out of free text, and confidence values let the router fall back to a safer model when the classification is shaky.

---

## What the Decision Model Returns

Every call sends one `state` and three typed questions. The model answers all three in a single request:

- `task_type` — a **choice** question. Picks one of `simple_chat`, `general`, `coding`, `reasoning` or `agentic`, with a probability for every option and a confidence score.
- `complexity` — a **score** question on a 0 to 2 scale. Anchored by three descriptions, from "a one-line answer" to "several steps or a long detailed answer". Can land between anchors.
- `needs_fresh_info` — a **noul** (yes/no) question. Returns the probability that answering needs information from the last few weeks.

A request looks like this:

```json
{
  "model": "tev1:0.8b-bf16",
  "state": { "prompt": "Fix the off-by-one error in my binary search implementation." },
  "questions": {
    "task_type": {
      "type": "choice",
      "instructions": "What kind of help is the user asking for in `prompt`?",
      "criteria": {
        "simple_chat": "Greetings, small talk, a well-known fact, a definition, a short rewrite or translation",
        "coding": "Writing, fixing, explaining or reviewing code, shell commands, SQL or regex",
        "agentic": "A large goal that needs many steps, tools, files or actions to complete"
      }
    },
    "needs_fresh_info": {
      "type": "noul",
      "instructions": "Does answering `prompt` correctly require information from the last few weeks?"
    }
  }
}
```

---

## Routing Rules

The rules are checked in order and the first match wins. All thresholds are in `config.py`.

| Order | Condition                                           | Route        | Reason                                            |
| ----- | --------------------------------------------------- | ------------ | ------------------------------------------------- |
| 1     | `task_type` confidence < `min_confidence` (0.5) | `general`  | Shaky classification, escalate rather than gamble |
| 2     | `task_type` is `coding`                         | `coding`   | Code tasks go to the coding model                 |
| 3     | `task_type` is `agentic` or complexity ≥ 1.7   | `frontier` | Multi-step or very heavy work                     |
| 4     | `task_type` is `reasoning` or complexity > 1.0  | `general`  | Needs more than a small model                     |
| 5     | `task_type` is `general`                        | `general`  | Everyday task                                     |
| 6     | Anything else                                       | `small`    | Simple request                                    |

`needs_web` is set independently. It is `true` when the `needs_fresh_info` probability is at or above `web_probability` (0.7), and it is a flag in the output, not a route.

Each route maps to an intended model. These are labels only, nothing is called:

| Route        | Intended model         |
| ------------ | ---------------------- |
| `small`    | `granite4.1:3b`      |
| `general`  | `qwen2.5:14b`        |
| `coding`   | `ornith-1.5-35b-a3b` |
| `frontier` | `gemini-flash`       |

---

## Real Demo Output

**Prompt:** *"Build a full-stack todo app with a database, auth and deployment pipeline and set up the CI for it."*

```
[classifier] POST /v1/systemone model=tev1:0.8b-bf16
[rules] task_type=agentic confidence=0.98 complexity=1.98
[rules] 3. agentic or very complex -> frontier
[rules] needs_fresh_info=0.56 (threshold 0.7) -> needs_web=False
[pipeline] decision: route=frontier model=gemini-flash needs_web=False
```

### Baseline evaluation

A first run over 28 labeled prompts gave **23 of 28 correct (82%)**.

| Expected route | Correct | Notes                                                                    |
| -------------- | ------- | ------------------------------------------------------------------------ |
| `coding`     | 7 / 7   | Confidence mostly above 0.9                                              |
| `frontier`   | 5 / 5   | All five classified as `agentic` with confidence 0.72 or higher        |
| `small`      | 5 / 7   | Two borderline prompts ("thanks", a short rewrite) escalated             |
| `general`    | 6 / 9   | Three ordinary prompts scored complexity ≥ 1.7 and went to `frontier` |

Latency was about 3 s on the first call (cold model load), then roughly 160 to 430 ms per decision.

### What the misses show

|                     | Finding                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| `task_type`       | Reliable. Misses came from the rules, not from the model misreading the prompt                   |
| `complexity`      | Noisy. Ordinary prompts like "tips for a job interview" scored 1.88, which tripped the threshold |
| Low-confidence rule | Sent two short `small` prompts to `general`. Reasonable, but costs some accuracy             |
| `needs_web`       | Not yet tested. The baseline set has no prompt that needs fresh information                      |

These numbers come from a small set labeled by the author, so treat them as a baseline to tune against, not as a benchmark.

---

## Tech Stack

| Component      | Technology                                   |
| -------------- | -------------------------------------------- |
| Decision model | Tev1 0.8B (`tev1:0.8b-bf16`) via Ollama    |
| Endpoint       | `POST /v1/systemone` (typed decision API)  |
| HTTP client    | httpx                                        |
| Configuration  | python-dotenv                                |
| UI             | Streamlit                                    |
| Evaluation     | pandas (CSV results, accuracy and confusion) |
| Tests          | pytest (routing rules only)                  |

---

## Project Structure

```
systemone-llm-router/
├── router/
│   ├── __init__.py
│   ├── questions.py         ← the three typed questions sent to the decision model
│   ├── classifier.py        ← ask_classifier(): one HTTP call to /v1/systemone
│   ├── rules.py             ← choose_route() and needs_web(), ordered rules
│   └── pipeline.py          ← route(): prompt in, decision dict out
├── eval/
│   ├── __init__.py
│   ├── prompts.csv          ← labeled prompts with the expected route
│   └── run_eval.py          ← runs the set, writes results.csv, prints a summary
├── tests/
│   └── test_rules.py        ← routing rule tests, no model needed
├── config.py                ← base URL, model name, routes and thresholds
├── app.py                   ← Streamlit UI with threshold sliders
├── conftest.py              ← puts the project root on the pytest path
├── .env.example             ← OLLAMA_BASE_URL
└── requirements.txt
```

The code is plain functions with no classes. Every step prints a tagged line (`[classifier]`, `[rules]`, `[pipeline]`, `[eval]`) so you can follow a decision in the terminal.

---

## Installation

**1. Clone the repository**

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/awesome-agentic-ai.git
cd awesome-agentic-ai
git sparse-checkout set systemone-llm-router
git checkout
cd systemone-llm-router
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate
```


**3. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**4. Install Ollama and pull the decision model**

Download Ollama from [ollama.com](https://ollama.com). The decision endpoint needs Ollama 0.35 or later. Then:

```bash
ollama pull tev1:0.8b-bf16
ollama serve
```

---

## Configuration

The Ollama address is read from a `.env` file. Copy the example and edit it if your server is elsewhere:

```bash
cp .env.example .env
```

```
OLLAMA_BASE_URL=http://localhost:11434
```

Everything else is in `config.py`:

```python
CLASSIFIER_MODEL = "tev1:0.8b-bf16"
REQUEST_TIMEOUT_S = 30
MAX_PROMPT_CHARS = 4000

ROUTES = {
    "small": "granite4.1:3b",
    "general": "qwen2.5:14b",
    "coding": "ornith-1.5-35b-a3b",
    "frontier": "gemini-flash",
}

THRESHOLDS = {
    "min_confidence": 0.5,
    "frontier_complexity": 1.7,
    "general_complexity": 1.0,
    "web_probability": 0.7,
}
```

---

## Usage

**Step 1 — Run the rule tests (no model needed):**

```bash
pytest
```

**Step 2 — Route a single prompt from the command line:**

```bash
python -c "from router.pipeline import route; route('Write a python function to parse a CSV file')"
```

This prints the raw response from the decision model, each rule that was checked, and the final route.

**Step 3 — Run the Streamlit app:**

```bash
streamlit run app.py
```

Open `http://localhost:8501`. Type a prompt and press the button to see the route, the intended model, the `needs_web` flag, the task type probabilities and the raw answers. The sidebar sliders override the thresholds for the session, so you can move a threshold and watch a borderline prompt change route.

**Step 4 — Run the evaluation set:**

```bash
python -m eval.run_eval
```

Run this from the project root. It sends every prompt in `eval/prompts.csv` through the router, writes `eval/results.csv` (route, confidence, complexity, latency and the raw answers) and prints overall accuracy, accuracy per route, a confusion table and p50 and p95 latency. Add your own prompts to the CSV, quoting any prompt that contains a comma.

---

## Notes

- The router only decides. It never calls the downstream models, so no API keys other than the Ollama address are needed.
- The decision model has a context of about 2,000 tokens, so prompts are truncated at 4,000 characters before the request is sent.
- The `confidence` value is not the same as the top probability, and it is not the probability of being correct. Check it against your own data before relying on a threshold.
- The `complexity` score is the noisiest signal. The rules lean on `task_type` first and treat complexity as a secondary signal.
- Tev1 0.8B is the smallest model in its family. Ollama's published evaluation lists a mean accuracy of 63.5% for it, against 73.3% for the 4B model, so expect some misses on borderline prompts. Those figures come from the model publisher's own datasets.
- Rules are plain Python in `router/rules.py`, so changing the policy never means re-prompting the model. The 12 tests in `tests/test_rules.py` check rule order and threshold overrides without calling it.
- Question wording matters. Describe each choice option with concrete examples rather than a single word, and treat score criteria as anchor points on a ruler.

---

## Contributing

Contributions to this project are welcome. If you have ideas for improvements, bug fixes or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License. See the [MIT License](https://opensource.org/licenses/MIT) for details.
