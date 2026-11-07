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

### Headroom

La primera prueba de compresión explícita del 7 de noviembre de 2026 a las 11:49 UTC llegó a `/v1/compress` desde loopback y agotó la espera del cliente (20 s). Las dos consultas de inferencia y la medición de tokens quedaron pendientes. `vmstat` observado después registró entre 63 y 69 % de CPU steal en las cuatro muestras de intervalo. La causa del timeout sigue sin confirmar. El siguiente ensayo aísla SmartCrusher en modo estructural sin pérdida y conserva la ruta de inferencia del piloto.

La segunda prueba, a las 11:52 UTC, ejecutó SmartCrusher estructural sin pérdida en 307 ms. El resultado sintético pasó de 6111 a 3049 bytes (50,1 %). DeepSeek devolvió HTTP 400 al recibir una llamada de herramienta sintética sin el campo `reasoning_content` que exige en modo thinking. El ahorro en tokens del proveedor sigue pendiente. El script ahora presenta el resultado original o comprimido como contexto de usuario en ambas consultas de inferencia. Los logs también registraron el fallback de `/v1/compress` a los 30 s y un intento fallido de cargar Kompress en modo offline por falta del modelo en caché local.
