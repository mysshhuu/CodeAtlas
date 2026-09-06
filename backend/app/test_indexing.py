from pathlib import Path

from app.retrieval.chunker import create_code_chunks
from app.services.embeddings import create_embedding
from app.services.qdrant_service import (
    create_collection,
    store_code_chunk,
)


# Change this to a Python file that already exists
TEST_FILE = Path("app/main.py")


def main():
    print("=" * 60)
    print("CODEATLAS INDEXING TEST")
    print("=" * 60)

    # Make sure Qdrant collection exists
    create_collection()

    # Create code chunks
    chunks = create_code_chunks(str(TEST_FILE))

    print(f"\nFound {len(chunks)} code chunks.")

    for index, chunk in enumerate(chunks):

        print(
            f"\nEmbedding: "
            f"{chunk['symbol']} "
            f"({chunk['start_line']}-{chunk['end_line']})"
        )

        # Create embedding from code
        embedding = create_embedding(chunk["content"])

        # Store in Qdrant
        store_code_chunk(
            point_id=index + 1,
            embedding=embedding,
            code=chunk["content"],
            metadata={
                "file_path": chunk["file_path"],
                "language": chunk["language"],
                "symbol": chunk["symbol"],
                "type": chunk["type"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
            },
        )

    print("\n" + "=" * 60)
    print("INDEXING TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()