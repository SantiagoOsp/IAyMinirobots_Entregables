import sqlite3
from pathlib import Path

from agents.maintenance_agent import run_agent

from database.database import initialize_database
from llm.ollama_client import chat
from rag.rag_chat import answer_question


GENERAL_PROMPT = """
Eres un asistente especializado en mantenimiento industrial.
Responde en español de manera clara y concisa.

Diferencia hechos, hipótesis y recomendaciones.
Si faltan datos para evaluar una falla, solicita esos datos.
No inventes especificaciones técnicas ni referencias.
En este modo no tienes acceso a documentos ni herramientas.
No afirmes haber consultado inventario, creado órdenes
o realizado acciones sobre equipos.
""".strip()


def create_history():
    """Crea el historial del modo general."""
    return [
        {
            "role": "system",
            "content": GENERAL_PROMPT,
        }
    ]


def show_help():
    print(
        "\nComandos:\n"
        "/rag      Consultar documentos indexados.\n"
        "/general  Conversar sin consulta documental.\n"
        "/agente   Consultar repuestos, inventario e historial.\n"
        "/nuevo    Reiniciar el historial del modo general.\n"
        "/ayuda    Mostrar los comandos.\n"
        "/salir    Terminar."
    )


def show_sources(sources):
    """Muestra la procedencia de los fragmentos enviados al modelo."""
    if not sources:
        return

    print("\nFragmentos enviados al modelo:")

    for source in sources:
        filename = Path(source["source"]).name

        print(
            f"[{source['reference']}] {filename} | "
            f"página física {source['page']} | "
            f"fragmento {source['chunk_index'] + 1}"
        )


def main():
    try:
        initialize_database()
    except (OSError, sqlite3.Error) as error:
        print(f"No se pudo inicializar SQLite: {error}")
        return 1

    mode = "rag"
    history = create_history()

    print("\nINDUSTRIAL AI ASSISTANT")
    print("Modo inicial: documental.")
    print("Las preguntas documentales se consultan por separado.")
    show_help()

    while True:
        try:
            user_input = input(f"\nUsuario [{mode}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSistema finalizado.")
            return 0

        if not user_input:
            continue

        command = user_input.lower()

        if command in {"/salir", "salir", "exit", "quit"}:
            print("Sistema finalizado.")
            return 0

        if command == "/ayuda":
            show_help()
            continue

        if command == "/rag":
            mode = "rag"
            print("Modo documental activado.")
            continue

        if command == "/general":
            mode = "general"
            print("Modo general activado, sin consulta documental.")
            continue

        if command == "/agente":
            mode = "agente"
            print("Agente activado en modo de consultas.")
            continue

        if command == "/nuevo":
            history = create_history()
            print("Historial del modo general reiniciado.")
            continue

        if command.startswith("/"):
            print("Comando desconocido. Escribe /ayuda.")
            continue

        try:
            if mode == "rag":
                print("\nBuscando documentos y consultando el modelo...")

                result = answer_question(
                    user_input,
                    top_k=3,
                )

                print(f"\nAsistente: {result['answer']}")
                show_sources(result["sources"])

            elif mode == "agente":
                print("\nConsultando herramientas...")

                result = run_agent(user_input)

                print(f"\nAsistente: {result['answer']}")

            else:
                user_message = {
                    "role": "user",
                    "content": user_input,
                }

                pending_messages = history + [user_message]

                print("\nConsultando el modelo...")
                answer = chat(pending_messages)

                # Guarda el turno solamente si la consulta funciona.
                history.extend(
                    [
                        user_message,
                        {
                            "role": "assistant",
                            "content": answer,
                        },
                    ]
                )

                print(f"\nAsistente: {answer}")

        except KeyboardInterrupt:
            print("\nConsulta interrumpida. Sistema finalizado.")
            return 0

        except Exception as error:
            # Gestiona errores de Ollama y Chroma en la interfaz.
            print(f"\nError: {type(error).__name__}: {error}")
            print("La consulta no se completó. Puedes reintentarlo.")


if __name__ == "__main__":
    raise SystemExit(main())