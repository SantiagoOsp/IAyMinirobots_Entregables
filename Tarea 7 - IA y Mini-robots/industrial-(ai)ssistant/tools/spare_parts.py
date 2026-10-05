import argparse
import json
from contextlib import closing

from database.database import get_connection


def buscar_repuesto(codigo):
    """Consulta un repuesto por código exacto."""
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("El código debe ser un texto no vacío.")

    codigo = codigo.strip()

    with closing(get_connection()) as connection:
        repuesto = connection.execute(
            """
            SELECT codigo, descripcion, fabricante
            FROM repuestos
            WHERE codigo = ?
            """,
            (codigo,),
        ).fetchone()

        if repuesto is None:
            return {
                "encontrado": False,
                "codigo": codigo,
                "mensaje": "No existe un repuesto registrado con ese código.",
            }

        equipos = connection.execute(
            """
            SELECT e.codigo, e.nombre
            FROM equipos AS e
            JOIN equipos_repuestos AS er
                ON er.equipo_codigo = e.codigo
            WHERE er.repuesto_codigo = ?
            ORDER BY e.codigo
            """,
            (codigo,),
        ).fetchall()

    return {
        "encontrado": True,
        "codigo": repuesto["codigo"],
        "descripcion": repuesto["descripcion"],
        "fabricante": repuesto["fabricante"],
        "equipos_compatibles_registrados": [
            {
                "codigo": equipo["codigo"],
                "nombre": equipo["nombre"],
            }
            for equipo in equipos
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Consulta un repuesto por su código exacto."
    )
    parser.add_argument("codigo", help="Código del repuesto.")
    args = parser.parse_args()

    try:
        result = buscar_repuesto(args.codigo)
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())