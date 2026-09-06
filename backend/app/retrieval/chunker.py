from pathlib import Path

from app.analysis.parser import extract_functions


# Maximum number of lines we keep for a class overview chunk.
# The individual methods will still be indexed separately.
CLASS_OVERVIEW_LINES = 40


def create_software_chunk(
    content: str,
    file_path: str,
    language: str,
    symbol: str,
    chunk_type: str,
    start_line: int,
    end_line: int,
) -> dict:
    """
    Create a standardized CodeAtlas code chunk.
    """

    return {
        "content": content,
        "file_path": file_path,
        "language": language,
        "symbol": symbol,
        "type": chunk_type,
        "start_line": start_line,
        "end_line": end_line,
    }


def create_fallback_chunk(
    source_code: str,
    file_path: str,
) -> dict:
    """
    Create a fallback chunk for files where the parser
    cannot find any functions or classes.

    This prevents an entire source file from disappearing
    from the CodeAtlas index.
    """

    lines = source_code.splitlines()

    return create_software_chunk(
        content=source_code,
        file_path=file_path,
        language=Path(file_path).suffix.lstrip("."),
        symbol=Path(file_path).stem,
        chunk_type="file",
        start_line=1,
        end_line=len(lines),
    )


def create_class_overview_chunk(
    lines: list[str],
    class_info: dict,
    file_path: str,
) -> dict:
    """
    Create a compact overview chunk for a class.

    Large classes can contain hundreds of lines. Instead of
    embedding the entire class as one huge vector, we keep
    the beginning of the class, which contains the class
    declaration, docstring, and usually important metadata.
    Individual methods are indexed separately.
    """

    start = class_info["start_line"]
    end = class_info["end_line"]

    overview_end = min(
        start + CLASS_OVERVIEW_LINES - 1,
        end,
        len(lines),
    )

    content = "\n".join(
        lines[start - 1:overview_end]
    )

    return create_software_chunk(
        content=content,
        file_path=file_path,
        language=Path(file_path).suffix.lstrip("."),
        symbol=class_info["name"],
        chunk_type="class",
        start_line=start,
        end_line=overview_end,
    )


def create_code_chunks(
    file_path: str,
) -> list[dict]:
    """
    Convert a source file into code-aware chunks.

    CodeAtlas chunking strategy:

        Source file
             ↓
        Parse functions/classes
             ↓
        Class → class overview + methods
        Function → function chunk
             ↓
        If nothing was parsed → whole-file fallback chunk

    This makes the chunker robust against:
    - large classes
    - files containing only classes
    - files containing only functions
    - parser edge cases
    - files with no recognized definitions
    """

    path = Path(file_path)

    source_code = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    lines = source_code.splitlines()

    chunks = []

    try:
        definitions = extract_functions(
            source_code
        )
    except Exception as error:
        print(
            f"    Parser failed for {file_path}: {error}",
            flush=True,
        )

        return [
            create_fallback_chunk(
                source_code,
                str(path),
            )
        ]

    for definition in definitions:

        start = definition["start_line"]
        end = definition["end_line"]

        if start < 1:
            continue

        if start > len(lines):
            continue

        end = min(
            end,
            len(lines),
        )

        # --------------------------------------------------
        # CLASS
        # --------------------------------------------------

        if definition["type"] == "class":

            class_chunk = create_class_overview_chunk(
                lines=lines,
                class_info=definition,
                file_path=str(path),
            )

            chunks.append(
                class_chunk
            )

        # --------------------------------------------------
        # FUNCTION
        # --------------------------------------------------

        else:

            content = "\n".join(
                lines[start - 1:end]
            )

            chunks.append(
                create_software_chunk(
                    content=content,
                    file_path=str(path),
                    language=path.suffix.lstrip("."),
                    symbol=definition["name"],
                    chunk_type=definition["type"],
                    start_line=start,
                    end_line=end,
                )
            )

    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------

    # If the parser didn't find anything, don't throw
    # the entire file away.
    if not chunks and source_code.strip():

        print(
            f"    No definitions found. "
            f"Creating fallback file chunk.",
            flush=True,
        )

        chunks.append(
            create_fallback_chunk(
                source_code,
                str(path),
            )
        )

    return chunks