# Taller de inteligencia artificial generativa

Este trabajo desarrolla los cinco ejercicios de la sección 7.11 del documento *Inteligencia artificial generativa*, de José J. Martínez P. (2026). Cada ejercicio se presenta en un notebook independiente que reúne la explicación conceptual, el código correspondiente, ejemplos y referencias.

El conjunto aborda cuatro formas de aplicar la IA generativa: organizar el trabajo mediante skills, responder preguntas apoyadas en documentos, interpretar solicitudes de mantenimiento y conectar un microcontrolador con un modelo de lenguaje externo. Los notebooks distinguen las definiciones, las implementaciones de ejemplo y los resultados efectivamente comprobados.

## Organización de los notebooks

| Ejercicio | Notebook | Contenido principal |
|---|---|---|
| 1 | [01_skills.ipynb](01_skills.ipynb) | Definición de cuatro skills y demostración de generación de HTML |
| 2 | [02_rag_industrial.ipynb](02_rag_industrial.ipynb) | Código de un chatbot RAG sobre manuales técnicos industriales |
| 3 | [03_chatbot_curso.ipynb](03_chatbot_curso.ipynb) | Código de un chatbot RAG sobre el material académico disponible |
| 4 | [04_agente_mantenimiento.ipynb](04_agente_mantenimiento.ipynb) | Herramientas de mantenimiento con SQLite e interpretación de solicitudes mediante LLM |
| 5 | [05_esp32_llm.ipynb](05_esp32_llm.ipynb) | Análisis de restricciones del ESP32 y simulación de una aplicación con LLM externo |

## 1. Definición de skills propios

El notebook `01_skills.ipynb` define cuatro habilidades a partir de la organización del trabajo presentada por AI Hero. La adaptación toma como referencia sus flujos de tickets, implementación y enseñanza, y establece instrucciones propias para el contexto del taller (Pocock, s. f.-a, s. f.-b, s. f.-c).

Un skill se entiende como un paquete de instrucciones y recursos que guía el comportamiento de un agente. Su archivo principal, `SKILL.md`, contiene un nombre, una descripción que indica su propósito y un procedimiento de trabajo. Esta organización proporciona contexto y reglas de actuación; no constituye entrenamiento del modelo.

### Skill para documentar tickets

`documentar-ticket` transforma una solicitud en una descripción estructurada del trabajo. Incluye problema, objetivo, alcance, exclusiones, entradas, salidas, dependencias, riesgos y criterios de aceptación. Sus instrucciones separan los datos confirmados de los supuestos y registran las dudas que impiden definir la tarea.

El ejemplo del notebook corresponde a una consulta de repuestos por código. Los criterios distinguen tres comportamientos: encontrar un repuesto existente, reconocer un código inexistente y rechazar un código vacío. De esta manera, el ticket describe resultados observables.

### Skill de implementación

`implementar-ticket` orienta la generación de código a partir de un ticket definido. Relaciona el comportamiento solicitado con pruebas de casos normales, entradas inválidas y situaciones límite. También exige registrar los comandos y resultados reales de las pruebas, diferenciando una verificación realizada de una afirmación sin evidencia.

El notebook describe un recurso de pruebas basado en `unittest`. La definición contempla una salida documental que identifica los archivos modificados, los resultados y los pendientes.

### Skill de explicación en HTML

`explicar-html` organiza una explicación del trabajo a partir del ticket, el código final y la evidencia de pruebas. Su contenido comprende el problema, el flujo de funcionamiento, las decisiones, las entradas, las salidas, un ejemplo y las limitaciones.

Además de definir sus instrucciones, el notebook implementa `render_html()`, una función que construye una página HTML a partir de un título y varias secciones. El contenido se escapa para representar las etiquetas introducidas como texto. La demostración comprobó el escape de una entrada con una etiqueta `script` y la escritura y lectura del HTML en un archivo temporal. La inspección visual en navegador no forma parte de la verificación realizada.

### Skill de captura de requerimientos

`capturar-requerimientos` establece un procedimiento para extraer requisitos de documentos y mantener su trazabilidad. Cada registro contempla un identificador, descripción, tipo, fuente y estado. Las instrucciones diferencian requisitos explícitos, inferencias y dudas, y conservan las fuentes de las contradicciones detectadas.

La relación entre las cuatro habilidades sigue una secuencia: los documentos aportan requisitos, los requisitos delimitan el ticket, el ticket guía la implementación y la evidencia final sustenta la explicación HTML. El notebook contiene las definiciones completas y la descripción de sus recursos; no registra una instalación de estos skills en una cuenta.

