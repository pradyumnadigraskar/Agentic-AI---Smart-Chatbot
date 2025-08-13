# app/qdrant_utils.py

import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

def get_qdrant_client():
    """
    Initialize and return a Qdrant client using environment variables.
    """
    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY", None)  # Optional if running locally
    )
    return client


def ensure_collection(client, collection_name, vector_size):
    """
    Ensures the Qdrant collection exists and matches the given vector size.
    If a mismatch is found, deletes and recreates the collection.
    """
    collections = [c.name for c in client.get_collections().collections]

    if collection_name not in collections:
        print(f"[Qdrant] Creating collection '{collection_name}' with vector size {vector_size}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
    else:
        info = client.get_collection(collection_name)
        existing_size = info.config.params.vectors.size
        if existing_size != vector_size:
            print(f"[Qdrant] Vector size mismatch: existing={existing_size}, required={vector_size}. Recreating collection...")
            client.delete_collection(collection_name)
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )


def upsert_documents(client, collection_name, vectors, metadatas, ids):
    """
    Inserts or updates documents in the Qdrant collection.
    Automatically ensures collection is created with correct vector size.
    """
    if not vectors:
        print("[Qdrant] No vectors to upsert.")
        return

    # Ensure collection exists and matches embedding size
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
    print(f"[Qdrant] Upserted {len(points)} points into collection '{collection_name}'.")


def search_query(client, collection_name, query_vector, top_k=5):
    """
    Searches Qdrant collection for top_k closest matches to the query_vector.
    """
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k
    )
