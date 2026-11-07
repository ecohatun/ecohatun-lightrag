# Evidencia de pruebas - Promoción producción Ecohatun Smart (2026-11-07, UTC)

Versiones: Dify 1.18.0; LightRAG imagen ghcr.io/hkuds/lightrag@sha256:5bdbd524931b...
(digests completos en REGISTRY.md, VPS /root/prod-promotion-20261107-0300UTC/).
Criterio T-200: 20 tubos, cita exclusiva al Manual p.2, sin 422, sin aviso de vectores faltantes, sin caché.

## T-200 restringida (antes de abrir dominio)
- Fecha: 2026-11-07 03:27 UTC. Entrada: workflow "Prueba LightRAG T-200" vía 127.0.0.1:18082/v1/workflows/run.
- Resultado esperado: respuesta correcta citando solo Manual p.2.
- Evidencia: run 4d7ca395-3003-40da-8b87-a2b0bdae84e1, succeeded, 8.52s. Respuesta: "T-200 tiene
  20 tubos al vacío" + cita [1] Manual Termas Solares Ecohatun.pdf (p. 2). Sin 422, sin avisos.
- Límite: consulta única, sin concurrencia; no mide carga.

## T-200 final por dominio (https://dify.ecohatun.com)
- Fecha: 2026-11-07 03:29 UTC. Entrada: mismo workflow por el dominio público con TLS.
- Evidencia: run 228b38a1-7b1b-43b7-af5a-1574f13e210b, succeeded, 6.40s, misma respuesta correcta.
- Límite: igual que la restringida.

## Credencial inválida / sin credencial (transversal)
- knowledge.ecohatun.com/mcp sin token -> 401 (2026-11-07 03:32 UTC).
- knowledge-mcp-prod con token inválido -> 403 (03:0x UTC, fase restringida).
- lightrag.ecohatun.com sin API key -> 403 en endpoints de API (03:0x UTC, fase restringida).
- Proveedor MCP en Dify apunta a red interna; el proxy SSRF solo admite el host knowledge-mcp-prod.

## Restauración (transversal)
- Ensayo real: el volumen prod ecohatun-smart-lightrag-e5-large-prod-data se sembró extrayendo
  validated-index-20261107-0300UTC.tar.gz (respaldo consistente: docker pause -> tar -> unpause;
  pausa atómica <2s sobre ~6.5MB, proceso congelado = sin escrituras durante el tar; no había
  ingesta activa). Verificación: 6 docs, 15 fragmentos con vectores, 254 nodos, 357 aristas,
  caché LLM vacía; T-200 respondió correctamente sobre ese volumen.

## Exposición por dominio
- dify.ecohatun.com: consola Dify (login admin requerido) + API /v1 con API key de la app.
- lightrag.ecohatun.com: API LightRAG con LIGHTRAG_API_KEY requerida (403 sin/con mala clave).
- knowledge.ecohatun.com: MCP con Bearer token propio (401 sin token, 403 con token inválido).
- omniroute.ecohatun.com: histórico, SIN ruta en Traefik (404 verificado 2026-11-07 03:32 UTC); no reutilizado.