## 2. Chatbot RAG industrial

El notebook `02_rag_industrial.ipynb` desarrolla el código de un chatbot basado en recuperación aumentada por generación, o RAG. Su propósito es responder preguntas técnicas utilizando fragmentos de manuales como evidencia. El modelo de lenguaje recibe esa información junto con la pregunta y genera una respuesta contextualizada.

Se seleccionaron documentos oficiales correspondientes al variador ABB ACS355, al variador Omron V1000 y al PLC Siemens S7-1200. Estos documentos describen componentes presentes en sistemas industriales; no representan manuales de máquinas completas. En la entrega se descargó el manual ABB y se verificó su firma PDF. Las descargas de Omron y Siemens agotaron el tiempo de espera, por lo que el notebook conserva sus enlaces y la función de descarga.

### Procesamiento documental

La función `read_documents()` identifica archivos PDF, Markdown y TXT. Para los PDF, extrae el texto por página; para los documentos de texto, conserva su contenido como una unidad documental. El código divide el texto en fragmentos de hasta 1.200 caracteres, con un avance de 1.000 caracteres que produce un solapamiento de hasta 200 caracteres entre fragmentos consecutivos de una misma unidad.

Cada fragmento conserva el archivo de origen, la página o unidad documental, su desplazamiento y una huella SHA-256 del archivo. Estos datos relacionan el contenido recuperado con su fuente e identifican la versión de los bytes procesados.

### Representación y recuperación

La función `embed()` define la comunicación con el endpoint `/api/embed` de Ollama. El modelo de embeddings configurado es `nomic-embed-text`. Los vectores se normalizan y se almacenan con los fragmentos en un índice JSON identificado como `industrial.json`, dentro de `data/vector_db`.

La función `retrieve()` representa la pregunta con el mismo modelo y compara su vector con los del índice. El producto punto entre vectores normalizados corresponde a la similitud de coseno. Los cuatro fragmentos con mayor puntuación constituyen el contexto de la respuesta. La implementación realiza una búsqueda exhaustiva sobre el índice JSON, sin un servicio independiente de base de datos vectorial.

### Generación de respuestas

La función `answer()` construye el contexto con identificadores de fuente y define una consulta al endpoint `/api/chat`. El modelo generativo configurado es `qwen2.5:3b`. Las instrucciones del sistema solicitan respuestas en español, citas de los fragmentos y una declaración de falta de evidencia cuando corresponda (Ollama, s. f.-a, s. f.-b).

El código incorpora un umbral de similitud de 0,35 como criterio experimental de abstención. Esta puntuación expresa cercanía vectorial, no una probabilidad de que la respuesta sea correcta. También conserva un historial breve de conversación y trata los documentos como datos, en lugar de instrucciones para el agente.

El resultado de este ejercicio es la implementación del flujo de descarga, extracción, fragmentación, indexación, recuperación y consulta generativa. No se ejecutaron embeddings ni respuestas reales con Ollama en el entorno de elaboración, y no se reportan métricas de precisión del chatbot.

## 3. Chatbot sobre los documentos del curso

El notebook `03_chatbot_curso.ipynb` aplica el mismo enfoque RAG al material académico. Su fuente disponible es `7.md`, correspondiente al capítulo de inteligencia artificial generativa. El procesamiento se dirige a `data/course_documents` y el índice definido es `course.json`, separado del índice industrial.

Esta separación mantiene dos conjuntos documentales con propósitos diferentes: uno respalda consultas técnicas de componentes industriales y el otro respalda preguntas sobre los contenidos del curso. El código conserva la procedencia de los fragmentos y solicita citas en las respuestas.

El notebook incluye preguntas sobre tokens, embeddings, componentes del encoder y ejercicios de la sección 7.11. Estas preguntas representan consultas académicas relacionadas con el documento disponible. En los archivos Markdown y TXT, la indicación “página/unidad 1” corresponde al documento completo; el desplazamiento conservado en el índice identifica la posición de cada fragmento.

El ejercicio incorpora una lectura crítica del material. Señala que *Attention Is All You Need* fue publicado por Vaswani y colaboradores en 2017, mientras que el documento del curso contiene una atribución y una fecha diferentes. También precisa que un token no equivale necesariamente a una palabra (Vaswani et al., 2017).

