import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from summarizer import CentralSummarizer
from llm_manager import AIChainManager

load_dotenv()

MODEL_NAME = os.getenv("SELECTED_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
NOTES_DIR = os.getenv("NOTES_DIR", "./notes")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./data/chroma")
INDEX_PATH = os.getenv("INDEX_PATH", "./data/central_index.json")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = FastAPI(title="AI Interactive Notes Server")

components = {
    "doc_processor": None,
    "vector_store": None,
    "summarizer": None,
    "chain_manager": None,
    "error": None,
}


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class IndexResponse(BaseModel):
    indexed: int
    message: str


class StatusResponse(BaseModel):
    ready: bool
    model_name: str
    error: str | None = None


def init_components():
    doc_processor = DocumentProcessor(NOTES_DIR)
    vector_store = VectorStoreManager(CHROMA_DIR)
    summarizer = CentralSummarizer(INDEX_PATH, MODEL_NAME, OLLAMA_BASE_URL)
    chain_manager = AIChainManager(MODEL_NAME, vector_store, summarizer, OLLAMA_BASE_URL)
    return doc_processor, vector_store, summarizer, chain_manager


@app.on_event("startup")
def startup_event():
    try:
        (
            components["doc_processor"],
            components["vector_store"],
            components["summarizer"],
            components["chain_manager"],
        ) = init_components()
    except Exception as exc:
        components["error"] = str(exc)


if os.path.isdir(STATIC_DIR):
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/status", response_model=StatusResponse)
def get_status():
    return {
        "ready": components["error"] is None,
        "model_name": MODEL_NAME,
        "error": components["error"],
    }


def require_components():
    if components["error"]:
        raise HTTPException(status_code=503, detail=components["error"])
    return (
        components["doc_processor"],
        components["vector_store"],
        components["summarizer"],
        components["chain_manager"],
    )


@app.post("/api/index", response_model=IndexResponse)
def index_notes():
    doc_processor, vector_store, summarizer, _ = require_components()
    docs = doc_processor.load_documents()
    if not docs:
        return {"indexed": 0, "message": "No notes found to index."}
    split_docs = doc_processor.split_documents(docs)
    vector_store.add_documents(split_docs)
    summarizer.summarize_new_files(docs)
    return {"indexed": len(docs), "message": f"Indexed {len(docs)} files successfully!"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    _, _, _, chain_manager = require_components()
    response = chain_manager.ask(request.message)
    return {"response": response}


@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="UI not built.")


@app.get("/{path_name:path}")
def serve_spa(path_name: str):
    if path_name.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="UI not built.")
