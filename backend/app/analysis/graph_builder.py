from pathlib import Path

from app.analysis.parser import (
    extract_functions,
    extract_calls,
)

from app.analysis.graph import (
    CodeGraph,
    create_graph,
    add_parser_results,
    add_parser_calls,
)


def build_repository_graph(
    repository_path: str,
) -> CodeGraph:
    """
    Build a CodeAtlas graph from an entire Python repository.

    Each function/class becomes a graph node.
    Each function call becomes a graph edge.
    """

    graph = create_graph()

    repository = Path(repository_path)

    if not repository.exists():
        raise FileNotFoundError(
            f"Repository not found: {repository_path}"
        )

    # ========================================================
    # DIRECTORIES TO IGNORE
    # ========================================================

    ignored_directories = {
        "__pycache__",
        ".venv",
        "venv",
        ".git",
        "node_modules",
        "site-packages",
        "dist",
        "build",
    }

    # ========================================================
    # FIND PYTHON FILES
    # ========================================================

    python_files = [
        path
        for path in repository.rglob("*.py")
        if not any(
            ignored in path.parts
            for ignored in ignored_directories
        )
    ]

    print(
        f"Found {len(python_files)} Python files.",
        flush=True,
    )

    # ========================================================
    # PROCESS EACH FILE
    # ========================================================

    for index, file_path in enumerate(
        python_files,
        start=1,
    ):

        print(
            f"[{index}/{len(python_files)}] "
            f"Parsing: {file_path}",
            flush=True,
        )

        try:

            # ------------------------------------------------
            # READ FILE
            # ------------------------------------------------

            source_code = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            print(
                "    Extracting functions...",
                flush=True,
            )

            # ------------------------------------------------
            # EXTRACT FUNCTIONS
            # ------------------------------------------------

            parsed_items = extract_functions(
                source_code
            )

            print(
                f"    Functions found: "
                f"{len(parsed_items)}",
                flush=True,
            )

            print(
                "    Extracting calls...",
                flush=True,
            )

            # ------------------------------------------------
            # EXTRACT CALLS
            # ------------------------------------------------

            calls = extract_calls(
                source_code
            )

            print(
                f"    Calls found: "
                f"{len(calls)}",
                flush=True,
            )

            # ------------------------------------------------
            # RELATIVE PATH
            # ------------------------------------------------

            relative_path = str(
                file_path.relative_to(repository)
            )

            # ------------------------------------------------
            # ADD NODES
            # ------------------------------------------------

            add_parser_results(
                graph,
                parsed_items,
                relative_path,
            )

            # ------------------------------------------------
            # ADD EDGES
            # ------------------------------------------------

            add_parser_calls(
                graph,
                calls,
            )

            print(
                "    Added to graph.",
                flush=True,
            )

        except Exception as error:

            print(
                f"    Skipping {file_path}: {error}",
                flush=True,
            )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "Finished building graph:",
        flush=True,
    )

    print(
        f"    Nodes: {len(graph.nodes)}",
        flush=True,
    )

    print(
        f"    Edges: {len(graph.edges)}",
        flush=True,
    )

    return graph