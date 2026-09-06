from pathlib import Path

from app.ingestion.github import (
    clone_repository,
    find_source_files,
)

from app.retrieval.chunker import (
    create_code_chunks,
)

from app.services.embeddings import (
    create_embedding,
)

from app.services.qdrant_service import (
    reset_collection,
    store_code_chunk,
)


def index_repository(
    repository_url: str,
    destination: str,
) -> dict:
    """
    Clone a GitHub repository and index its source code.

    Pipeline:

        GitHub repository
              ↓
        Clone repository
              ↓
        Find source files
              ↓
        Create code chunks
              ↓
        Create embeddings
              ↓
        Store in Qdrant
    """

    print("=" * 60)
    print("CODEATLAS REPOSITORY INDEXING")
    print("=" * 60)

    # --------------------------------------------------
    # 1. Clone repository
    # --------------------------------------------------

    print(
        "\n[1/5] Preparing repository...",
        flush=True,
    )

    repository_path = clone_repository(
        repository_url,
        destination,
    )

    print(
        f"Repository path: {repository_path}",
        flush=True,
    )

    # --------------------------------------------------
    # 2. Find useful source files
    # --------------------------------------------------

    print(
        "\n[2/5] Finding source files...",
        flush=True,
    )

    source_files = find_source_files(
        repository_path
    )

    print(
        f"Found {len(source_files)} source files.",
        flush=True,
    )

    if not source_files:
        raise ValueError(
            "No supported source files were found "
            "in the repository."
        )

    # --------------------------------------------------
    # 3. Create a fresh Qdrant collection
    # --------------------------------------------------

    print(
        "\n[3/5] Preparing vector database...",
        flush=True,
    )

    reset_collection()

    # --------------------------------------------------
    # 4. Index source files
    # --------------------------------------------------

    print(
        "\n[4/5] Creating embeddings and "
        "indexing code...",
        flush=True,
    )

    point_id = 1
    total_chunks = 0
    processed_files = 0

    # NEW:
    # Keep track of exactly how many chunks
    # were created for each source file.
    file_chunk_counts = {}

    for file_number, file_path in enumerate(
        source_files,
        start=1,
    ):

        print(
            f"\n[{file_number}/{len(source_files)}] "
            f"Processing: {file_path}",
            flush=True,
        )

        try:

            chunks = create_code_chunks(
                str(file_path)
            )

            print(
                f"    Chunks found: {len(chunks)}",
                flush=True,
            )

            # Get the repository-relative path.
            relative_path = str(
                Path(file_path).relative_to(
                    Path(repository_path)
                )
            )

            # Store the number of chunks for this file.
            file_chunk_counts[
                relative_path
            ] = len(chunks)

            for chunk in chunks:

                print(
                    f"    Embedding: "
                    f"{chunk['symbol']} "
                    f"({chunk['start_line']}-"
                    f"{chunk['end_line']})",
                    flush=True,
                )

                embedding = create_embedding(
                    chunk["content"]
                )

                store_code_chunk(
                    point_id=point_id,
                    embedding=embedding,
                    code=chunk["content"],
                    metadata={
                        "file_path": chunk["file_path"],
                        "language": chunk["language"],
                        "symbol": chunk["symbol"],
                        "type": chunk["type"],
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                        "repository_url": repository_url,
                    },
                )

                point_id += 1
                total_chunks += 1

            processed_files += 1

        except Exception as error:

            print(
                f"    Skipping {file_path}: {error}",
                flush=True,
            )

    # --------------------------------------------------
    # 5. Return results
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("REPOSITORY INDEXING COMPLETE")
    print("=" * 60)

    print(
        f"Files processed: {processed_files}",
        flush=True,
    )

    print(
        f"Code chunks indexed: {total_chunks}",
        flush=True,
    )

    return {
        "repository_path": str(
            Path(repository_path)
        ),

        "files": processed_files,

        "chunks": total_chunks,

        # NEW:
        # Per-file chunk information.
        "file_chunk_counts": file_chunk_counts,
    }