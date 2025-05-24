import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from app.config import VECTOR_COLLECTION

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Define where to persist the vector store
PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma")
os.makedirs(PERSIST_DIR, exist_ok=True)

embedder = SentenceTransformer("all-MiniLM-L6-v2")
db = PersistentClient(path=PERSIST_DIR)

def update_vector_store(collection_name, docs):
    if collection_name in [c.name for c in db.list_collections()]:
        db.delete_collection(collection_name)
    collection = db.get_or_create_collection(collection_name)
    embeddings = embedder.encode(docs)
    for i, text in enumerate(docs):
        collection.add(documents=[text], embeddings=[embeddings[i]], ids=[str(i)])

def query_vector_store(query, collection_name):
    collection = db.get_or_create_collection(collection_name)
    q_embed = embedder.encode([query])[0]
    results = collection.query(query_embeddings=[q_embed], n_results=10)
    docs = results.get("documents", [])
    return docs[0] if docs and docs[0] else []
