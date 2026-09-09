import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

load_dotenv()

COLLECTION_NAME = "codeatlas_code"

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


# Use Qdrant Cloud when credentials are available.
# Otherwise, fall back to local Qdrant storage.
if QDRANT_URL and QDRANT_API_KEY:
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
    print("Connected to Qdrant Cloud")
else:
    client = QdrantClient(
        path="data/qdrant"
    )
    print("Using local Qdrant database")


def create_collection():
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
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
        with_payload=True,
    )

    return results.points