import sqlite3
from contextlib import closing

from database.database import get_connection, initialize_database


MIGRATION_SQL = """
CREATE TABLE IF NOT EXISTS solicitudes_orden (
    solicitud_id TEXT PRIMARY KEY NOT NULL
        CHECK (length(trim(solicitud_id)) > 0),

    orden_id INTEGER NOT NULL UNIQUE,

    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (orden_id)
        REFERENCES ordenes_trabajo(id)
);
"""


def migrate():
    """Añade la tabla sin modificar órdenes ni historiales existentes."""
    initialize_database()

    with closing(get_connection()) as connection:
        with connection:
            connection.execute(MIGRATION_SQL)

        columns = connection.execute(
            "PRAGMA table_info(solicitudes_orden)"
        ).fetchall()

        column_names = {column["name"] for column in columns}

        expected = {
            "solicitud_id",
            "orden_id",
            "fecha_creacion",
        }

        if column_names != expected:
            raise RuntimeError(
                "La tabla solicitudes_orden tiene una estructura inesperada."
            )


def main():
    try:
        migrate()
    except (OSError, sqlite3.Error, RuntimeError) as error:
        print(f"Error durante la migración: {error}")
        return 1

    print("Migración completada.")
    print("Tabla disponible: solicitudes_orden")
    print("Las órdenes y los historiales existentes se conservaron.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())