import requests

from config import OLLAMA_URL, LLM_MODEL, OLLAMA_TIMEOUT


class OllamaError(RuntimeError):
    """Error al comunicarse con Ollama."""


def validate_messages(messages):
    """Valida mensajes de conversación y resultados de herramientas."""
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages debe ser una lista no vacía.")

    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Cada mensaje debe ser un diccionario.")

        role = message.get("role")

        if role not in {"system", "user", "assistant", "tool"}:
            raise ValueError(f"Rol no válido: {role!r}")

        content = message.get("content", "")
        calls = message.get("tool_calls", [])

        if not isinstance(content, str):
            raise ValueError("El contenido debe ser texto.")

        if not isinstance(calls, list):
            raise ValueError("tool_calls debe ser una lista.")

        if calls and role != "assistant":
            raise ValueError(
                "Solo los mensajes assistant pueden contener tool_calls."
            )

        if role != "assistant" and "content" not in message:
            raise ValueError("El mensaje debe incluir content.")

        if role == "tool":
            name = message.get("tool_name")
            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    "El resultado de una herramienta requiere tool_name."
                )


def chat_message(messages, tools=None):
    """Devuelve el mensaje completo del modelo, incluidas tool_calls."""
    validate_messages(messages)

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "stream": False,
    }

    if tools is not None:
        if not isinstance(tools, list):
            raise ValueError("tools debe ser una lista.")
        payload["tools"] = tools

    try:
        with requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=(10, OLLAMA_TIMEOUT),
        ) as response:

            if not response.ok:
                try:
                    error_data = response.json()
                    detail = (
                        error_data.get("error", response.reason)
                        if isinstance(error_data, dict)
                        else response.reason
                    )
                except ValueError:
                    detail = response.reason

                raise OllamaError(
                    f"Ollama devolvió HTTP {response.status_code}: {detail}"
                )

            try:
                data = response.json()
            except ValueError as error:
                raise OllamaError(
                    "Ollama no devolvió JSON válido."
                ) from error

    except requests.exceptions.Timeout as error:
        raise OllamaError(
            "Se agotó el tiempo de espera de Ollama."
        ) from error

    except requests.exceptions.ConnectionError as error:
        raise OllamaError(
            f"No se pudo conectar con {OLLAMA_URL}."
        ) from error

    except requests.exceptions.RequestException as error:
        raise OllamaError(
            f"Error durante la petición: {error}"
        ) from error

    if not isinstance(data, dict):
        raise OllamaError("Formato de respuesta inesperado.")

    if data.get("error"):
        raise OllamaError(f"Ollama informó: {data['error']}")

    message = data.get("message")

    if not isinstance(message, dict):
        raise OllamaError("Ollama no devolvió un mensaje válido.")

    if message.get("role") != "assistant":
        raise OllamaError("Se esperaba un mensaje del asistente.")

    content = message.get("content", "")
    calls = message.get("tool_calls", [])

    if not isinstance(content, str) or not isinstance(calls, list):
        raise OllamaError("Contenido o llamadas a herramientas inválidos.")

    for call in calls:
        function = call.get("function") if isinstance(call, dict) else None

        if not isinstance(function, dict):
            raise OllamaError("Llamada a herramienta mal formada.")

        name = function.get("name")
        arguments = function.get("arguments")

        if not isinstance(name, str) or not name.strip():
            raise OllamaError("La herramienta no tiene un nombre válido.")

        if not isinstance(arguments, dict):
            raise OllamaError(
                "Los argumentos de la herramienta deben ser un objeto JSON."
            )

    if not content.strip() and not calls:
        raise OllamaError("El modelo devolvió un mensaje vacío.")

    # Conserva también los campos adicionales del mensaje.
    return message


def chat(messages):
    """Interfaz de texto utilizada por el chat general y el RAG."""
    message = chat_message(messages)

    if message.get("tool_calls"):
        raise OllamaError(
            "El modelo solicitó herramientas en una consulta de texto."
        )

    content = message.get("content", "")

    if not content.strip():
        raise OllamaError("El modelo no devolvió texto.")

    return content


def main():
    messages = [
        {
            "role": "user",
            "content": "Explica el mantenimiento preventivo en una frase.",
        }
    ]

    print(f"Modelo: {LLM_MODEL}")

    try:
        print(chat(messages))
    except OllamaError as error:
        print(f"Error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())