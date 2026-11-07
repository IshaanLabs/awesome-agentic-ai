# OKF HR Knowledge Agent

A side-by-side demo showing the difference between **Plain RAG** and **OKF-Aware RAG** when answering HR policy questions.

Built with Google's [Open Knowledge Format (OKF v0.2)](https://github.com/google/open-knowledge-format), LangChain, ChromaDB, Nomic Embed and Qwen2.5 via Ollama. Every HR policy is a Markdown file with YAML frontmatter carrying structured signals — `status`, `verified`, `stale_after`, `version`, `links` — that the OKF-aware pipeline uses to filter, rank and traverse knowledge before generating an answer.

---

## The Problem This Demo Illustrates

Ask a simple question: **"How many annual leave days do employees get?"**

Vector search works perfectly. It retrieves three highly relevant documents:

| Document           | Answer                    | Status           |
| ------------------ | ------------------------- | ---------------- |
| leave_policy_v1.md | 15 days                   | superseded       |
| leave_policy_v2.md | 18 days                   | superseded       |
| leave_policy_v3.md | 20 days + 5 carry-forward | **stable** |

A plain RAG pipeline with no metadata filtering will retrieve all three and may blend them into a conflicting answer. Any pipeline that stores a `status` field and filters on it would solve this specific problem.

**What OKF adds is not the filter itself — it is the shared portable format, the linting contract and the link graph.** OKF defines a standard way to express status, provenance, freshness and relationships so that any tool, agent or pipeline can inspect and act on those signals consistently, without each team inventing their own schema.

---

## What OKF Adds

Plain RAG treats every chunk as equal. OKF frontmatter gives each policy machine-readable signals:

- `status` — is this policy active, superseded or draft?
- `verified` — who signed off and when?
- `stale_after` — when should this stop being trusted? Stored as a Unix timestamp at ingest so Chroma can filter with `$gt`.
- `version` — which iteration is this?
- `links` — which other policies does this connect to? Enables graph traversal at retrieval time.
- `description` — one-line summary for linting and discovery.

A policy concept looks like this:

```yaml
---
type: Policy
title: Leave Policy v3
description: Current authoritative leave policy granting 20 days annual leave with 5-day carry-forward.
status: stable
version: "3.0"
generated: { by: process:hr-sync, at: 2026-01-01T09:00:00Z }
verified: { by: human:hr-director, at: 2026-01-01T11:30:00Z }
stale_after: 2027-01-01T00:00:00Z
sources:
  - id: hr-policy-v3
    resource: https://docs.example.com/hr-policy-v3
    title: HR Policy Document v3
tags: [leave, annual-leave, hr]
links:
  - ./expense_policy.md
  - ./remote_work_policy.md
---

## Leave Policy

Employees are entitled to 20 days of annual leave per calendar year.
...
```

---

## Side-by-Side Comparison

|                     | Plain RAG                   | OKF-Aware RAG                                                                |
| ------------------- | --------------------------- | ---------------------------------------------------------------------------- |
| Retrieval           | Top-k similarity, all docs  | Metadata filter (`status: stable` + `stale_after_ts > now`) + similarity |
| Conflict resolution | None                        | Superseded and stale policies excluded automatically                         |
| Provenance          | Not shown                   | Verified by, verified at, stale after shown per source                       |
| Graph traversal     | No                          | Follows markdown `links` to pull related stable concepts                   |
| Stale enforcement   | None                        | `stale_after` stored as Unix int, filtered at query time                   |
| Answer quality      | May be wrong or conflicting | Authoritative, versioned, cited                                              |

---

## Real Demo Output

**Query:** *"I'm going on leave and need to claim travel expenses, what are the rules?"*

### Plain RAG answer

> For travel expenses during your leave, you need to follow the rules outlined in the Expense Reimbursement Policy. Here are the key points:
>
> - Flights: Economy class for domestic flights, business class for international flights over 8 hours.
> - Hotels: Up to $200/night domestic, $300/night international.
> - Meals: Up to $50 per day.
>   For more details, you can refer to the Remote Work Policy and the Leave Policy.

**Sources retrieved:** `leave_policy_v3.md`, `expense_policy.md`, `leave_policy_v1.md`

⚠️ Notice `leave_policy_v1.md` (superseded, stale since 2024) was pulled in by vector similarity. The answer happens to be correct by luck, but the source set is untrustworthy.

---

### OKF-Aware RAG answer

> When you are on leave and need to claim travel expenses, the rules are as follows:
>
> **Expense Policy (v1.5, verified by finance-director):**
> All business expenses must be submitted within 30 days of incurrence.
>
> **Leave Policy v3:**
> You are entitled to 20 days of annual leave. For travel during leave:
>
> - Flights: Economy class domestic, business class international over 8 hours.
> - Hotels: Up to $200/night domestic, $300/night international.
> - Meals: Up to $50/day.
>
> **Approval:** Under $500 requires manager approval. Over $500 requires director approval.

**Sources retrieved:** `leave_policy_v3.md`, `expense_policy.md`, `remote_work_policy.md`

**OKF Signals used:**

