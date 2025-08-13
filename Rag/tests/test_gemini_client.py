import pytest
import os
from app.gemini_client import generate_text, embed_texts

def test_generate_without_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(RuntimeError):
        generate_text("hello")
