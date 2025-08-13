# app/gemini_client.py
from typing import List
import google.generativeai as genai
from app.config import GEMINI_API_KEY

# Configure API key
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise RuntimeError("GEMINI_API_KEY not set in environment.")

def generate_text(prompt: str, model: str = "gemini-1.5-flash", max_output_tokens: int = 512) -> str:
    """
    Generates text from Gemini.
    """
    model_client = genai.GenerativeModel(model)
    response = model_client.generate_content(prompt, generation_config={"max_output_tokens": max_output_tokens})
    return getattr(response, "text", str(response))

def embed_texts(texts: List[str], model: str = "models/text-embedding-004") -> List[List[float]]:
    """
    Generates embeddings for given texts using Gemini embeddings model.
    """
    results = []
    for text in texts:
        embedding = genai.embed_content(model=model, content=text)
        results.append(embedding["embedding"])
    return results
