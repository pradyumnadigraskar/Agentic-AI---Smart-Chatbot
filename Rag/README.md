# Gemini + OpenWeatherMap + Qdrant RAG Demo

This scaffold demonstrates:
- LangGraph agentic pipeline (decision node -> weather or PDF RAG)
- Gemini (google-generativeai) as the LLM & embeddings provider
- OpenWeatherMap for live weather
- Qdrant for vector storage
- LangChain used for some helper primitives / chains
- Streamlit UI for chat
- Simple LangSmith evaluation placeholder

Setup:
1. python -m venv .venv
2. Activate venv and install: pip install -r requirements.txt
3. Copy .env.example -> .env and fill keys: GEMINI_API_KEY, OPENWEATHER_API_KEY, QDRANT_URL, LANGSMITH_API_KEY (optional)
4. streamlit run app/ui.py
