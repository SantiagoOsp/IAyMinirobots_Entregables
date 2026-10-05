# Taller de IA generativa: guía de notebooks

La entrega se organiza en **cinco notebooks Jupyter, uno por ejercicio** de la sección 7.11 del material de José J. Martínez P. (2026). Cada uno contiene la respuesta escrita, referencias al código, bibliografía y celdas de demostración cuando corresponden.

Los notebooks utilizan los módulos del proyecto; no reemplazan esos archivos. Las celdas se entregan sin ejecutar. Su estructura y sintaxis fueron revisadas, pero las consultas a Ollama y SQLite deben comprobarse en tu computador.

## Notebooks

| Ejercicio | Archivo | Contenido |
|---|---|---|
| 1. Skills propias | [01_skills.ipynb](notebooks/01_skills.ipynb) | Cuatro definiciones, reglas, ejemplo de ticket, lectura de los `SKILL.md` y registro de evidencia. |
| 2. RAG industrial | [02_rag_industrial.ipynb](notebooks/02_rag_industrial.ipynb) | Manuales, indexación, búsqueda de fragmentos y respuesta con fuentes. |
| 3. Chatbot del curso | [03_chatbot_curso.ipynb](notebooks/03_chatbot_curso.ipynb) | Consulta de documentos del curso y verificación de respuestas. |
| 4. Agente de mantenimiento | [04_agente_mantenimiento.ipynb](notebooks/04_agente_mantenimiento.ipynb) | Repuestos, inventario, creación de orden, historial y comprobación de reintentos. |
| 5. ESP32 y LLM | [05_esp32_llm.ipynb](notebooks/05_esp32_llm.ipynb) | Respuesta conceptual, restricciones, estimación de memoria y telemetría ficticia. |

Las respuestas completas están dentro de los notebooks. Este README explica cómo ejecutarlos y completar la evidencia.

## Preparación

Coloca los cinco archivos en `notebooks/`, dentro del proyecto. Conserva las carpetas `rag/`, `llm/`, `database/`, `tools/`, `agents/`, `skills/`, y los archivos `config.py` y `app.py`.

Desde la raíz y en el entorno Python de la aplicación:

```bash
python -m pip install -r requirements.txt
python -m pip install notebook ipykernel
python -m notebook
```

También puedes abrirlos en VS Code con soporte para notebooks. Selecciona el intérprete del proyecto como kernel.

Los notebooks 1–4 buscan la raíz en el directorio de trabajo y sus carpetas superiores. Si no la encuentran, configura la primera celda:

```python
PROJECT_DIR = Path(r"C:\industrial-ai-assistant")
```

Utiliza tu ruta real. Si cambias de proyecto después de importar módulos, reinicia el kernel.

Para los ejercicios 2–4, comprueba que Ollama esté disponible y que `LLM_MODEL` y `EMBEDDING_MODEL` correspondan a modelos instalados:

```bash
ollama list
```

El modelo del agente debe admitir llamadas a herramientas. Las celdas del notebook 1 solo requieren Python y tus skills; el notebook 5 utiliza la biblioteca estándar y no necesita Ollama ni hardware.

## Documentos y datos

| Ubicación | Uso |
|---|---|
| `data/manuals/` | Varios manuales oficiales en PDF. |
| `data/course_documents/` | Documentos del curso en PDF. |
| `data/documents/` | Sin función específica en la versión actual. |
| `data/vector_db/` | Índice de ChromaDB; no colocar documentos aquí. |
| `skills/<nombre>/SKILL.md` | Instrucciones de cada skill. |
| `database/industrial_ai.db` | Base SQLite configurada por defecto. |

Guardar un PDF no lo indexa automáticamente. El lector admite PDF: exporta `7.md` a ese formato; cambiar su extensión no basta.

Manuales y material del curso comparten la colección `industrial_documents_v1`. Las carpetas no aplican filtros: revisa las fuentes para detectar resultados mezclados.

## Ejecución por ejercicio

### 1. Skills

Ejecuta la configuración, la comprobación de archivos y su vista previa. Compara las definiciones propuestas con tus archivos reales y completa la tabla con una entrada, salida y revisión por skill.

La lectura comprueba disponibilidad, no ejecución. La aplicación no carga las skills automáticamente.

### 2 y 3. Chatbots documentales

1. Ejecuta la configuración y la lista de PDF.
2. Selecciona el documento, por ejemplo:

```python
PDF_PATH = PROJECT_DIR / "data" / "manuals" / "manual_bomba.pdf"
```

Para el ejercicio 3, usa `data/course_documents/`.

3. Cambia `RUN_INDEX` a `True` y ejecuta la indexación. Repite con cada manual necesario.
4. Ajusta `QUESTION`, cambia `RUN_QUERY` a `True` y ejecuta recuperación y respuesta.
5. Compara citas y afirmaciones con el PDF original y completa la tabla de verificación.

Si ya indexaste los documentos, puedes consultar sin indexarlos otra vez. La indexación modifica ChromaDB; no ejecutes indexaciones simultáneas. Las preguntas se procesan por separado y deben incluir su contexto.

### 4. Agente de mantenimiento

Usa la base de demostración y ejecuta las celdas en orden:

| Variable | Acción al activarla |
|---|---|
| `RUN_DEMO_SETUP` | Prepara la tabla de solicitudes y carga datos ficticios. |
| `RUN_READS` | Consulta directamente las herramientas SQLite. |
| `RUN_AGENT_QUERY` | Permite al modelo solicitar herramientas de consulta. |
| `RUN_WRITE` | Habilita creación de orden y comprobación posterior del reintento. |

Las variables están inicialmente en `False`. Preparación y escritura modifican la base configurada: utiliza datos de prueba. Los códigos `DEMO-` y sus compatibilidades son ficticios.

Conserva `REQUEST_ID` para reintentar la misma solicitud. El valor inicial es `notebook-ejercicio-4-001`; usa uno nuevo para una solicitud distinta. La celda final verifica el reintento directamente sobre la herramienta utilizando los argumentos ejecutados por el agente.

Si el modelo falla después de una escritura, la orden puede estar guardada. Revisa los resultados de herramientas y el historial antes de reintentar.

### 5. ESP32

Lee la respuesta y ejecuta las dos celdas: estimación de memoria de pesos y mensaje ficticio de telemetría.

La estimación no incluye toda la memoria de inferencia ni mide un modelo real. No se conecta con hardware: firmware y comunicación HTTP/MQTT son una propuesta conceptual.

## Relación con el código

| Archivos | Notebooks |
|---|---|
| `config.py`, `llm/ollama_client.py` | 2, 3 y 4 |
| Módulos `rag/`: lectura, división, embeddings, índice, recuperación y respuesta | 2 y 3 |
| `database/database.py`, `schema.sql`, `seed_demo.py`, `migrate_idempotency.py` | 4 |
| `tools/spare_parts.py`, `inventory.py`, `work_orders.py`, `failure_history.py` | 4 |
| `agents/maintenance_agent.py` | 4 |
| Cuatro archivos `skills/<nombre>/SKILL.md` | 1 |

`app.py` conserva los modos `/rag`, `/general` y `/agente`. No necesitas ejecutarla al trabajar con los notebooks: estos llaman directamente a las funciones.

## Referencia del taller

Martínez P., J. J. (2026, septiembre). *7. Inteligencia artificial generativa* [Material de curso, archivo `7.md`], sección 7.11.
