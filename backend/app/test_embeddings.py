from app.services.embeddings import create_embedding


text = """
def authenticate_user(username, password):
    return database.verify(username, password)
"""


embedding = create_embedding(text)


print()
print("=" * 60)
print("CODEATLAS EMBEDDING TEST")
print("=" * 60)

print(f"Embedding dimensions: {len(embedding)}")

print()
print("First 10 values:")

for value in embedding[:10]:
    print(value)

print("=" * 60)