import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentence_transformers import SentenceTransformer
import chromadb
from app.config import VECTOR_COLLECTION
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

embedder = SentenceTransformer("all-MiniLM-L6-v2")
db = chromadb.Client()
collection = db.get_or_create_collection(VECTOR_COLLECTION)


def update_vector_store(collection_name, docs):
    db.delete_collection(collection_name)
    collection = db.get_or_create_collection(collection_name)
    embeddings = embedder.encode(docs)
    for i, text in enumerate(docs):
        collection.add(documents=[text], embeddings=[embeddings[i]], ids=[str(i)])


def query_vector_store(query, collection_name):
    collection = db.get_or_create_collection(collection_name)
    q_embed = embedder.encode([query])[0]
    results = collection.query(query_embeddings=[q_embed], n_results=3)
    return results["documents"][0]