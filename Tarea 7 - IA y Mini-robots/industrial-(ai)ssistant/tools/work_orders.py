import argparse
import json
from contextlib import closing

from database.database import get_connection


PRIORIDADES = {"BAJA", "MEDIA", "ALTA", "CRITICA"}


def validar_texto(value, nombre):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{nombre} debe contener texto.")

    return value.strip()


def crear_orden_trabajo(
    equipo_codigo,
    falla,
    solicitud_id,
    prioridad="MEDIA",
):
    """Crea una orden o recupera la de una solicitud ya procesada."""
    equipo_codigo = validar_texto(equipo_codigo, "El código del equipo")
    falla = validar_texto(falla, "La descripción de la falla")
    solicitud_id = validar_texto(solicitud_id, "El identificador de solicitud")
    prioridad = validar_texto(prioridad, "La prioridad").upper()

    if prioridad not in PRIORIDADES:
        raise ValueError(
            "La prioridad debe ser BAJA, MEDIA, ALTA o CRITICA."
        )

    with closing(get_connection()) as connection:
        with connection:
            # Serializa las escrituras antes de comprobar la solicitud.
            connection.execute("BEGIN IMMEDIATE")

            previous = connection.execute(
                """
                SELECT
                    ot.id,
                    ot.equipo_codigo,
                    ot.falla,
                    ot.prioridad
                FROM solicitudes_orden AS s
                JOIN ordenes_trabajo AS ot
                    ON ot.id = s.orden_id
                WHERE s.solicitud_id = ?
                """,
                (solicitud_id,),
            ).fetchone()

            if previous is not None:
                same_request = (
                    previous["equipo_codigo"] == equipo_codigo
                    and previous["falla"] == falla
                    and previous["prioridad"] == prioridad
                )

                if not same_request:
                    raise ValueError(
                        "El solicitud_id ya pertenece a una orden "
                        "con datos diferentes."
                    )

                orden_id = previous["id"]
                reutilizada = True

            else:
                equipo = connection.execute(
                    """
                    SELECT codigo
                    FROM equipos
                    WHERE codigo = ?
                    """,
                    (equipo_codigo,),
                ).fetchone()

                if equipo is None:
                    return {
                        "procesada": False,
                        "estado": "EQUIPO_NO_ENCONTRADO",
                        "equipo_codigo": equipo_codigo,
                        "solicitud_id": solicitud_id,
                    }

                cursor = connection.execute(
                    """
                    INSERT INTO ordenes_trabajo (
                        equipo_codigo, falla, prioridad
                    )
                    VALUES (?, ?, ?)
                    """,
                    (equipo_codigo, falla, prioridad),
                )
                orden_id = cursor.lastrowid

                connection.execute(
                    """
                    INSERT INTO historial_fallas (
                        equipo_codigo, falla, orden_trabajo
                    )
                    VALUES (?, ?, ?)
                    """,
                    (equipo_codigo, falla, orden_id),
                )

                connection.execute(
                    """
                    INSERT INTO solicitudes_orden (
                        solicitud_id, orden_id
                    )
                    VALUES (?, ?)
                    """,
                    (solicitud_id, orden_id),
                )

                reutilizada = False

            orden = connection.execute(
                """
                SELECT
                    ot.id,
                    ot.equipo_codigo,
                    e.nombre AS equipo_nombre,
                    ot.falla,
                    ot.prioridad,
                    ot.estado,
                    ot.fecha_creacion
                FROM ordenes_trabajo AS ot
                JOIN equipos AS e
                    ON e.codigo = ot.equipo_codigo
                WHERE ot.id = ?
                """,
                (orden_id,),
            ).fetchone()

            historial = connection.execute(
                """
                SELECT id
                FROM historial_fallas
                WHERE orden_trabajo = ?
                ORDER BY id
                """,
                (orden_id,),
            ).fetchall()

            if len(historial) != 1:
                raise RuntimeError(
                    "La orden no tiene exactamente un registro de falla. "
                    "Revisa la integridad del historial."
                )

            result = {
                "procesada": True,
                "creada": not reutilizada,
                "reutilizada": reutilizada,
                "solicitud_id": solicitud_id,
                "orden_id": orden["id"],
                "referencia": f"OT-{orden['id']}",
                "equipo_codigo": orden["equipo_codigo"],
                "equipo_nombre": orden["equipo_nombre"],
                "falla": orden["falla"],
                "prioridad": orden["prioridad"],
                "estado": orden["estado"],
                "fecha_creacion_utc": orden["fecha_creacion"],
                "historial_id": historial[0]["id"],
            }

        # Devuelve el resultado únicamente después del commit.
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Crea una orden con protección contra reintentos."
    )
    parser.add_argument("equipo", help="Código exacto del equipo.")
    parser.add_argument("falla", help="Descripción de la falla.")
    parser.add_argument(
        "--solicitud-id",
        required=True,
        help="Identificador único; conserva el mismo al reintentar.",
    )
    parser.add_argument(
        "--prioridad",
        type=str.upper,
        choices=sorted(PRIORIDADES),
        default="MEDIA",
    )
    args = parser.parse_args()

    try:
        result = crear_orden_trabajo(
            equipo_codigo=args.equipo,
            falla=args.falla,
            solicitud_id=args.solicitud_id,
            prioridad=args.prioridad,
        )
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["procesada"] else 1


if __name__ == "__main__":
    raise SystemExit(main())