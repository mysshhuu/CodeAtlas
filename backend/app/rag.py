from app.retrieval.service import retrieve_code
from app.services.llm import generate_answer


def build_context(results: list[dict]) -> str:
    """
    Convert retrieved code chunks into context
    that the LLM can understand.
    """

    context_parts = []

    for result in results:

        context_parts.append(
            f"""
File: {result['file_path']}
Symbol: {result['symbol']}
Type: {result['type']}
Lines: {result['start_line']}-{result['end_line']}

Code:
{result['code']}
"""
        )

    return "\n".join(context_parts)


def answer_question(
    question: str,
    limit: int = 5,
) -> dict:
    """
    Complete CodeAtlas RAG pipeline.

    Question
        ↓
    Retrieval
        ↓
    Context
        ↓
    LLM
        ↓
    Answer
    """

    # 1. Retrieve relevant code
    results = retrieve_code(
        question,
        limit=limit,
    )

    # 2. Build context
    context = build_context(results)

    # 3. Generate answer
    answer = generate_answer(
        question=question,
        context=context,
    )

    # 4. Build source information
    sources = []

    for result in results:

        sources.append(
            {
                "file_path": result["file_path"],
                "symbol": result["symbol"],
                "start_line": result["start_line"],
                "end_line": result["end_line"],
                "score": result["score"],
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }