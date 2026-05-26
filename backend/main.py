import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException #type: ignore
from fastapi.middleware.cors import CORSMiddleware #type: ignore
from pydantic import BaseModel #type: ignore
from rag import ingest_document, query_document, delete_document, get_all_documents

app = FastAPI(title="Docquery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()
    doc_id = str(uuid.uuid4())

    chunk_count = ingest_document(doc_id, file.filename, file_bytes)

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "chunks": chunk_count
    }


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    try:
        result = query_document(request.doc_id, request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found or error: {str(e)}")


@app.delete("/document/{doc_id}")
def delete_doc(doc_id: str):
    success = delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": doc_id}
