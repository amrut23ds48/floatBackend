# 🌊 Argo RAG Bot

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline using:
- **Microsoft Access DB** (2004 Argo Dataset)
- **LangChain + Chroma Cloud** (Vector database for retrieval)
- **HuggingFace Embeddings**
- **Perplexity API** (SONAR PRO) for LLM answers

---

## 🚀 Features
- Extract data from `.accdb` database (`extract_access.py`)
- Convert tables to JSON format for processing
- Chunk & upload documents to **Chroma Cloud** (`build_chroma.py`)
- Query documents using **RAG + Perplexity API** (`query_rag.py`)
- Supports resumable uploads with checkpoints

---

## 📂 Project Structure
argo_rag/
│── data/ # Source Access DB file
│ └── ARGO_DB_2004.accdb
│── output/ # Generated JSON + checkpoints
│── src/
│ ├── build_chroma.py # Upload docs to Chroma
│ ├── extract_access.py # Extract from Access DB
│ ├── query_rag.py # Query interface
│ └── utils.py # Common config/paths
│── .env # API keys + config (not committed)
│── requirements.txt
│── README.md
│── .gitignore


---

## ⚙️ Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/floatchat-backend.git
   cd floatchat-backend/argo_rag

2. Create virtual environment:

python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

3. Install dependencies:

pip install -r requirements.txt


4. Add your .env file:

CHROMA_API_KEY=your_chroma_api_key
CHROMA_TENANT=your_chroma_tenant
CHROMA_DATABASE=your_chroma_db
PERPLEXITY_API_KEY=your_perplexity_api_key
PERPLEXITY_MODEL=sonar-pro

5. 🛠 Usage

1. Extract Data
python src/extract_access.py

2. Build & Upload Chroma Index
python src/build_chroma.py

3. Query with RAG
python src/query_rag.py


6. Type your questions interactively:

Ask a question (or type 'exit'): What was the average salinity in the Indian Ocean in 2004?

10. 📝 Notes

Default chunk size: 300 tokens

Batch size: 50 (safe for Chroma Cloud free tier)

If uploads fail, adjust BATCH_SIZE or request quota increase.