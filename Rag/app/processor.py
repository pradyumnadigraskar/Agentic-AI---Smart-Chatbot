import os
import uuid
from app.pdf_utils import load_pdf_text, split_text_to_chunks
from app.gemini_client import embed_texts, generate_text
from app.qdrant_utils import get_qdrant_client as init_qdrant, upsert_documents, search_query as similarity_search

from app.config import PDFS_DIR

COLLECTION = "pdf_collection"

def index_pdf(path: str):
    text = load_pdf_text(path)
    chunks = split_text_to_chunks(text)
    client = init_qdrant()
    texts = chunks
    embeddings = embed_texts(texts)
    ids = [str(uuid.uuid4()) for _ in texts]
    metadatas = [{"source": os.path.basename(path), "chunk_index": i, "text": t[:2000]} for i, t in enumerate(texts)]
    upsert_documents(client, COLLECTION, embeddings, metadatas, ids)
    return len(texts)

def retrieve_and_answer(query: str, top_k: int = 4) -> str:
    q_emb = embed_texts([query])[0]
    client = init_qdrant()
    hits = similarity_search(client, COLLECTION, q_emb, top_k)
    # build context from payloads
    contexts = []
    for h in hits:
        payload = getattr(h, "payload", h.payload if hasattr(h, "payload") else (h._payload if hasattr(h, "_payload") else None))
        if isinstance(payload, dict):
            contexts.append(payload.get("text", str(payload)))
        else:
            contexts.append(str(payload))
    prompt = "You are a helpful assistant. Use the following document context to answer the question.\n\nContext:\n" + "\n\n".join(contexts) + "\n\nQuestion: " + query
    answer = generate_text(prompt)
    return answer
