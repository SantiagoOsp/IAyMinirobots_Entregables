---
name: implementation
description: Implementa un ticket técnico mediante cambios controlados
de código y genera pruebas que verifiquen los criterios de aceptación.
---

# Objetivo

Implementar un ticket aprobado sin modificar funcionalidad fuera de alcance.

# Entradas

- ticket técnico
- código existente
- criterios de aceptación
- arquitectura del proyecto

# Procedimiento

1. Leer completamente el ticket.
2. Identificar los archivos involucrados.
3. Determinar el comportamiento actual.
4. Diseñar la modificación mínima necesaria.
5. Crear o actualizar pruebas.
6. Implementar el cambio.
7. Ejecutar las pruebas.
8. Corregir errores.
9. Verificar los criterios de aceptación.
10. Documentar los archivos modificados.

# Estrategia de pruebas

Aplicar cuando sea posible:

Red → Green → Refactor

1. Crear una prueba que falle.
2. Implementar el comportamiento.
3. Comprobar que la prueba pase.
4. Refactorizar sin romper pruebas.

# Salida

## Implementación realizada

## Archivos modificados

## Pruebas creadas

## Resultado de pruebas

## Criterios de aceptación

## Riesgos o limitaciones

# Reglas

- No modificar componentes fuera del ticket.
- No eliminar pruebas existentes para conseguir que el sistema pase.
- No ocultar errores.
- No declarar una función terminada si las pruebas fallan.