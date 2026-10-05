---
name: explanation
description: Analiza una implementación terminada y genera una
explicación técnica en formato HTML.
---

# Objetivo

Generar un documento HTML autocontenido que explique el trabajo
realizado de forma comprensible.

# Entradas

- ticket original
- código anterior
- código modificado
- pruebas
- resultados obtenidos

# Procedimiento

1. Leer el ticket.
2. Analizar los cambios implementados.
3. Identificar arquitectura y flujo.
4. Explicar las decisiones tomadas.
5. Explicar las pruebas.
6. Generar un archivo report.html.

# El HTML debe contener

1. Título del trabajo
2. Problema original
3. Requerimientos
4. Arquitectura
5. Implementación
6. Archivos modificados
7. Código relevante
8. Pruebas realizadas
9. Resultados
10. Limitaciones
11. Conclusiones

# Reglas

- El HTML debe abrir directamente en navegador.
- Utilizar HTML5.
- Incluir CSS dentro del propio documento.
- No depender de servicios externos.
- Usar tablas cuando mejoren la comprensión.
- Utilizar bloques <pre><code> para código.
- No inventar resultados de pruebas.