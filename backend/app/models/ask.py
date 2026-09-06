from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    limit: int = 5


class Source(BaseModel):
    file_path: str
    symbol: str
    start_line: int | None
    end_line: int | None
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]