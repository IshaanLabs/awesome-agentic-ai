from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
import config


def get_rag_answer(question):
    print(f"\n[Plain RAG] Question: {question}")

    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL, base_url=config.OLLAMA_BASE_URL)
    db = Chroma(
        collection_name=config.RAG_COLLECTION,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_PERSIST_PATH
    )

    print("[Plain RAG] Retrieving top 3 documents...")
    results = db.similarity_search(question, k=3)

    for i, doc in enumerate(results):
        print(f"  Doc {i+1}: {doc.metadata.get('source_file')} | status: {doc.metadata.get('status', 'unknown')}")

    context = "\n\n---\n\n".join([doc.page_content for doc in results])

    prompt = f"""You are an HR assistant. Answer the question using only the context below.
Do not mention which document you used.

Context:
{context}

Question: {question}
Answer:"""

    llm = ChatOllama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE_URL)
    print("[Plain RAG] Generating answer...")
    response = llm.invoke([HumanMessage(content=prompt)])

    sources = [doc.metadata.get("source_file", "unknown") for doc in results]
    print(f"[Plain RAG] Sources used: {sources}")

    return response.content, sources
