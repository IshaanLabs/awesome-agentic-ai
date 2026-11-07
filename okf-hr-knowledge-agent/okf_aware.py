import os
from datetime import datetime, timezone
import frontmatter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
import config


def follow_links(source_file, visited, depth=0, max_depth=1):
    if depth >= max_depth:
        return []

    filepath = os.path.join(config.POLICIES_DIR, source_file)
    if not os.path.exists(filepath) or source_file in visited:
        return []

    post = frontmatter.load(filepath)
    links = post.metadata.get("links", [])
    if isinstance(links, str):
        links = [l.strip() for l in links.split(",") if l.strip()]

    linked_docs = []
    for link in links:
        linked_filename = os.path.basename(link)
        linked_path = os.path.join(config.POLICIES_DIR, linked_filename)

        if not os.path.exists(linked_path) or linked_filename in visited:
            continue

        linked_post = frontmatter.load(linked_path)
        linked_meta = linked_post.metadata

        # only pull in stable linked docs — a link must not resurrect a superseded policy
        if linked_meta.get("status") != "stable":
            print(f"  [OKF] Skipping link {linked_filename}: status={linked_meta.get('status')}")
            continue

        print(f"  [OKF] Following link (depth={depth}): {source_file} -> {linked_filename}")
        linked_docs.append({
            "content": linked_post.content,
            "metadata": linked_meta,
            "source_file": linked_filename
        })
        visited.add(linked_filename)

    return linked_docs


def get_okf_answer(question):
    print(f"\n[OKF-Aware] Question: {question}")

    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL, base_url=config.OLLAMA_BASE_URL)
    db = Chroma(
        collection_name=config.OKF_COLLECTION,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_PERSIST_PATH
    )

    # compute now_ts inside the function so a long-running app never uses a stale value
    now_ts = int(datetime.now(timezone.utc).timestamp())
    print(f"[OKF-Aware] Filtering: status=stable AND stale_after_ts > {now_ts}...")

    results = db.similarity_search(
        question,
        k=3,
        filter={
            "$and": [
                {"status": {"$eq": "stable"}},
                {"stale_after_ts": {"$gt": now_ts}}
            ]
        }
    )

    # surface a warning if all stable policies are expired rather than silently returning nothing
    if not results:
        print("[OKF-Aware] No results after filter. Checking if stable policies exist but are stale...")
        fallback = db.similarity_search(question, k=3, filter={"status": {"$eq": "stable"}})
        if fallback:
            warning = "Warning: The only matching policies are past their review date and may be outdated. Please verify with HR."
            sources = [doc.metadata.get("source_file", "unknown") for doc in fallback]
            signals = [{
                "source_file": doc.metadata.get("source_file"),
                "status": doc.metadata.get("status"),
                "verified_by": doc.metadata.get("verified_by", "N/A"),
                "verified_at": doc.metadata.get("verified_at", "N/A"),
                "stale_after": doc.metadata.get("stale_after", "N/A"),
                "version": doc.metadata.get("version", "N/A"),
            } for doc in fallback]
            return warning, sources, signals
        return "No current HR policy found for this question.", [], []

    for i, doc in enumerate(results):
        print(f"  Doc {i+1}: {doc.metadata.get('source_file')} | status: {doc.metadata.get('status')} | verified_by: {doc.metadata.get('verified_by', 'N/A')}")

    # seed visited with primary results so graph traversal never re-adds them
    visited = set(doc.metadata.get("source_file", "") for doc in results)

    linked_contents = []
    for doc in results:
        source_file = doc.metadata.get("source_file", "")
        linked = follow_links(source_file, visited, depth=0, max_depth=1)
        linked_contents.extend(linked)

    primary_context = "\n\n---\n\n".join([doc.page_content for doc in results])

    if linked_contents:
        print(f"  [OKF] {len(linked_contents)} linked concept(s) pulled in via graph traversal")
        linked_context = "\n\n---\n\n".join([lc["content"] for lc in linked_contents])
        full_context = primary_context + "\n\n--- [Linked Concepts] ---\n\n" + linked_context
    else:
        full_context = primary_context

    okf_signals = []
    for doc in results:
        okf_signals.append({
            "source_file": doc.metadata.get("source_file"),
            "status": doc.metadata.get("status"),
            "verified_by": doc.metadata.get("verified_by", "N/A"),
            "verified_at": doc.metadata.get("verified_at", "N/A"),
            "stale_after": doc.metadata.get("stale_after", "N/A"),
            "version": doc.metadata.get("version", "N/A"),
        })

    prompt = f"""You are an HR assistant. Answer the question using only the verified, stable policies below.
Be precise and cite the policy version when relevant.

Context:
{full_context}

Question: {question}
Answer:"""

    llm = ChatOllama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE_URL)
    print("[OKF-Aware] Generating answer from stable, non-stale policies only...")
    response = llm.invoke([HumanMessage(content=prompt)])

    sources = [doc.metadata.get("source_file", "unknown") for doc in results]
    print(f"[OKF-Aware] Sources used: {sources}")

    return response.content, sources, okf_signals
