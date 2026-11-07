import os
from datetime import datetime, timezone
import frontmatter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import config


def to_unix_ts(value):
    # PyYAML parses unquoted ISO datetimes into datetime objects, not strings
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return int(value.timestamp())
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return int(dt.timestamp())
        except Exception:
            return None
    return None


def load_policies(policies_dir):
    print(f"Loading policies from {policies_dir}...")
    docs = []
    for filename in os.listdir(policies_dir):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(policies_dir, filename)
        post = frontmatter.load(filepath)
        metadata = dict(post.metadata)
        metadata["source_file"] = filename

        if isinstance(metadata.get("generated"), dict):
            metadata["generated_by"] = metadata["generated"].get("by", "")
            metadata["generated_at"] = str(metadata["generated"].get("at", ""))
            del metadata["generated"]
        if isinstance(metadata.get("verified"), dict):
            metadata["verified_by"] = metadata["verified"].get("by", "")
            metadata["verified_at"] = str(metadata["verified"].get("at", ""))
            del metadata["verified"]

        # store stale_after as unix int so Chroma can filter with $gt
        if metadata.get("stale_after"):
            ts = to_unix_ts(metadata["stale_after"])
            if ts:
                metadata["stale_after_ts"] = ts
                print(f"  stale_after_ts for {filename}: {ts}")
            metadata["stale_after"] = str(metadata["stale_after"])

        if isinstance(metadata.get("sources"), list):
            metadata["sources"] = str(metadata["sources"])
        if isinstance(metadata.get("links"), list):
            metadata["links"] = ",".join(metadata["links"])
        if isinstance(metadata.get("tags"), list):
            metadata["tags"] = ",".join(metadata["tags"])

        # prepend title and tags to body for better embedding quality on short docs
        title = metadata.get("title", "")
        tags = metadata.get("tags", "")
        enriched_content = f"Title: {title}\nTags: {tags}\n\n{post.content}"

        doc = Document(page_content=enriched_content, metadata=metadata)
        docs.append(doc)
        print(f"  Loaded: {filename} | status: {metadata.get('status', 'unknown')}")
    print(f"Total policies loaded: {len(docs)}")
    return docs


def build_rag_index(docs):
    print("\nBuilding plain RAG index (no metadata filtering)...")
    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL, base_url=config.OLLAMA_BASE_URL)
    db = Chroma(
        collection_name=config.RAG_COLLECTION,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_PERSIST_PATH
    )
    db.add_documents(docs)
    print(f"RAG index built with {len(docs)} documents.")
    return db


def build_okf_index(docs):
    print("\nBuilding OKF-aware index (metadata preserved)...")
    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL, base_url=config.OLLAMA_BASE_URL)
    db = Chroma(
        collection_name=config.OKF_COLLECTION,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_PERSIST_PATH
    )
    db.add_documents(docs)
    print(f"OKF index built with {len(docs)} documents.")
    return db


if __name__ == "__main__":
    docs = load_policies(config.POLICIES_DIR)
    build_rag_index(docs)
    build_okf_index(docs)
    print("\nIngestion complete. Both indexes ready.")
