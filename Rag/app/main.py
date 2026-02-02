# Rag/app/main.py
import os
import shutil
import json
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import PDFS_DIR
from app.processor import index_pdf, retrieve_and_answer_stream
from app.langgraph_nodes import decision_node, weather_worker
from app.langsmith_eval import evaluate

app = FastAPI()
os.makedirs(PDFS_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    query: str

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # ... (Keep existing upload logic) ...
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    file_path = os.path.join(PDFS_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        chunk_count = index_pdf(file_path)
        return {"filename": file.filename, "chunks_indexed": chunk_count, "status": "success"}
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

async def response_generator(query: str):
    """
    Generator that yields:
    1. The answer chunks (text)
    2. A special separator
    3. The evaluation JSON
    """
    # 1. Decide action
    decision = decision_node({"text": query})
    
    full_answer = ""
    
    # 2. Execute Logic
    if decision.get("action") == "weather":
        # Weather is fast, not streamed from LLM usually, but we simulate stream for consistency
        output = weather_worker(decision)
        answer_text = output.get("result", output.get("error", "Error"))
        full_answer = answer_text
        yield answer_text
    else:
        # RAG Streaming
        try:
            for chunk in retrieve_and_answer_stream(query):
                full_answer += chunk
                yield chunk
        except Exception as e:
            err = f"Error: {str(e)}"
            full_answer = err
            yield err

    # 3. Evaluate (After generation is complete)
    eval_result = evaluate(query, full_answer)
    
    # Send a delimiter followed by the evaluation data
    # We use a unique separator string that won't appear in normal text
    yield f"\n\n__EVAL_START__{json.dumps(eval_result)}__EVAL_END__"

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    return StreamingResponse(response_generator(request.query), media_type="text/plain")

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)