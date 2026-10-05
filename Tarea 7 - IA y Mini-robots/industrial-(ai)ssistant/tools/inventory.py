import argparse
import json
from contextlib import closing

from database.database import get_connection


def consultar_inventario(codigo):
    """Consulta cantidad y ubicación de un repuesto por código exacto."""
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("El código debe ser un texto no vacío.")

    codigo = codigo.strip()

    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT
                r.codigo,
                r.descripcion,
                i.codigo_repuesto,
                i.cantidad,
                i.ubicacion
            FROM repuestos AS r
            LEFT JOIN inventario AS i
                ON i.codigo_repuesto = r.codigo
            WHERE r.codigo = ?
            """,
            (codigo,),
        ).fetchone()

    if row is None:
        return {
            "estado": "REPUESTO_NO_ENCONTRADO",
            "codigo": codigo,
            "cantidad": None,
            "ubicacion": None,
            "mensaje": "El repuesto no existe en el catálogo.",
        }

    if row["codigo_repuesto"] is None:
        return {
            "estado": "SIN_REGISTRO_INVENTARIO",
            "codigo": row["codigo"],
            "descripcion": row["descripcion"],
            "cantidad": None,
            "ubicacion": None,
            "mensaje": "El repuesto existe, pero no tiene inventario registrado.",
        }

    cantidad = row["cantidad"]

    return {
        "estado": "CON_EXISTENCIAS" if cantidad > 0 else "AGOTADO",
        "codigo": row["codigo"],
        "descripcion": row["descripcion"],
        "cantidad": cantidad,
        "ubicacion": row["ubicacion"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Consulta las existencias de un repuesto."
    )
    parser.add_argument("codigo", help="Código exacto del repuesto.")
    args = parser.parse_args()

    try:
        result = consultar_inventario(args.codigo)
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())