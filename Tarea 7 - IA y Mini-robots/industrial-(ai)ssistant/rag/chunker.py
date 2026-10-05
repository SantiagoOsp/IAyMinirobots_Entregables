import argparse

from rag.document_loader import load_pdf, DocumentLoadError


def chunk_documents(documents, chunk_size=1000, overlap=150):
    """
    Divide las páginas en fragmentos medidos en caracteres.

    Conserva la fuente, la página y la posición del fragmento
    dentro del texto extraído.
    """
    if (
        type(chunk_size) is not int
        or type(overlap) is not int
        or chunk_size <= 0
        or not 0 <= overlap < chunk_size
    ):
        raise ValueError(
            "chunk_size debe ser un entero positivo y "
            "overlap un entero entre 0 y chunk_size - 1."
        )

    chunks = []

    for document in documents:
        source = document["source"]
        page = document["page"]
        text = document["text"]

        if not isinstance(text, str):
            raise ValueError("El texto de cada página debe ser una cadena.")

        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            fragment = text[start:end]

            if fragment.strip():
                chunks.append(
                    {
                        "source": source,
                        "page": page,
                        "chunk_index": chunk_index,
                        "start_char": start,
                        "end_char": end,
                        "text": fragment,
                    }
                )
                chunk_index += 1

            # Evita generar fragmentos adicionales al llegar al final.
            if end == len(text):
                break

            start = end - overlap

    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Divide el texto de un PDF en fragmentos."
    )
    parser.add_argument("pdf", help="Ruta del archivo PDF.")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=150)
    args = parser.parse_args()

    try:
        documents = load_pdf(args.pdf)
        chunks = chunk_documents(
            documents,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
        )
    except (FileNotFoundError, ValueError, DocumentLoadError) as error:
        print(f"Error: {error}")
        return 1

    print(f"\nPáginas con texto: {len(documents)}")
    print(f"Fragmentos generados: {len(chunks)}")

    for chunk in chunks[:3]:
        print(
            f"\n--- Página {chunk['page']} | "
            f"Fragmento {chunk['chunk_index'] + 1} | "
            f"{len(chunk['text'])} caracteres ---"
        )
        print(chunk["text"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())