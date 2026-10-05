import argparse
import warnings
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PyPdfError


class DocumentLoadError(RuntimeError):
    """Error al leer o extraer el contenido de un documento."""


def load_pdf(file_path):
    """
    Extrae texto de un PDF.

    Devuelve una lista de diccionarios con:
    source: ruta del archivo.
    page: número de página física, empezando por 1.
    text: texto extraído.
    """
    path = Path(file_path).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Este lector solamente admite archivos PDF.")

    documents = []

    try:
        with path.open("rb") as file:
            reader = PdfReader(file)

            if reader.is_encrypted:
                raise DocumentLoadError(
                    "El PDF está cifrado. Esta versión no admite contraseñas."
                )

            for page_number, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()

                if not text:
                    warnings.warn(
                        f"{path.name}, página {page_number}: "
                        "sin texto extraíble; puede estar vacía "
                        "o requerir OCR.",
                        stacklevel=2,
                    )
                    continue

                documents.append(
                    {
                        "source": str(path),
                        "page": page_number,
                        "text": text,
                    }
                )

    except (OSError, PyPdfError) as error:
        raise DocumentLoadError(
            f"No se pudo leer {path.name}: {error}"
        ) from error

    if not documents:
        raise DocumentLoadError(
            f"No se encontró texto extraíble en {path.name}."
        )

    return documents


def main():
    parser = argparse.ArgumentParser(
        description="Extrae texto de un PDF para revisar su contenido."
    )
    parser.add_argument("pdf", help="Ruta del archivo PDF.")
    args = parser.parse_args()

    try:
        documents = load_pdf(args.pdf)
    except (FileNotFoundError, ValueError, DocumentLoadError) as error:
        print(f"Error: {error}")
        return 1

    print(f"\nArchivo: {documents[0]['source']}")
    print(f"Páginas con texto: {len(documents)}")
    print(
        "Caracteres extraídos:",
        sum(len(document["text"]) for document in documents),
    )

    # Muestra las primeras tres páginas con texto.
    for document in documents[:3]:
        print(f"\n--- Página {document['page']} ---")
        print(document["text"][:1200])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())