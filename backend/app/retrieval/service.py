from app.services.embeddings import create_embedding
from app.services.qdrant_service import search_code


# Directories that usually contain supporting material
# rather than the main implementation.
LOW_PRIORITY_DIRECTORIES = {
    "tests",
    "test",
    "docs",
    "docs_src",
    "benchmarks",
    "examples",
    "scripts",
}


def calculate_relevance_score(
    result: dict,
) -> float:
    """
    Adjust the Qdrant semantic similarity score.

    Qdrant gives us a semantic similarity score.
    We then slightly reduce the score for files that
    are usually tests, documentation, or examples.

    This helps CodeAtlas prefer the actual implementation.
    """

    score = result["score"]
    file_path = result["file_path"].lower()

    path_parts = file_path.replace("\\", "/").split("/")

    # Penalize supporting directories.
    for directory in LOW_PRIORITY_DIRECTORIES:
        if directory in path_parts:
            score -= 0.10

    # Give a small bonus to the main package.
    #
    # For example:
    # fastapi/applications.py
    #
    # should be preferred over:
    # tests/test_applications.py
    if "fastapi" in path_parts:
        score += 0.03

    return score


def retrieve_code(
    question: str,
    limit: int = 5,
) -> list[dict]:
    """
    Find the code chunks most relevant to a user's question.

    Pipeline:

        User question
              ↓
        Create embedding
              ↓
        Search Qdrant
              ↓
        Retrieve more candidates
              ↓
        Rerank candidates
              ↓
        Return best results
    """

    # --------------------------------------------------
    # STEP 1: Convert the question into an embedding
    # --------------------------------------------------

    query_embedding = create_embedding(
        question
    )

    # --------------------------------------------------
    # STEP 2: Retrieve more candidates than we need
    # --------------------------------------------------
    #
    # Instead of immediately taking the top 5,
    # retrieve up to 15 candidates.
    #
    # This gives our reranking step more choices.

    candidate_limit = max(
        limit * 3,
        15,
    )

    results = search_code(
        query_embedding=query_embedding,
        limit=candidate_limit,
    )

    # --------------------------------------------------
    # STEP 3: Convert Qdrant results into dictionaries
    # --------------------------------------------------

    chunks = []

    for result in results:
        payload = result.payload or {}

        chunk = {
            "score": result.score,
            "code": payload.get("code", ""),
            "file_path": payload.get("file_path", ""),
            "language": payload.get("language", ""),
            "symbol": payload.get("symbol", ""),
            "type": payload.get("type", ""),
            "start_line": payload.get("start_line"),
            "end_line": payload.get("end_line"),
        }

        # Calculate our improved relevance score.
        chunk["relevance_score"] = (
            calculate_relevance_score(chunk)
        )

        chunks.append(chunk)

    # --------------------------------------------------
    # STEP 4: Sort by our improved relevance score
    # --------------------------------------------------

    chunks.sort(
        key=lambda chunk: chunk["relevance_score"],
        reverse=True,
    )

    # --------------------------------------------------
    # STEP 5: Return only the requested number
    # --------------------------------------------------

    final_chunks = chunks[:limit]

    # Keep the original Qdrant score as the public score.
    #
    # This is useful because the frontend can still show
    # the actual vector similarity score.

    return final_chunks