Esta observación expone una limitación de RAG: recuperar fielmente un documento no garantiza que todas sus afirmaciones sean correctas. El notebook presenta el código del chatbot y las preguntas de consulta, sin afirmar que se ejecutó la inferencia generativa ni que se procesaron otros módulos del curso.

## 4. Agente de mantenimiento

El notebook `04_agente_mantenimiento.ipynb` desarrolla una demostración con herramientas deterministas y una función de interpretación mediante LLM. La información se organiza en una base SQLite en memoria con tablas de equipos, repuestos, compatibilidades, órdenes e historial. Los registros utilizados son ficticios.

### Búsqueda de repuestos

`buscar_repuesto()` recibe un código exacto y devuelve su código y descripción. La función rechaza entradas vacías o inválidas y diferencia un repuesto inexistente de uno registrado. Las consultas utilizan parámetros SQL, sin incorporar directamente la entrada del usuario al texto de la consulta.

### Consulta del almacén

`consultar_almacen()` comprueba la existencia del repuesto y devuelve su cantidad disponible. El ejemplo incluye un repuesto con tres unidades y otro con stock cero. Consultar la disponibilidad no reserva ni descuenta material.

### Generación de órdenes de trabajo

`generar_orden()` recibe el identificador de solicitud, equipo, falla reportada, código de repuesto y cantidad. Antes de registrar la orden, comprueba la existencia del equipo y del repuesto, la descripción de la falla, la cantidad entera positiva y la compatibilidad registrada.

La orden recibe un identificador y una fecha en UTC. Su estado es `ABIERTA` cuando el stock cubre la cantidad solicitada y `PENDIENTE_REPUESTO` cuando no la cubre. Estos estados representan disponibilidad al momento de la consulta, sin una reserva de inventario.

### Actualización del historial

La orden y el registro de falla se escriben en una misma transacción. El historial conserva el equipo, la falla reportada, la fecha y la referencia de la orden. Esta operación registra un reporte de falla; no confirma una causa raíz ni una reparación terminada.

El identificador de solicitud evita duplicados: repetir una solicitud con los mismos datos devuelve la orden existente y no genera otro registro de historial. Reutilizar el identificador con datos diferentes produce un rechazo.

### Interpretación con el modelo de lenguaje

`interpretar_solicitud()` define una consulta a Ollama para extraer un JSON con equipo, falla, código y cantidad. El catálogo sirve como referencia y las instrucciones impiden asumir códigos ausentes o diagnosticar una falla. La función `ejecutar_plan()` exige los campos previstos y conduce la propuesta hacia las herramientas validadas.

El diseño asigna al LLM la interpretación de la solicitud y al código la comprobación y escritura de datos. Corresponde a un flujo acotado, sin un ciclo autónomo abierto de decisiones.

### Resultados comprobados

Las pruebas verificaron la creación de una orden abierta, el estado pendiente por stock cero, la ausencia de duplicados al repetir una solicitud y la conservación del stock después de consultarlo. También comprobaron el rechazo de un repuesto inexistente, un equipo inexistente, una cantidad inválida y un identificador reutilizado con datos diferentes.

La interpretación real mediante Ollama no se ejecutó. La demostración tampoco se conectó a un almacén institucional ni a un sistema de mantenimiento externo. Los datos de la base en memoria permanecen durante la sesión del notebook.

## 5. Uso de un LLM en una aplicación con ESP32

El notebook `05_esp32_llm.ipynb` responde que un ESP32 puede participar en una aplicación con LLM como cliente de un servidor externo. La adquisición de datos y la lógica local quedan en el microcontrolador, mientras que el procesamiento del lenguaje se sitúa en un servidor o gateway.

El análisis utiliza como referencia la familia ESP32 clásica, cuya documentación describe hasta 240 MHz de frecuencia de CPU y 520 KB de SRAM interna. Esta memoria se comparte con el programa, comunicaciones y otros recursos; no representa memoria completamente disponible para un modelo (Espressif Systems, s. f.).

### Restricciones analizadas

| Restricción | Explicación dentro del ejercicio |
|---|---|
| Memoria | Los pesos y recursos de un LLM habitual superan ampliamente la SRAM del ESP32 clásico. |
| Capacidad de cálculo | La generación de lenguaje requiere un procesamiento muy superior al considerado para la adquisición y comunicación de sensores. |
| Conectividad y latencia | La consulta externa depende de la disponibilidad y del tiempo de respuesta de la red y del servidor. |
| Consumo energético | La comunicación inalámbrica y la frecuencia de consultas forman parte del consumo de la aplicación. |
| Seguridad | La arquitectura contempla autenticación del dispositivo y comunicación cifrada. |
| Naturaleza de la respuesta | La explicación generada por el LLM se diferencia de la lógica determinista de protección y control. |

