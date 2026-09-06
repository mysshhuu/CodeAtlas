from ingestion.github import (
    clone_repository,
    find_source_files,
)


REPO_URL = "https://github.com/tiangolo/fastapi.git"

REPO_PATH = "data/repos/fastapi"


repository = clone_repository(
    REPO_URL,
    REPO_PATH,
)


files = find_source_files(repository)


print()
print("=" * 60)
print("CODEATLAS INGESTION TEST")
print("=" * 60)

print(f"Repository: {REPO_URL}")
print(f"Source files found: {len(files)}")

print()
print("First 20 source files:")
print("-" * 60)


for file in files[:20]:
    print(file)

print("=" * 60)