# Pruebas del piloto MW2

## 7 de noviembre de 2026

Prueba ejecutada por MCP en Hindsight staging con el script versionado en `cf58c824c61b62c48a8b267e9339ad5649bead66`. Banco sintético `mw2-acceptance-ac9f6ff2fa85`.

| Comprobación | Resultado |
|---|---|
| LightRAG producción → E5-Large | HTTP 200, 1024 dimensiones, 1082 ms |
| Hindsight staging → E5-Large | 1024 dimensiones |
| MCP sin credencial | HTTP 401 |
| MCP con credencial inválida | HTTP 401 |
| Guardado A / B | 34912 / 36793 ms |
| Recuperación A / B | 3491 / 3573 ms |
| A y B recuperan su propio recuerdo | Sí, en ambas identidades |
| A y B recuperan el recuerdo de la otra identidad | Ninguna coincidencia |

La primera ejecución agotó el tiempo de espera contra E5-Large. El problema se reprodujo desde Hindsight, LightRAG y el propio contenedor E5. E5 volvió a saludable tras el reinicio autorizado y su calentamiento. La prueba posterior confirmó la generación de embeddings desde producción.

El resultado verifica embeddings, acceso MCP y aislamiento de los dos casos sintéticos. Quedan pendientes una prueba de persistencia tras reiniciar Hindsight, el contrato con OpenCode, una comparación de tokens con y sin compresión y la revisión de consumidores antes de decidir la sustitución de Claude-Mem.
