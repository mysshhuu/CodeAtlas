from pathlib import Path

from git import Repo


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".venv",
    "venv",
    "tests",
    "docs",
    "docs_src",
    "scripts",
}


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}


def clone_repository(
    repo_url: str,
    destination: str,
) -> str:
    destination_path = Path(destination)

    if destination_path.exists():
        return str(destination_path)

    Repo.clone_from(
        repo_url,
        destination_path,
    )

    return str(destination_path)


def find_source_files(
    repository_path: str,
) -> list[Path]:
    root = Path(repository_path)

    source_files = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        if any(
            part in IGNORED_DIRECTORIES
            for part in path.parts
        ):
            continue

        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            source_files.append(path)

    return source_files