from pypdf import PdfReader
from typing import List

def load_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    pages = [(p.extract_text() or "") for p in reader.pages]
    return "\n\n".join(pages)

def split_text_to_chunks(text: str, chunk_words: int = 400, overlap_words: int = 80) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+chunk_words]
        chunks.append(" ".join(chunk))
        i += chunk_words - overlap_words
    return chunks
