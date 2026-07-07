from fastapi import APIRouter
from app.services import rag_service
from app.schemas import RAGQueryRequest, RAGAnswerResponse

router = APIRouter()


@router.post("/query", response_model=RAGAnswerResponse)
async def rag_query(request: RAGQueryRequest):
    result = await rag_service.answer_with_rag(request.question)
    return result


@router.get("/search")
def search_questions(q: str, top_k: int = 5):
    results = rag_service.query(q, top_k)
    return {"results": results}
