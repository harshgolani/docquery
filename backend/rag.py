import os
import io
from dotenv import load_dotenv #type: ignore
from pypdf import PdfReader #type: ignore
from sentence_transformers import SentenceTransformer #type: ignore
import chromadb #type: ignore
import anthropic #type: ignore

load_dotenv()

# Load embedding model once at startup
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Persistent ChromaDB — documents survive server restarts
chroma_client = chromadb.PersistentClient(path="chroma_db")

# Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# In-memory document registry: {doc_id: {"filename": str, "chunks": int}}
document_registry: dict = {}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def ingest_document(doc_id: str, filename: str, file_bytes: bytes) -> int:
    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text(text)

    collection = chroma_client.get_or_create_collection(name=doc_id)

    embeddings = embedding_model.encode(chunks).tolist()

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    )

    document_registry[doc_id] = {
        "filename": filename,
        "chunks": len(chunks)
    }

    return len(chunks)


def get_all_documents() -> list[dict]:
    return [
        {"doc_id": doc_id, **meta}
        for doc_id, meta in document_registry.items()
    ]


def query_document(doc_id: str, question: str, n_results: int = 4) -> dict:
    collection = chroma_client.get_collection(name=doc_id)

    question_embedding = embedding_model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results
    )

    chunks = results["documents"][0]
    context = "\n\n---\n\n".join(chunks)

    response = anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system="""You are a helpful assistant that answers questions based on the provided document context.
Always base your answer on the context provided. If the answer is not in the context, say so clearly.
Be concise and accurate.""",
        messages=[
            {
                "role": "user",
                "content": f"Context from document:\n\n{context}\n\nQuestion: {question}"
            }
        ]
    )

    return {
        "answer": response.content[0].text,
        "sources": chunks
    }


def delete_document(doc_id: str) -> bool:
    try:
        chroma_client.delete_collection(name=doc_id)
        document_registry.pop(doc_id, None)
        return True
    except Exception:
        return False
