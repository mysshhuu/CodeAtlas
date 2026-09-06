from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


COLLECTION_NAME = "codeatlas_code"

# Create a local Qdrant database
client = QdrantClient(path="data/qdrant")


def create_collection():
    """
    Create the CodeAtlas vector collection if it doesn't exist.
    """

    collections = client.get_collections().collections

    existing_collections = [
        collection.name
        for collection in collections
    ]

    if COLLECTION_NAME not in existing_collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE,
            ),
        )

        print(
            f"Created collection: {COLLECTION_NAME}"
        )

    else:
        print(
            f"Collection already exists: {COLLECTION_NAME}"
        )


def reset_collection():
    """
    Delete the existing CodeAtlas collection and
    create a fresh empty collection.

    We use this when indexing a new repository so
    old/incomplete vectors don't mix with the new
    repository.
    """

    collections = client.get_collections().collections

    existing_collections = [
        collection.name
        for collection in collections
    ]

    if COLLECTION_NAME in existing_collections:
        client.delete_collection(
            collection_name=COLLECTION_NAME
        )

        print(
            f"Deleted old collection: {COLLECTION_NAME}"
        )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE,
        ),
    )

    print(
        f"Created fresh collection: {COLLECTION_NAME}"
    )


def store_code_chunk(
    point_id: int,
    embedding: list[float],
    code: str,
    metadata: dict,
):
    """
    Store one code chunk inside Qdrant.
    """

    point = PointStruct(
        id=point_id,
        vector=embedding,
        payload={
            "code": code,
            **metadata,
        },
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point],
    )

    print(
        f"Stored code chunk: {point_id}"
    )


def search_code(
    query_embedding: list[float],
    limit: int = 5,
):
    """
    Search Qdrant for the most relevant code chunks.
    """

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
        with_payload=True,
    )

    return results.points