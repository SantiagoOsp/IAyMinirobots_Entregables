---
name: requirements-reader
description: Analiza documentos proporcionados por el usuario y
extrae requerimientos funcionales, no funcionales, restricciones
y criterios de aceptación.
---

# Objetivo

Convertir documentos técnicos en una especificación estructurada.

# Fuentes permitidas

- PDF
- Markdown
- TXT
- DOCX
- manuales técnicos
- especificaciones
- procedimientos

# Procedimiento

1. Identificar los documentos disponibles.
2. Leer el contenido relevante.
3. Extraer requerimientos explícitos.
4. Identificar restricciones.
5. Identificar interfaces.
6. Identificar parámetros técnicos.
7. Identificar requerimientos ambiguos.
8. Mantener trazabilidad con la fuente.

# Clasificación

FR = Functional Requirement
NFR = Non Functional Requirement
CON = Constraint
INT = Interface
SAF = Safety Requirement

# Formato de salida

| ID | Tipo | Requerimiento | Fuente | Estado |
|----|------|---------------|--------|--------|
| FR-001 | Funcional | ... | pág. X | Confirmado |

# Reglas

- No inventar requerimientos.
- Cada requerimiento debe indicar su fuente.
- Las inferencias deben marcarse como inferencias.
- Las contradicciones entre documentos deben informarse.