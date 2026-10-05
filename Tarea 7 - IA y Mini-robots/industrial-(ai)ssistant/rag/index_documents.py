import argparse

from rag.document_loader import load_pdf
from rag.chunker import chunk_documents
from rag.embeddings import generate_embeddings
from rag.vector_store import (
    get_collection,
    make_chunk_id,
    store_chunks,
)


def index_pdf(
    file_path,
    chunk_size=1000,
    overlap=150,
    embedding_batch_size=16,
):
    """Indexa un PDF y elimina sus fragmentos anteriores sobrantes."""
    if (
        type(embedding_batch_size) is not int
        or embedding_batch_size <= 0
    ):
        raise ValueError("embedding_batch_size debe ser un entero positivo.")

    print("\nLeyendo PDF...")
    documents = load_pdf(file_path)

    print("Dividiendo texto...")
    chunks = chunk_documents(
        documents,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    if not chunks:
        raise ValueError("No se generaron fragmentos para indexar.")

    source = documents[0]["source"]
    collection = get_collection()

    # Recupera los identificadores anteriores de este archivo.
    previous = collection.get(
        where={"source": source},
        include=[],
    )
    previous_ids = set(previous["ids"])

    print(f"Páginas con texto: {len(documents)}")
    print(f"Fragmentos generados: {len(chunks)}")
    print("Generando embeddings...")

    embeddings = []
    dimension = None

    # Genera todos los vectores antes de modificar los registros.
    for start in range(0, len(chunks), embedding_batch_size):
        batch = chunks[start:start + embedding_batch_size]
        texts = [chunk["text"] for chunk in batch]

        vectors = generate_embeddings(texts)

        # Verifica que las dimensiones coincidan entre lotes.
        current_dimension = len(vectors[0])

        if dimension is None:
            dimension = current_dimension
        elif current_dimension != dimension:
            raise ValueError(
                "La dimensión de los embeddings cambió entre lotes."
            )

        embeddings.extend(vectors)

        print(
            f"Embeddings generados: "
            f"{len(embeddings)}/{len(chunks)}"
        )

    print("Guardando en ChromaDB...")
    stored = store_chunks(chunks, embeddings)

    # Elimina solamente los registros anteriores que ya no existen.
    current_ids = {make_chunk_id(chunk) for chunk in chunks}
    obsolete_ids = sorted(previous_ids - current_ids)

    for start in range(0, len(obsolete_ids), 500):
        collection.delete(ids=obsolete_ids[start:start + 500])

    # Comprueba los identificadores finales del documento.
    final = collection.get(
        where={"source": source},
        include=[],
    )

    if set(final["ids"]) != current_ids:
        raise RuntimeError(
            "La verificación final del índice no coincide "
            "con los fragmentos generados."
        )

    return {
        "source": source,
        "pages": len(documents),
        "chunks": stored,
        "removed": len(obsolete_ids),
        "dimension": dimension,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Indexa un PDF en la base vectorial."
    )
    parser.add_argument("pdf", help="Ruta del archivo PDF.")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=150)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    try:
        result = index_pdf(
            args.pdf,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            embedding_batch_size=args.batch_size,
        )
    except Exception as error:
        # Captura en la interfaz de terminal; devuelve un código de error.
        print(f"\nIndexación fallida: {type(error).__name__}: {error}")
        print(
            "Si el fallo ocurrió durante el almacenamiento, "
            "el índice puede haber quedado parcialmente actualizado. "
            "Corrige la causa y vuelve a ejecutar el comando."
        )
        return 1

    print("\nIndexación completada.")
    print(f"Archivo: {result['source']}")
    print(f"Páginas con texto: {result['pages']}")
    print(f"Fragmentos almacenados: {result['chunks']}")
    print(f"Fragmentos antiguos eliminados: {result['removed']}")
    print(f"Dimensiones por vector: {result['dimension']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())