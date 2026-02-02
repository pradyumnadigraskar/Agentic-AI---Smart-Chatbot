# app/gemini_client.py
from typing import List, Generator
import google.generativeai as genai
from app.config import GEMINI_API_KEY

# Configure API key
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise RuntimeError("GEMINI_API_KEY not set in environment.")

def generate_text(prompt: str, model: str = "gemini-2.5-flash", max_output_tokens: int = 512) -> str:
    """Non-streaming generation (kept for compatibility/weather summaries)"""
    model_client = genai.GenerativeModel(model)
    response = model_client.generate_content(prompt, generation_config={"max_output_tokens": max_output_tokens})
    return getattr(response, "text", str(response))

def generate_text_stream(prompt: str, model: str = "gemini-2.5-flash") -> Generator[str, None, None]:
    """
    Generates text from Gemini in a streaming fashion.
    """
    model_client = genai.GenerativeModel(model)
    response = model_client.generate_content(prompt, stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text

def embed_texts(texts: List[str], model: str = "models/text-embedding-004") -> List[List[float]]:
    results = []
    for text in texts:
        embedding = genai.embed_content(model=model, content=text)
        results.append(embedding["embedding"])
    return results