import math

import requests

from config import OLLAMA_URL, EMBEDDING_MODEL, OLLAMA_TIMEOUT


class EmbeddingError(RuntimeError):
    """Error al generar o validar embeddings."""


def generate_embeddings(texts):
    """Devuelve un vector por cada texto, en el mismo orden."""
    if not isinstance(texts, list) or not texts:
        raise ValueError("texts debe ser una lista no vacía.")

    if any(
        not isinstance(text, str) or not text.strip()
        for text in texts
    ):
        raise ValueError("Cada texto debe ser una cadena no vacía.")

    payload = {
        "model": EMBEDDING_MODEL,
        "input": texts,
        "truncate": False,
    }

    try:
        with requests.post(
            f"{OLLAMA_URL}/api/embed",
            json=payload,
            timeout=(10, OLLAMA_TIMEOUT),
        ) as response:

            if not response.ok:
                try:
                    error_data = response.json()
                    detail = (
                        error_data.get("error", response.reason)
                        if isinstance(error_data, dict)
                        else response.reason
                    )
                except ValueError:
                    detail = response.reason

                raise EmbeddingError(
                    f"Ollama devolvió HTTP {response.status_code}: {detail}"
                )

            try:
                data = response.json()
            except ValueError as error:
                raise EmbeddingError(
                    "Ollama no devolvió JSON válido."
                ) from error

    except requests.exceptions.Timeout as error:
        raise EmbeddingError(
            "Se agotó el tiempo de espera al generar embeddings."
        ) from error

    except requests.exceptions.ConnectionError as error:
        raise EmbeddingError(
            f"No se pudo conectar con Ollama en {OLLAMA_URL}."
        ) from error

    except requests.exceptions.RequestException as error:
        raise EmbeddingError(
            f"Error durante la petición: {error}"
        ) from error

    if not isinstance(data, dict):
        raise EmbeddingError("Formato de respuesta inesperado.")

    if data.get("error"):
        raise EmbeddingError(f"Ollama informó: {data['error']}")

    vectors = data.get("embeddings")

    if not isinstance(vectors, list) or len(vectors) != len(texts):
        raise EmbeddingError(
            "La cantidad de vectores no coincide con los textos enviados."
        )

    dimension = None

    for vector in vectors:
        if not isinstance(vector, list) or not vector:
            raise EmbeddingError("Se recibió un vector vacío o inválido.")

        if any(
            type(value) not in (int, float)
            or not math.isfinite(value)
            for value in vector
        ):
            raise EmbeddingError(
                "El vector contiene valores numéricos inválidos."
            )

        if not any(value != 0 for value in vector):
            raise EmbeddingError("Se recibió un vector de ceros.")

        if dimension is None:
            dimension = len(vector)
        elif len(vector) != dimension:
            raise EmbeddingError(
                "Los vectores tienen dimensiones diferentes."
            )

    return vectors


def embed_query(text):
    """Genera el vector de una pregunta."""
    return generate_embeddings([text])[0]


def main():
    texts = [
        "La bomba presenta vibración elevada.",
        "El motor requiere mantenimiento preventivo.",
    ]

    print(f"Modelo de embeddings: {EMBEDDING_MODEL}")

    try:
        vectors = generate_embeddings(texts)
    except EmbeddingError as error:
        print(f"Error: {error}")
        return 1

    print(f"Vectores generados: {len(vectors)}")
    print(f"Dimensiones por vector: {len(vectors[0])}")

    for text, vector in zip(texts, vectors):
        print(f"\nTexto: {text}")
        print(f"Primeros 5 valores: {vector[:5]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())