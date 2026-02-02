# Rag/app/qdrant_utils.py

import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

def get_qdrant_client():
    """
    Initialize and return a Qdrant client using environment variables.
    """
    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY", None)
    )
    return client

def recreate_collection(client, collection_name, vector_size):
    """
    Forces recreation of a collection, effectively clearing all old data.
    """
    # Try to delete if it exists
    try:
        client.delete_collection(collection_name)
        print(f"[Qdrant] Deleted old collection '{collection_name}'")
    except Exception:
        pass  # Collection might not exist yet, which is fine

    # Create fresh
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    print(f"[Qdrant] Created fresh collection '{collection_name}'")

def ensure_collection(client, collection_name, vector_size):
    """
    Ensures the Qdrant collection exists.
    """
    collections = [c.name for c in client.get_collections().collections]

    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

def upsert_documents(client, collection_name, vectors, metadatas, ids):
    """
    Inserts documents into the Qdrant collection.
    """
    if not vectors:
        return

    # Note: We rely on the caller (processor.py) to handle clearing/recreating 
    # the collection if a fresh start is needed.
    ensure_collection(client, collection_name, len(vectors[0]))

    points = [
        {
            "id": ids[i],
            "vector": vectors[i],
            "payload": metadatas[i]
        }
        for i in range(len(vectors))
    ]

    client.upsert(collection_name=collection_name, points=points)
    print(f"[Qdrant] Upserted {len(points)} points.")

def search_query(client, collection_name, query_vector, top_k=5):
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k
    )