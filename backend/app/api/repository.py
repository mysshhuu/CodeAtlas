from git import Repo
from pathlib import Path
from urllib.parse import urlparse
import json

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.repository_indexer import (
    index_repository,
)

from app.analysis.parser import (
    extract_functions,
    extract_calls,
)


router = APIRouter(
    prefix="/repository",
    tags=["Repository"],
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class RepositoryRequest(BaseModel):
    repository_url: str


class RepositoryResponse(BaseModel):
    message: str
    repository_url: str
    repository_path: str
    files: int
    chunks: int


class FileInfo(BaseModel):
    file_path: str
    language: str
    chunks: int


class FilesResponse(BaseModel):
    repository_path: str
    files: list[FileInfo]


class DependencyNode(BaseModel):
    id: str
    name: str
    node_type: str
    file_path: str
    start_line: int
    end_line: int


class DependencyEdge(BaseModel):
    source: str
    target: str
    relationship: str


class DependenciesResponse(BaseModel):
    repository_path: str
    files: int
    nodes: int
    functions: int
    classes: int
    calls: int
    edges: list[DependencyEdge]
    nodes_data: list[DependencyNode]


class CommitInfo(BaseModel):
    hash: str
    short_hash: str
    message: str
    author: str
    date: str


class HistoryResponse(BaseModel):
    repository_path: str
    commits: list[CommitInfo]


# ============================================================
# HELPERS
# ============================================================

IGNORED_DIRECTORIES = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "site-packages",
    "tests",
    "docs",
    "docs_src",
    "scripts",
}


def get_repository_name(
    repository_url: str,
) -> str:
    parsed_url = urlparse(
        repository_url
    )

    path = parsed_url.path.strip("/")

    if not path:
        raise ValueError(
            "Invalid repository URL."
        )

    repository_name = path.split("/")[-1]

    if repository_name.endswith(".git"):
        repository_name = repository_name[:-4]

    if not repository_name:
        raise ValueError(
            "Could not determine repository name."
        )

    return repository_name


def get_latest_repository():
    repositories_root = Path(
        "data/repos"
    )

    if not repositories_root.exists():
        return None

    repositories = [
        path
        for path in repositories_root.iterdir()
        if path.is_dir()
        and path.name != "__pycache__"
    ]

    if not repositories:
        return None

    return max(
        repositories,
        key=lambda path: path.stat().st_mtime,
    )


# ============================================================
# INDEX REPOSITORY
# ============================================================

