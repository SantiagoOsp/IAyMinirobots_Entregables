import sqlite3
from contextlib import closing

from config import DATABASE_PATH, SCHEMA_PATH, prepare_directories


def get_connection():
    """Abre una conexión con SQLite y activa las claves foráneas."""
    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10,
    )

    try:
        # Permite consultar columnas por nombre.
        connection.row_factory = sqlite3.Row

        # Debe activarse en cada conexión.
        connection.execute("PRAGMA foreign_keys = ON")

        return connection

    except Exception:
        connection.close()
        raise


def initialize_database():
    """Crea las carpetas y tablas necesarias."""
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(
            f"No se encontró el esquema SQL: {SCHEMA_PATH}"
        )

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    prepare_directories()

    with closing(get_connection()) as connection:
        try:
            # Crea el esquema dentro de una única transacción.
            connection.executescript(
                "BEGIN;\n" + schema + "\nCOMMIT;"
            )

        except sqlite3.Error:
            if connection.in_transaction:
                connection.rollback()
            raise


def get_table_names():
    """Devuelve los nombres de las tablas de la aplicación."""
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        return [row["name"] for row in rows]


def main():
    initialize_database()

    print(f"Base de datos inicializada: {DATABASE_PATH}")
    print("\nTablas disponibles:")

    for table_name in get_table_names():
        print(f"- {table_name}")


if __name__ == "__main__":
    main()