- `leave_policy_v3.md` — status: stable | version: 3.0 | verified by: human:hr-director
- `expense_policy.md` — status: stable | version: 1.5 | verified by: human:finance-director
- `remote_work_policy.md` — status: stable | version: 2.0 | verified by: human:hr-director

### What happened differently

|                           | Plain RAG                 | OKF-Aware RAG                                                   |
| ------------------------- | ------------------------- | --------------------------------------------------------------- |
| `leave_policy_v1.md`    | ✅ retrieved (superseded) | ❌ blocked by status + stale filter                             |
| `remote_work_policy.md` | ❌ not retrieved          | ✅ pulled via graph traversal from `leave_policy_v3.md` links |

`remote_work_policy.md` was never retrieved by vector similarity. It was walked in because `leave_policy_v3.md` has it in its `links` frontmatter field. The `follow_links()` function checked its `status: stable` before pulling it in, and the shared `visited` set prevented any duplicate additions.

---

## Tech Stack

| Component        | Technology                                                     |
| ---------------- | -------------------------------------------------------------- |
| LLM              | Qwen2.5 via Ollama                                             |
| Embeddings       | nomic-embed-text via Ollama                                    |
| Vector Store     | ChromaDB                                                       |
| Framework        | LangChain (langchain-ollama, langchain-chroma, langchain-core) |
| UI               | Streamlit                                                      |
| Knowledge Format | OKF v0.2 (Markdown + YAML frontmatter)                         |
| Metadata parsing | python-frontmatter                                             |

---

## Project Structure

```
okf-hr-knowledge-agent/
├── policies/
│   ├── leave_policy_v1.md       ← status: superseded (15 days, stale 2024)
│   ├── leave_policy_v2.md       ← status: superseded (18 days, stale 2025)
│   ├── leave_policy_v3.md       ← status: stable, authoritative, links to expense + remote
│   ├── remote_work_policy.md    ← status: stable, links to leave + expense
│   ├── expense_policy.md        ← status: stable, links to remote + leave
│   ├── code_of_conduct.md       ← status: stable, links to performance review
│   └── performance_review.md    ← status: stable, links to leave + conduct
├── config.py                    ← all model URLs, paths and collection names
├── ingest.py                    ← loads policies, parses frontmatter, builds both indexes
├── rag.py                       ← plain RAG pipeline (no metadata filtering)
├── okf_aware.py                 ← OKF-aware pipeline (filter + graph traversal)
├── streamlit_app.py             ← side-by-side Streamlit UI
└── requirements.txt
```

---

## Installation

**1. Clone the repository**

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/awesome-agentic-ai.git
cd awesome-agentic-ai
git sparse-checkout set okf-hr-knowledge-agent
git checkout
cd okf-hr-knowledge-agent
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Install Ollama and pull the model**

Download Ollama from [ollama.com](https://ollama.com), then:

```bash
ollama pull qwen2.5
ollama pull nomic-embed-text
ollama serve
```

---

## Configuration

All configurable values are in `config.py`:

```python
OLLAMA_BASE_URL = "http://localhost:11434"  
LLM_MODEL = "qwen2.5"
EMBEDDING_MODEL = "nomic-embed-text"
CHROMA_PERSIST_PATH = "./chroma_db"
RAG_COLLECTION = "hr_rag"
OKF_COLLECTION = "hr_okf"
POLICIES_DIR = "./policies"
```

---

## Usage

**Step 1 — Ingest policies into both vector indexes:**

```bash
python ingest.py
```

This loads all `.md` files from `policies/`, parses YAML frontmatter, flattens nested fields for Chroma compatibility, converts `stale_after` to a Unix timestamp integer (`stale_after_ts`), prepends `Title` and `Tags` to the embedded text for better retrieval quality, and writes to two separate Chroma collections — `hr_rag` and `hr_okf`.

**Step 2 — Run the Streamlit app:**

```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501`. Type a question or click a sample query. Both pipelines run in parallel and display their answers, sources and OKF signals side by side.

**To demo the stale enforcement:**

Edit `stale_after` in `leave_policy_v3.md` to a past date, re-run `ingest.py`, then ask "How many leave days do I get?" — the OKF-aware pipeline will return a warning instead of an answer. Plain RAG will answer normally.

---

## Notes

- Both Chroma collections receive the same documents at ingest. The difference is entirely at retrieval time — plain RAG uses top-k similarity only, OKF-aware adds a `$and` metadata filter.
- `stale_after` in the YAML is parsed by PyYAML as a `datetime` object, not a string. The ingest pipeline handles both `datetime` objects and ISO strings, normalises naive datetimes to UTC, and stores the result as an integer Unix timestamp.
- `follow_links()` uses a shared `visited` set seeded with primary retrieval results, a `max_depth=1` limit and a `status: stable` check on every linked file. This prevents loops, duplicates and superseded policies being pulled in via links.
- If all stable policies for a question are past their `stale_after` date, the OKF-aware pipeline surfaces a warning rather than returning nothing silently.
- Embedding quality is improved by prepending `Title:` and `Tags:` to each document's body text before embedding. This matters especially for short policy documents.

---

## Contributing

Contributions to this project are welcome. If you have ideas for improvements, bug fixes or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License. See the [MIT License](https://opensource.org/licenses/MIT) for details.
