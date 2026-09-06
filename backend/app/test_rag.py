from app.rag import answer_question


question = "Where is the health check endpoint implemented?"


print("=" * 60)
print("CODEATLAS RAG TEST")
print("=" * 60)

print()
print("Question:")
print(question)

print()
print("Thinking...")
print()


result = answer_question(
    question,
    limit=5,
)


print("ANSWER")
print("-" * 60)

print(result["answer"])


print()
print()
print("SOURCES")
print("-" * 60)


for source in result["sources"]:

    print(
        f"{source['file_path']} | "
        f"{source['symbol']} | "
        f"Lines "
        f"{source['start_line']}-"
        f"{source['end_line']} | "
        f"Score: "
        f"{source['score']:.4f}"
    )


print()
print("=" * 60)
print("CODEATLAS RAG TEST COMPLETE")
print("=" * 60)