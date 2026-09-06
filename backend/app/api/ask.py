from fastapi import APIRouter
from pydantic import BaseModel

from app.rag import answer_question


router = APIRouter(
    prefix="/ask",
    tags=["CodeAtlas"],
)


class AskRequest(BaseModel):
    question: str
    limit: int = 5


class Source(BaseModel):
    file_path: str
    symbol: str
    start_line: int
    end_line: int
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


@router.post(
    "",
    response_model=AskResponse,
)
def ask_codebase(
    request: AskRequest,
):
    """
    Ask a question about the indexed codebase.
    """

    result = answer_question(
        question=request.question,
        limit=request.limit,
    )

    return result