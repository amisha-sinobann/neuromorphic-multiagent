"""
Neuromorphic AI Multi-Agent Document Reviewer
Backend: FastAPI
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
from pathlib import Path
import uuid

from agents.orchestrator import MultiAgentOrchestrator
from services.document_processor import extract_text_from_file

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="Neuromorphic AI Multi-Agent Reviewer",
    description=(
        "Multi-agent system that sees, thinks, recalls, and checks research documents "
        "to reduce hallucination and factual mistakes in neuromorphic AI writing."
    ),
    version="1.0.0",
)

# Allow local frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = MultiAgentOrchestrator()


@app.get("/")
def root():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {
        "status": "ok",
        "service": "Neuromorphic AI Multi-Agent Reviewer",
        "agents": ["Viewer", "Thinker", "Recall", "Checker", "Synthesizer"],
        "message": "Open / for the UI, or POST to /api/review",
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/review")
async def review_document(file: UploadFile = File(...)):
    """
    Upload a research document (txt, pdf, docx).
    The multi-agent pipeline will:
      1. Viewer   see & extract claims
      2. Thinker   reason about risks
      3. Recall    ground with knowledge base
      4. Checker   detect hallucination / mistakes
      5. Synthesizer  produce final report
    """
    allowed = {".txt", ".pdf", ".docx", ".doc"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed)}",
        )

    # Save upload
    file_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{file_id}{suffix}"
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Extract text
    try:
        text = extract_text_from_file(str(save_path), file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")

    if not text or len(text.strip()) < 30:
        raise HTTPException(
            status_code=400,
            detail="Could not extract meaningful text from the document.",
        )

    # Run multi-agent pipeline
    try:
        result = orchestrator.process_document(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent pipeline error: {e}")

    return JSONResponse(content={
        "filename": file.filename,
        "document_id": result.get("document_id"),
        "result": result,
    })


@app.post("/api/review-text")
async def review_text(payload: dict):
    """Alternative endpoint: send plain text directly (no file)."""
    text = payload.get("text", "").strip()
    if len(text) < 20:
        raise HTTPException(status_code=400, detail="Text too short. Paste at least a couple of sentences.")
    result = orchestrator.process_document(text)
    return {"result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
