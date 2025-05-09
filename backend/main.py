import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.database.db_manager import DatabaseManager
from backend.embedding.call_embedding import get_chat_completion

EMBEDDING_PROVIDER = "openai"
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

db_manager = DatabaseManager(
    embedding=EMBEDDING_PROVIDER
)
vector_db = db_manager.get_db()
@app.post("/ask")
async def ask_question(query: ChatRequest):
    related_docs = vector_db.similarity_search(query.message, k=3)
    context = "\n\n".join([doc.page_content for doc in related_docs])

    prompt = f"Based on the following content, answer the user's question:\n\n{context}\n\nQuestion: {query.message}\n\nAnswer:"

    answer = get_chat_completion(
        prompt=prompt,
        model="gpt-4.1-mini",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=512
    )

    return {"answer": answer}
