import hashlib
import json

import chromadb

from config import VECTOR_DB_PATH, EMBEDDING_MODEL


COLLECTION_NAME = "industrial_documents_v1"


def get_collection():
    """Abre o crea la colección persistente de fragmentos."""
    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=None,
        configuration={"hnsw": {"space": "cosine"}},
        metadata={"embedding_model": EMBEDDING_MODEL},
    )

    stored_model = (collection.metadata or {}).get("embedding_model")

    if stored_model != EMBEDDING_MODEL:
        raise ValueError(
            f"La colección usa {stored_model!r}, pero config.py "
            f"indica {EMBEDDING_MODEL!r}. Debes crear un nuevo índice "
            "para cambiar de modelo."
        )

    return collection


def make_chunk_id(chunk):
    """Genera un identificador estable para cada posición de fragmento."""
    identity = [
        chunk["source"],
        chunk["page"],
        chunk["chunk_index"],
    ]

    encoded = json.dumps(
        identity,
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def store_chunks(chunks, embeddings):
    """Guarda fragmentos y vectores recibidos en el mismo orden."""
    if not chunks:
        raise ValueError("No hay fragmentos para guardar.")

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Debe existir exactamente un vector por fragmento."
        )

    ids = [make_chunk_id(chunk) for chunk in chunks]

    if len(set(ids)) != len(ids):
        raise ValueError("Hay fragmentos con identificadores repetidos.")

    collection = get_collection()

    # Respeta el límite de registros por operación del cliente.
    client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
    batch_size = client.get_max_batch_size()

    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        batch = chunks[start:end]

        collection.upsert(
            ids=ids[start:end],
            embeddings=embeddings[start:end],
            documents=[chunk["text"] for chunk in batch],
            metadatas=[
                {
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"],
                    "start_char": chunk["start_char"],
                    "end_char": chunk["end_char"],
                }
                for chunk in batch
            ],
        )

    return len(chunks)


def search_chunks(query_embedding, top_k=3):
    """Devuelve los fragmentos más cercanos al vector de la pregunta."""
    if type(top_k) is not int or top_k <= 0:
        raise ValueError("top_k debe ser un entero positivo.")

    collection = get_collection()
    count = collection.count()

    if count == 0:
        return []

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for chunk_id, text, metadata, distance in zip(
        result["ids"][0],
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        matches.append(
            {
                "id": chunk_id,
                "text": text,
                "source": metadata["source"],
                "page": metadata["page"],
                "chunk_index": metadata["chunk_index"],
                "distance": distance,
            }
        )

    return matches


def main():
    collection = get_collection()

    print(f"Base vectorial: {VECTOR_DB_PATH}")
    print(f"Colección: {collection.name}")
    print(f"Modelo de embeddings: {EMBEDDING_MODEL}")
    print(f"Fragmentos almacenados: {collection.count()}")


if __name__ == "__main__":
    main()