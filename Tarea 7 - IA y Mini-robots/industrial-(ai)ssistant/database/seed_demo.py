from contextlib import closing

from database.database import get_connection, initialize_database


EQUIPOS = [
    (
        "DEMO-P-101",
        "Bomba de demostración",
        "Zona de pruebas",
        "OPERATIVO",
    ),
    (
        "DEMO-M-101",
        "Motor de demostración",
        "Zona de pruebas",
        "OPERATIVO",
    ),
]

REPUESTOS = [
    (
        "DEMO-BRG-6205",
        "Rodamiento de demostración",
        "Fabricante ficticio",
    ),
    (
        "DEMO-SEAL-001",
        "Sello mecánico de demostración",
        "Fabricante ficticio",
    ),
]

COMPATIBILIDADES = [
    ("DEMO-P-101", "DEMO-BRG-6205"),
    ("DEMO-M-101", "DEMO-BRG-6205"),
    ("DEMO-P-101", "DEMO-SEAL-001"),
]

INVENTARIO = [
    ("DEMO-BRG-6205", 4, "DEMO-A-03-02"),
    ("DEMO-SEAL-001", 0, "DEMO-A-03-03"),
]


def seed_demo():
    """Inserta datos de prueba sin sobrescribir registros existentes."""
    initialize_database()

    with closing(get_connection()) as connection:
        # Confirma todo junto o revierte las inserciones si hay un error.
        with connection:
            connection.executemany(
                """
                INSERT INTO equipos (
                    codigo, nombre, ubicacion, estado
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(codigo) DO NOTHING
                """,
                EQUIPOS,
            )

            connection.executemany(
                """
                INSERT INTO repuestos (
                    codigo, descripcion, fabricante
                )
                VALUES (?, ?, ?)
                ON CONFLICT(codigo) DO NOTHING
                """,
                REPUESTOS,
            )

            connection.executemany(
                """
                INSERT INTO equipos_repuestos (
                    equipo_codigo, repuesto_codigo
                )
                VALUES (?, ?)
                ON CONFLICT(equipo_codigo, repuesto_codigo) DO NOTHING
                """,
                COMPATIBILIDADES,
            )

            connection.executemany(
                """
                INSERT INTO inventario (
                    codigo_repuesto, cantidad, ubicacion
                )
                VALUES (?, ?, ?)
                ON CONFLICT(codigo_repuesto) DO NOTHING
                """,
                INVENTARIO,
            )


def show_demo_inventory():
    """Muestra las existencias actuales de los repuestos de prueba."""
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT
                r.codigo,
                r.descripcion,
                i.cantidad,
                i.ubicacion
            FROM repuestos AS r
            JOIN inventario AS i
                ON i.codigo_repuesto = r.codigo
            WHERE r.codigo IN (?, ?)
            ORDER BY r.codigo
            """,
            ("DEMO-BRG-6205", "DEMO-SEAL-001"),
        ).fetchall()

    print("\nInventario de demostración:")

    for row in rows:
        print(
            f"{row['codigo']} | "
            f"{row['descripcion']} | "
            f"Cantidad: {row['cantidad']} | "
            f"Ubicación: {row['ubicacion']}"
        )


def main():
    try:
        seed_demo()
        show_demo_inventory()
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")
        return 1

    print("\nCarga de demostración completada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())