### Estimación de almacenamiento

El notebook calcula que un modelo de mil millones de parámetros a cuatro bits requiere aproximadamente 500 MB decimales únicamente para sus pesos. La relación con 520 KiB de SRAM nominal es cercana a 939 veces. Esta estimación no incluye metadatos de cuantización, activaciones, caché de atención ni el entorno de ejecución.

La comparación sustenta la decisión de ubicar el LLM fuera del ESP32 clásico para la aplicación descrita. No establece una equivalencia entre todas las variantes de la familia ni entre un modelo TinyML y un chatbot LLM.

### Aplicación y simulación

La aplicación planteada corresponde a una maqueta que registra temperatura y envía lecturas a un gateway. El LLM produce explicaciones para el operador, mientras que la función local `process_reading()` determina el estado de la lectura y la alarma sin depender del servidor.

La simulación utiliza un umbral didáctico de 60 °C, sin atribuirle validez como límite industrial. Las pruebas comprobaron que una lectura alta mantiene la alarma local aunque el servidor no esté disponible, que una lectura normal sin conexión no genera consulta al LLM y que un valor no finito produce un estado de error de sensor.

El notebook incluye el pseudocódigo del firmware y un ejemplo del mensaje JSON entre el dispositivo y el gateway. El resultado es una explicación de arquitectura, una estimación de memoria y una simulación en Python; no se cargó firmware ni se realizaron pruebas en un ESP32 físico.

## Evidencia de la entrega

| Notebook | Resultado efectivamente obtenido |
|---|---|
| `01_skills.ipynb` | Cuatro definiciones completas de skills y pruebas de escape y escritura HTML. |
| `02_rag_industrial.ipynb` | Código del flujo RAG y manual ABB descargado; sin inferencia Ollama ejecutada. |
| `03_chatbot_curso.ipynb` | Código RAG para el documento `7.md`, preguntas de consulta y lectura crítica; sin inferencia Ollama ejecutada. |
| `04_agente_mantenimiento.ipynb` | Herramientas SQLite y pruebas de comportamiento ejecutadas; interpretación LLM definida, sin ejecución real. |
| `05_esp32_llm.ipynb` | Estimación de almacenamiento y pruebas de la simulación local; sin validación en hardware. |

Las celdas activas de demostración fueron ejecutadas sin errores. Los notebooks conservan sus salidas y distinguen las operaciones externas que no se realizaron. Las carpetas `data/manuals` y `data/course_documents` corresponden a las fuentes documentales; `data/vector_db` corresponde a los índices definidos por el código. La carpeta `data/documents` está contemplada en la estructura, sin documentos procesados en esta entrega.

## Referencias

ABB. (s. f.). *ACS355 user’s manual*. https://library.e.abb.com/public/805f31a82d524d8aa8a750011e2cd001/EN_ACS355_UM_E_A5.pdf

Espressif Systems. (s. f.). *ESP32 series datasheet*. https://documentation.espressif.com/esp32_datasheet_en.html

Martínez P., J. J. (2026, septiembre). *7. Inteligencia artificial generativa* [Material del curso].

Ollama. (s. f.-a). *Generate a chat message*. https://docs.ollama.com/api/chat

Ollama. (s. f.-b). *Generate embeddings*. https://docs.ollama.com/api/embed

Omron. (s. f.). *V1000: Guía de referencia rápida*. https://assets.omron.eu/downloads/latest/manual/es/i67e_v1000_getting_started_guide_es.pdf

Pocock, M. (s. f.-a). *The /implement Skill*. AI Hero. https://www.aihero.dev/skills-implement

Pocock, M. (s. f.-b). *The /teach Skill*. AI Hero. https://www.aihero.dev/skills-teach

Pocock, M. (s. f.-c). *The /to-tickets Skill*. AI Hero. https://www.aihero.dev/skills-to-tickets

Siemens. (s. f.). *S7-1200 system manual*. https://cache.industry.siemens.com/dl/files/241/109797241/att_1066673/v1/s71200_system_manual_en-US_en-US.pdf

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). *Attention is all you need*. https://arxiv.org/abs/1706.03762
