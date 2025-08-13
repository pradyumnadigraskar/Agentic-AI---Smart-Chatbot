# Rag/app/ui.py

import os
import sys
import streamlit as st


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from app.langgraph_nodes import decision_node, weather_worker, rag_worker
from app.processor import index_pdf
from app.config import PDFS_DIR


st.set_page_config(page_title="Agentic AI - Smart Chatbot")
st.title("🌤 Agentic AI - Smart Chatbot")


st.sidebar.header("📄 Uploaded PDF's")
pdf_file = st.sidebar.file_uploader("Upload PDF to index", type=["pdf"])

if pdf_file:
    os.makedirs(PDFS_DIR, exist_ok=True)
    saved_path = os.path.join(PDFS_DIR, pdf_file.name)
    with open(saved_path, "wb") as f:
        f.write(pdf_file.read())
    chunk_count = index_pdf(saved_path)
    st.sidebar.success(f"Indexed {chunk_count} chunks from {pdf_file.name}")


st.header("💬 Chat")
query = st.text_input('Ask something (e.g., "weather in Paris" or "What does the PDF say about X?")')

if st.button("Send") and query:
    # Decide what action to take
    decision = decision_node({"text": query})
    
    if decision.get("action") == "weather":
        output = weather_worker(decision)
    else:
        output = rag_worker(decision)

    
    if "error" in output:
        st.error(output["error"])
    else:
        st.subheader("Answer:")
        st.write(output["result"])

   
    from app.langsmith_eval import evaluate
    st.subheader("Evaluation")
    st.json(evaluate(query, output.get("result", "")))
