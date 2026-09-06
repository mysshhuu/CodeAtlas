from app.services.qdrant_service import (
    create_collection,
    store_code_chunk,
)


create_collection()


fake_embedding = [0.0] * 1536


store_code_chunk(
    point_id=1,
    embedding=fake_embedding,
    code="""
def authenticate_user(username, password):
    return database.verify(username, password)
""",
    metadata={
        "file_path": "src/auth/service.py",
        "language": "python",
        "symbol": "authenticate_user",
        "start_line": 10,
        "end_line": 11,
    },
)


print()
print("=" * 60)
print("QDRANT TEST PASSED")
print("=" * 60)