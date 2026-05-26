import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Request #type: ignore
from fastapi.middleware.cors import CORSMiddleware #type: ignore
from pydantic import BaseModel #type: ignore
from slowapi import Limiter, _rate_limit_exceeded_handler #type: ignore
from slowapi.util import get_remote_address #type: ignore
from slowapi.errors import RateLimitExceeded #type: ignore
from rag import ingest_document, query_document, delete_document, get_all_documents

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Docquery API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://docquery-app.netlify.app"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class QuestionRequest(BaseModel):
    doc_id: str
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/documents")
def list_documents():
    return get_all_documents()


@app.post("/upload")
@limiter.limit("5/hour")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")

    doc_id = str(uuid.uuid4())
    chunk_count = ingest_document(doc_id, file.filename, file_bytes)

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "chunks": chunk_count
    }


@app.post("/ask", response_model=QuestionResponse)
@limiter.limit("20/hour")
async def ask_question(request: Request, body: QuestionRequest):
    if len(body.question) > 1000:
        raise HTTPException(status_code=400, detail="Question too long. Maximum 1000 characters")
    try:
        result = query_document(body.doc_id, body.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found or error: {str(e)}")


@app.delete("/document/{doc_id}")
def delete_doc(doc_id: str):
    success = delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": doc_id}
