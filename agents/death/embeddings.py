import json
import os
import asyncio
import nest_asyncio
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --------------------------
# Fix async event loop issues (Streamlit + gRPC)
# --------------------------
nest_asyncio.apply()
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

JSON_PATH = "knowledge_base/death_rules.json"
INDEX_PATH = Path(__file__).parent / "death_embeddings.index"

# --------------------------
# Load JSON and flatten
# --------------------------
with open(JSON_PATH, "r", encoding="utf-8") as f:
    death_data = json.load(f)

def flatten_json(d, prefix=""):
    """Recursively flatten JSON into text strings."""
    texts = []
    for k, v in d.items():
        if isinstance(v, dict):
            texts.extend(flatten_json(v, prefix=f"{prefix}{k}."))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                texts.append(f"{prefix}{k}[{i}]: {item}")
        else:
            texts.append(f"{prefix}{k}: {v}")
    return texts

chunks = flatten_json(death_data)

# --------------------------
# Split into chunks
# --------------------------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
texts = splitter.split_text("\n".join(chunks))

# --------------------------
# Lazy embedding creation
# --------------------------
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )

# --------------------------
# Build / Save FAISS Index
# --------------------------
if not INDEX_PATH.exists():
    vector_store = FAISS.from_texts(texts, get_embeddings())
    vector_store.save_local(str(INDEX_PATH))

# --------------------------
# Query function
# --------------------------
def query_embeddings(query: str, k: int = 3):
    """
    Retrieve the top-k relevant text chunks from the knowledge base.
    """
    store = FAISS.load_local(
        str(INDEX_PATH),
        get_embeddings(),
        allow_dangerous_deserialization=True
    )
    results = store.similarity_search(query, k=k)
    return [r.page_content for r in results]
