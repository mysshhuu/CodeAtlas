from app.services.llm import generate_answer


context = """
File: app/main.py
Symbol: health_check
Lines: 12-16

def health_check():
    return {
        "status": "ok"
    }
"""


question = "Where is the health check implemented?"


answer = generate_answer(
    question=question,
    context=context,
)


print()
print("=" * 60)
print("CODEATLAS LLM TEST")
print("=" * 60)

print()
print("Question:")
print(question)

print()
print("Answer:")
print(answer)

print()
print("=" * 60)