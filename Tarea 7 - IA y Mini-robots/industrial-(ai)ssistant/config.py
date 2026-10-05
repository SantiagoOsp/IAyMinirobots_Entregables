from pathlib import Path
import os


# Carpeta raíz del proyecto: donde está este archivo.
BASE_DIR = Path(__file__).resolve().parent


# Conexión con Ollama.
# El cliente añadirá /api/chat o /api/embed según la operación.
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434",
).rstrip("/")

LLM_MODEL = os.getenv("LLM_MODEL", "qwen3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embeddinggemma")

# Tiempo máximo de espera por respuesta, en segundos.
OLLAMA_TIMEOUT = 120


# Rutas de almacenamiento.
DATA_DIR = BASE_DIR / "data"

MANUALS_PATH = DATA_DIR / "manuals"
COURSE_DOCUMENTS_PATH = DATA_DIR / "course_documents"
VECTOR_DB_PATH = DATA_DIR / "vector_db"

DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "industrial_ai.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"

SKILLS_PATH = BASE_DIR / "skills"


def prepare_directories():
    """Crea las carpetas de almacenamiento que todavía no existan."""
    directories = (
        MANUALS_PATH,
        COURSE_DOCUMENTS_PATH,
        VECTOR_DB_PATH,
        DATABASE_DIR,
    )

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    print(f"Proyecto: {BASE_DIR}")
    print(f"Servidor Ollama: {OLLAMA_URL}")
    print(f"Modelo conversacional: {LLM_MODEL}")
    print(f"Modelo de embeddings: {EMBEDDING_MODEL}")
    print(f"Base de datos: {DATABASE_PATH}")
    print(f"Esquema SQL: {SCHEMA_PATH}")