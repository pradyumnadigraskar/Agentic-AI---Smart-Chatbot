
import os
import uuid
import json
from app.pdf_utils import load_pdf_text, split_text_to_chunks
from app.gemini_client import embed_texts, generate_text_stream # Import stream
from app.qdrant_utils import get_qdrant_client as init_qdrant, upsert_documents, search_query as similarity_search, recreate_collection
from app.config import PDFS_DIR

COLLECTION = "pdf_collection"

def index_pdf(path: str):
    # ... (Keep existing index_pdf logic exactly as before) ...
    text = load_pdf_text(path)
    chunks = split_text_to_chunks(text)
    if not chunks: return 0
    client = init_qdrant()
    embeddings = embed_texts(chunks)
    vector_size = len(embeddings[0])
    recreate_collection(client, COLLECTION, vector_size)
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": os.path.basename(path), "chunk_index": i, "text": t[:2000]} for i, t in enumerate(chunks)]
    upsert_documents(client, COLLECTION, embeddings, metadatas, ids)
    return len(chunks)

def retrieve_and_answer_stream(query: str, top_k: int = 4):
    """
    Generator that yields chunks of the answer.
    """
    q_emb = embed_texts([query])[0]
    client = init_qdrant()
    hits = similarity_search(client, COLLECTION, q_emb, top_k)
    
    contexts = []
    for h in hits:
        payload = getattr(h, "payload", h.payload if hasattr(h, "payload") else (h._payload if hasattr(h, "_payload") else None))
        contexts.append(payload.get("text", str(payload)) if isinstance(payload, dict) else str(payload))
            
    if not contexts:
        yield "I couldn't find any relevant information in the uploaded PDF."
        return

    # Updated Prompt for Points
    prompt = (
        "You are a helpful assistant. Use the following document context to answer the question.\n"
        "Guidelines:\n"
        "1. Structure your answer using clear bullet points where appropriate.\n"
        "2. Keep the answer concise and easy to read.\n\n"
        "Context:\n" + "\n\n".join(contexts) + "\n\n"
        "Question: " + query
    )
    
    # Stream the response
    for chunk in generate_text_stream(prompt):
        yield chunk