import os
import json
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

# Load .env
load_dotenv()

# ---------------- Constants ---------------- #
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")

COLLECTION_NAME = "argo_collection"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
# Set a safe batch size to stay below Chroma Cloud quota
BATCH_SIZE = 50
CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "chroma_upload_checkpoint.txt")
JSON_FILE = os.path.join(OUTPUT_DIR, "argo_data.json")

# ---------------- Checkpoint Helpers ---------------- #
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def save_checkpoint(idx):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(idx))

# ---------------- Data Helpers ---------------- #
def load_documents(json_path: str):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"[ERROR] JSON file not found: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [
        Document(page_content=f"Table: {item['table']}\nRow: {item['row']}",
                 metadata={"table": item["table"]})
        for item in raw
    ]

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(docs)

# ---------------- Chroma Helpers ---------------- #
def init_chroma_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE
    )
    return Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings, client=client)

# ---------------- Upload ---------------- #
def upload_to_chroma():
    docs = load_documents(JSON_FILE)
    print(f"[INFO] Loaded {len(docs)} documents")

    chunks = split_documents(docs)
    print(f"[INFO] Split into {len(chunks)} chunks")

    vector_store = init_chroma_vectorstore()
    start_idx = load_checkpoint()
    print(f"[INFO] Resuming from batch index: {start_idx}")

    for i in range(start_idx, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        try:
            vector_store.add_documents(batch)
            print(f"[INFO] Uploaded batch {i // BATCH_SIZE + 1} ({len(batch)} chunks)")
            save_checkpoint(i + BATCH_SIZE)
        except chromadb.errors.ChromaError as e:
            print(f"[ERROR] Failed to upload batch {i // BATCH_SIZE + 1}: {e}")
            print("[INFO] Try reducing BATCH_SIZE or request a quota increase")
            break

    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)

    print(f"[SUCCESS] Uploaded {len(chunks)} chunks to Chroma Cloud")

# ---------------- Entry Point ---------------- #
if __name__ == "__main__":
    upload_to_chroma()
