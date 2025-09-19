import os
import time
import requests
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

# ---------------- Load Environment ---------------- #
load_dotenv()

CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")

COLLECTION_NAME = "argo_collection"


# ---------------- Perplexity API ---------------- #
def query_perplexity(prompt: str, retries: int = 3) -> str:
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            resp_json = resp.json()
            if "choices" in resp_json and resp_json["choices"]:
                return resp_json["choices"][0].get("message", {}).get("content", "")
            return "[ERROR] Unexpected response format"
        except Exception as e:
            print(f"[WARN] Perplexity query failed (attempt {attempt+1}): {e}")
            time.sleep(2)  # backoff before retry

    return "[ERROR] Failed after retries"


# ---------------- Chroma Cloud ---------------- #
def get_vectorstore() -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
    )

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        client=client,
    )


# ---------------- Initialize VectorStore Once ---------------- #
print("[INFO] Connecting to Chroma Cloud...")
vector_store = get_vectorstore()
print("[INFO] Connected to Chroma Cloud ✅")


# ---------------- RAG Query ---------------- #
def rag_query(user_query: str, top_k: int = 3) -> str:  # ⚡ reduced top_k for speed
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    docs = retriever.get_relevant_documents(user_query)

    if not docs:
        return "No relevant documents found."

    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"Context:\n{context}\n\nQuestion: {user_query}\nAnswer:"
    return query_perplexity(prompt)


# ---------------- Entry Point ---------------- #
if __name__ == "__main__":
    while True:
        q = input("\nAsk a question (or type 'exit'): ")
        if q.lower() in {"exit", "quit"}:
            break
        print("\nAnswer:\n", rag_query(q))
