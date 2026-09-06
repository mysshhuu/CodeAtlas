from app.retrieval.service import retrieve_code


question = "Where is the health check endpoint implemented?"


print("=" * 60)
print("CODEATLAS RETRIEVAL TEST")
print("=" * 60)

print()
print("Question:")
print(question)

print()
print("Searching Qdrant...")
print()


results = retrieve_code(
    question,
    limit=5,
)


if not results:
    print("No results found.")

else:
    for index, result in enumerate(results, start=1):

        print(f"RESULT #{index}")
        print("-" * 60)

        print(f"Score: {result['score']}")
        print(f"File: {result['file_path']}")
        print(f"Symbol: {result['symbol']}")
        print(f"Type: {result['type']}")

        print(
            f"Lines: "
            f"{result['start_line']}"
            f"-"
            f"{result['end_line']}"
        )

        print()
        print("Code:")
        print(result["code"])

        print()
        print("=" * 60)