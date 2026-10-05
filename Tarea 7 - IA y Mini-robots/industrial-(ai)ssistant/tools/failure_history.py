import argparse
import json
from contextlib import closing

from database.database import get_connection


def consultar_historial(equipo_codigo, limite=10):
    """Devuelve las fallas más recientes de un equipo registrado."""
    if not isinstance(equipo_codigo, str) or not equipo_codigo.strip():
        raise ValueError("El código del equipo debe contener texto.")

    if type(limite) is not int or not 1 <= limite <= 100:
        raise ValueError("El límite debe ser un entero entre 1 y 100.")

    equipo_codigo = equipo_codigo.strip()

    with closing(get_connection()) as connection:
        equipo = connection.execute(
            """
            SELECT codigo, nombre
            FROM equipos
            WHERE codigo = ?
            """,
            (equipo_codigo,),
        ).fetchone()

        if equipo is None:
            return {
                "estado": "EQUIPO_NO_ENCONTRADO",
                "equipo_codigo": equipo_codigo,
                "registros": [],
            }

        rows = connection.execute(
            """
            SELECT
                h.id AS historial_id,
                h.falla,
                h.fecha,
                h.orden_trabajo AS orden_id,
                ot.prioridad,
                ot.estado AS estado_orden
            FROM historial_fallas AS h
            LEFT JOIN ordenes_trabajo AS ot
                ON ot.id = h.orden_trabajo
                AND ot.equipo_codigo = h.equipo_codigo
            WHERE h.equipo_codigo = ?
            ORDER BY h.fecha DESC, h.id DESC
            LIMIT ?
            """,
            (equipo_codigo, limite),
        ).fetchall()

    registros = [
        {
            "historial_id": row["historial_id"],
            "falla": row["falla"],
            "fecha_utc": row["fecha"],
            "orden_id": row["orden_id"],
            "referencia_orden": (
                f"OT-{row['orden_id']}"
                if row["orden_id"] is not None
                else None
            ),
            "prioridad": row["prioridad"],
            "estado_orden": row["estado_orden"],
        }
        for row in rows
    ]

    return {
        "estado": "CON_REGISTROS" if registros else "SIN_REGISTROS",
        "equipo_codigo": equipo["codigo"],
        "equipo_nombre": equipo["nombre"],
        "cantidad_devuelta": len(registros),
        "limite": limite,
        "registros": registros,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Consulta el historial de fallas de un equipo."
    )
    parser.add_argument("equipo", help="Código exacto del equipo.")
    parser.add_argument("--limite", type=int, default=10)
    args = parser.parse_args()

    try:
        result = consultar_historial(
            args.equipo,
            limite=args.limite,
        )
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())