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

El resultado verifica embeddings, acceso MCP y aislamiento de los dos casos sintéticos. El contrato con OpenCode y la revisión de consumidores siguen pendientes antes de decidir la sustitución de Claude-Mem. La persistencia y la comparación estructural de tokens se documentan abajo.

### Headroom

La primera prueba de compresión explícita del 7 de noviembre de 2026 a las 11:49 UTC llegó a `/v1/compress` desde loopback y agotó la espera del cliente (20 s). Las dos consultas de inferencia y la medición de tokens quedaron pendientes. `vmstat` observado después registró entre 63 y 69 % de CPU steal en las cuatro muestras de intervalo. La causa del timeout sigue sin confirmar. El siguiente ensayo aísla SmartCrusher en modo estructural sin pérdida y conserva la ruta de inferencia del piloto.

La segunda prueba, a las 11:52 UTC, ejecutó SmartCrusher estructural sin pérdida en 307 ms. El resultado sintético pasó de 6111 a 3049 bytes (50,1 %). DeepSeek devolvió HTTP 400 al recibir una llamada de herramienta sintética sin el campo `reasoning_content` que exige en modo thinking. El ahorro en tokens del proveedor sigue pendiente. El script ahora presenta el resultado original o comprimido como contexto de usuario en ambas consultas de inferencia. Los logs también registraron el fallback de `/v1/compress` a los 30 s y un intento fallido de cargar Kompress en modo offline por falta del modelo en caché local.

La comparación estructural corregida pasó con el script del commit `c9a1eb066fc500ff5430024733a021ba7c334958`, por el mismo proxy de staging y el alias `ecohatun-smart-deepseek` de OmniRoute.

| Métrica | Original | Comprimido |
|---|---:|---:|
| Contexto sintético en bytes | 6111 | 3049 |
| Tokens de entrada reportados por la API | 2524 | 1242 |
| Tokens de salida reportados por la API | 104 | 139 |
| Latencia de inferencia en el cliente | 2098 ms | 1910 ms |
| T-200, 20 tubos, Manual Ecohatun p. 2 | Correcto | Correcto |

SmartCrusher sin pérdida tardó 87 ms. La diferencia de entrada fue de 1282 tokens (50,8 %). Los dos resultados compararon exactamente modelo, tubos, fuente y página. Es una sola pareja de corridas con un catálogo sintético, mediante compresión explícita antes del envío. Queda pendiente evaluar la compresión automática en el proxy, con entradas representativas de MW2 y mediciones repetidas.

### Persistencia de Hindsight tras reinicio

Banco sintético `mw2-acceptance-ac9f6ff2fa85`, consultado por MCP con el script del commit `2010109fdcdd6593057d2bbb90567c3f0ea053ed`. Se reinició únicamente Hindsight de staging el 7 de noviembre a las 11:59:32 UTC. PostgreSQL conservó su arranque de las 05:52:59 UTC y seguía saludable al verificar.

| Comprobación | Antes | Después |
|---|---|---|
| Identidad A recupera su recuerdo y ninguno de B | Sí, 1984 ms | Sí, 5118 ms |
| Identidad B recupera su recuerdo y ninguno de A | Sí, 1298 ms | Sí, 4401 ms |
| Acceso sin credencial y con credencial inválida | HTTP 401 en ambos casos | HTTP 401 en ambos casos |

El primer comando agotó su ventana de arranque y se detuvo antes de la consulta posterior. Los logs confirmaron que la API terminó de iniciar después. La comprobación posterior se ejecutó por separado, en modo de lectura, y confirmó ambos recuerdos sin volver a reiniciar ni escribir datos. Sigue pendiente el contrato con OpenCode. En los logs de PostgreSQL previos al reinicio quedaron registrados avisos de funciones SQL de mantenimiento ausentes en `public`. Su alcance sigue pendiente de revisión.
