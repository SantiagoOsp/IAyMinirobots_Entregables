import argparse
from pathlib import Path

from rag.embeddings import embed_query
from rag.vector_store import get_collection, search_chunks


def retrieve(question, top_k=3, max_distance=None):
    """
    Recupera fragmentos relacionados con una pregunta.

    max_distance permite descartar resultados lejanos.
    No representa un porcentaje de confianza.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("La pregunta debe contener texto.")

    if type(top_k) is not int or top_k <= 0:
        raise ValueError("top_k debe ser un entero positivo.")

    if max_distance is not None:
        if (
            type(max_distance) not in (int, float)
            or not 0 <= max_distance <= 2
        ):
            raise ValueError("max_distance debe estar entre 0 y 2.")

    # Evita consultar Ollama si todavía no hay documentos.
    if get_collection().count() == 0:
        return []

    query_embedding = embed_query(question.strip())

    matches = search_chunks(
        query_embedding,
        top_k=top_k,
    )

    if max_distance is not None:
        matches = [
            match
            for match in matches
            if match["distance"] <= max_distance
        ]

    return matches


def main():
    parser = argparse.ArgumentParser(
        description="Busca fragmentos relacionados con una pregunta."
    )
    parser.add_argument("question", help="Pregunta que deseas consultar.")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--max-distance", type=float, default=None)
    args = parser.parse_args()

    try:
        matches = retrieve(
            args.question,
            top_k=args.top_k,
            max_distance=args.max_distance,
        )
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")
        return 1

    if not matches:
        print(
            "No se recuperaron fragmentos. "
            "Comprueba que existan documentos indexados y, "
            "si aplicaste un filtro, revisa su umbral."
        )
        return 0

    print(f"\nPregunta: {args.question}")
    print(f"Fragmentos recuperados: {len(matches)}")

    for number, match in enumerate(matches, start=1):
        filename = Path(match["source"]).name

        print(f"\n--- Resultado {number} ---")
        print(f"Archivo: {filename}")
        print(f"Página física: {match['page']}")
        print(f"Fragmento: {match['chunk_index'] + 1}")
        print(f"Distancia coseno: {match['distance']:.4f}")
        print(f"\n{match['text']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())