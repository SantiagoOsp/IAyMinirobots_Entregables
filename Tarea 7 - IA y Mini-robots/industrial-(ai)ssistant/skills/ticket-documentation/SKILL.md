---
name: ticket-documentation
description: Documenta de manera estructurada un trabajo, falla,
mejora o requerimiento y genera un ticket listo para implementación.
---

# Objetivo

Convertir una descripción informal de un trabajo en un ticket técnico
completo, verificable y listo para desarrollar.

# Entradas

El usuario puede proporcionar:

- descripción del problema
- equipo o sistema afectado
- comportamiento actual
- comportamiento esperado
- prioridad
- restricciones
- archivos relacionados

# Procedimiento

1. Analizar la solicitud.
2. Identificar el problema principal.
3. Separar hechos de suposiciones.
4. Identificar información faltante.
5. Determinar criterios verificables de aceptación.
6. Registrar restricciones y dependencias.
7. Generar el ticket.

# Formato de salida

## Título

Descripción breve y específica.

## Contexto

Explique dónde aparece el problema.

## Problema

Describa el comportamiento observado.

## Resultado esperado

Describa lo que debería ocurrir.

## Alcance

Indique qué debe implementarse.

## Fuera de alcance

Indique explícitamente lo que no debe modificarse.

## Criterios de aceptación

- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

## Dependencias

Liste sistemas, documentos, equipos o módulos relacionados.

## Riesgos

Liste posibles efectos adversos.

## Evidencias

Documentos, logs, fotografías o pruebas asociadas.

# Reglas

- No inventar requerimientos.
- Diferenciar información confirmada de inferencias.
- Los criterios de aceptación deben ser comprobables.
- Si falta información crítica, marcarla como pendiente.