@router.post(
    "/index",
    response_model=RepositoryResponse,
)
def index_repository_endpoint(
    request: RepositoryRequest,
):
    repository_name = get_repository_name(
        request.repository_url
    )

    destination = str(
        Path("data/repos") / repository_name
    )

    result = index_repository(
        repository_url=request.repository_url,
        destination=destination,
    )

    # Save the per-file chunk information so that
    # GET /repository/files can use the exact
    # information produced during indexing.

    repository_path = Path(
        result["repository_path"]
    )

    chunk_counts_file = (
        repository_path
        / ".codeatlas_file_chunks.json"
    )

    chunk_counts_file.write_text(
        json.dumps(
            result.get(
                "file_chunk_counts",
                {}
            ),
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "message": "Repository indexed successfully.",
        "repository_url": request.repository_url,
        "repository_path": result["repository_path"],
        "files": result["files"],
        "chunks": result["chunks"],
    }


# ============================================================
# GET REPOSITORY FILES
# ============================================================

@router.get(
    "/files",
    response_model=FilesResponse,
)
def get_repository_files():

    repository = get_latest_repository()

    if repository is None:
        return {
            "repository_path": "",
            "files": [],
        }

    python_files = [
        path
        for path in repository.rglob("*.py")
        if not any(
            ignored in path.parts
            for ignored in IGNORED_DIRECTORIES
        )
    ]

    # Load chunk information produced during indexing.

    chunk_counts_file = (
        repository
        / ".codeatlas_file_chunks.json"
    )

    file_chunk_counts = {}

    if chunk_counts_file.exists():
        try:
            file_chunk_counts = json.loads(
                chunk_counts_file.read_text(
                    encoding="utf-8"
                )
            )
        except Exception as error:
            print(
                "Could not read CodeAtlas chunk "
                f"metadata: {error}"
            )

    # Build response.

    file_results = []

    for file_path in sorted(
        python_files
    ):

        relative_path = str(
            file_path.relative_to(
                repository
            )
        )

        chunk_count = int(
            file_chunk_counts.get(
                relative_path,
                0
            )
        )

        file_results.append(
            FileInfo(
                file_path=relative_path,
                language="Python",
                chunks=chunk_count,
            )
        )

    return {
        "repository_path": str(repository),
        "files": file_results,
    }


# ============================================================
# GET DEPENDENCIES / CODE GRAPH
# ============================================================

@router.get(
    "/dependencies",
    response_model=DependenciesResponse,
)
def get_repository_dependencies():

    repository = get_latest_repository()

    if repository is None:
        return {
            "repository_path": "",
            "files": 0,
            "nodes": 0,
            "functions": 0,
            "classes": 0,
            "calls": 0,
            "edges": [],
            "nodes_data": [],
        }

    python_files = [
        path
        for path in repository.rglob("*.py")
        if not any(
            ignored in path.parts
            for ignored in IGNORED_DIRECTORIES
        )
    ]

    nodes = []
    edges = []

    function_count = 0
    class_count = 0
    call_count = 0

    # --------------------------------------------------------
    # Analyze every Python file
    # --------------------------------------------------------

    for file_path in sorted(
        python_files
    ):

        try:
            source_code = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            relative_path = str(
                file_path.relative_to(
                    repository
                )
            )

            # ------------------------------------------------
            # Extract functions and classes
            # ------------------------------------------------

            parsed_items = extract_functions(
                source_code
            )

            for item in parsed_items:

                node_id = (
                    f"{relative_path}:"
                    f"{item['name']}"
                )

                nodes.append(
                    DependencyNode(
                        id=node_id,
                        name=item["name"],
                        node_type=item["type"],
                        file_path=relative_path,
                        start_line=item["start_line"],
                        end_line=item["end_line"],
                    )
                )

                if item["type"] == "function":
                    function_count += 1

                elif item["type"] == "class":
                    class_count += 1

            # ------------------------------------------------
            # Extract function calls
            # ------------------------------------------------

            parsed_calls = extract_calls(
                source_code
            )

            for call in parsed_calls:

                source_name = call.get(
                    "source",
                    ""
                )

                target_name = call.get(
                    "target",
                    ""
                )

                if not source_name or not target_name:
                    continue

                source_id = (
                    f"{relative_path}:"
                    f"{source_name}"
                )

                # We keep the target name because
                # a call may refer to another file,
                # an imported function, or a library.

                target_id = target_name

                edges.append(
                    DependencyEdge(
                        source=source_id,
                        target=target_id,
                        relationship=call.get(
                            "relationship",
                            "calls",
                        ),
                    )
                )

                call_count += 1

        except Exception as error:

            print(
                f"Could not analyze "
                f"{file_path}: {error}"
            )

    return {
        "repository_path": str(repository),
        "files": len(python_files),
        "nodes": len(nodes),
        "functions": function_count,
        "classes": class_count,
        "calls": call_count,
        "edges": edges,
        "nodes_data": nodes,
    }


# ============================================================
# GET GIT HISTORY
# ============================================================

@router.get(
    "/history",
    response_model=HistoryResponse,
)
def get_repository_history():

    repository = get_latest_repository()

    if repository is None:
        return {
            "repository_path": "",
            "commits": [],
        }

    try:
        git_repository = Repo(
            str(repository)
        )

        commits = []

        # Get the 20 most recent commits.
        for commit in git_repository.iter_commits(
            max_count=20
        ):

            commits.append(
                CommitInfo(
                    hash=commit.hexsha,
                    short_hash=commit.hexsha[:7],
                    message=commit.message.strip(),
                    author=str(
                        commit.author
                    ),
                    date=commit.committed_datetime.isoformat(),
                )
            )

        return {
            "repository_path": str(
                repository
            ),
            "commits": commits,
        }

    except Exception as error:

        print(
            f"Could not read Git history: {error}"
        )

        return {
            "repository_path": str(
                repository
            ),
            "commits": [],
        }