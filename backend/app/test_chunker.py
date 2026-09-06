from pathlib import Path

from app.retrieval.chunker import create_code_chunks


test_file = Path("data/test_example.py")

test_file.parent.mkdir(
    parents=True,
    exist_ok=True,
)


test_file.write_text(
    """
def create_user(name):
    user = {"name": name}
    return user


def delete_user(user_id):
    print(f"Deleting {user_id}")
""",
    encoding="utf-8",
)


chunks = create_code_chunks(
    str(test_file)
)


print()
print("=" * 60)
print("CODEATLAS CHUNKING TEST")
print("=" * 60)

print(f"Chunks created: {len(chunks)}")

for index, chunk in enumerate(
    chunks,
    start=1,
):

    print()
    print(f"CHUNK {index}")
    print("-" * 60)

    print(
        f"Symbol: {chunk['symbol']}"
    )

    print(
        f"File: {chunk['file_path']}"
    )

    print(
        f"Lines: "
        f"{chunk['start_line']}"
        f"-"
        f"{chunk['end_line']}"
    )

    print()
    print(chunk["content"])

print()
print("=" * 60)