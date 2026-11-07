# Piloto staging: LightRAG E5-Large 1024D + bridge knowledge-mcp (Dify piloto)

Despliegue versionado (2026-11-06) de los contenedores del piloto staging que antes
se creaban con `docker run` manual. Solo staging (`ecohatun.scope=staging`);
produccion (lighost.ecohatun.com) no usa este archivo.

## Contenido

- `compose.yml` - los dos servicios, imagenes fijadas por digest, volumen de datos
  externo (`ecohatun-smart-lightrag-e5-large-piloto-data`, conserva el indice),
  redes externas `dokploy-network` y `ecohatun-dify-mcp-piloto`.
- `operate.py` - LightRAG v1.5.7 con PILOTO-422FIX: el pre-compute de embeddings de
  consulta enviaba query + keywords LL + keywords HL en un solo lote de hasta 3
  textos y el servidor E5 compartido responde 422 ("batch size 3 > maximum allowed
  batch size 1"). Ahora los envia de a uno con la misma embedding_func (mismo modelo
  E5-Large 1024D), conservando el orden de resultados. Se monta sobre
  `/app/lightrag/operate.py` (read-only). Copia original de la imagen:
  `/root/piloto-fixes/operate.py.bak-20261106-422batch`.
- `service.py` - bridge MCP con PILOTO-TIMEOUT90: `httpx.AsyncClient(timeout=90)`
  (antes 55; el bridge se rendia justo antes de que LightRAG respondiera). Se monta
  sobre `/knowledge/service.py`. Copia con 55s:
  `/root/ecohatun-knowledge-mcp-piloto/service.py.bak-20261106-55s`.
- `.env` / `mcp.env` - secretos locales (gitignored). Plantillas: `env.example`,
  `mcp.env.example`.

## Recrear el piloto desde cero

    cd /root/ecohatun-lightrag-github/deploy/ecohatun-piloto
    docker compose up -d

El volumen de datos es externo: el indice, los documentos y la cache sobreviven.

## Revertir los fixes

- 422: quitar la linea `./operate.py:/app/lightrag/operate.py:ro` del compose
  (o montar `/root/piloto-fixes/operate.py.bak-20261106-422batch`) y `docker compose up -d`.
- Timeout: en `service.py` volver `timeout=90` a `timeout=55` (o copiar
  `/root/ecohatun-knowledge-mcp-piloto/service.py.bak-20261106-55s`) y
  `docker compose up -d` (o `docker restart knowledge-mcp-piloto`).
