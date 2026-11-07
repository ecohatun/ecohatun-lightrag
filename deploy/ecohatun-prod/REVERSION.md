# Reversión - Promoción a producción Ecohatun Smart (2026-11-07)

Alcance: servicios de producción desplegados en el proyecto Dokploy "Ecohatun Smart" > production.
El piloto NO se toca en ningún paso de esta reversión (salvo referencia al fix agent_backend, ver §5).
Ninguna credencial aparece en este documento: solo referencias (vault / archivos 0600 en el VPS).

## 1. Revertir rutas (dominios)
En el panel Dokploy (o tRPC domain.delete), borrar los dominios:
- dify.ecohatun.com     (domainId YRbUQ9yQTfQ72_mUoKiX4, compose dify-prod / nginx:80)
- lightrag.ecohatun.com (domainId THPu9bP8WBHWYFDU6iHyU, compose lightrag-prod / lightrag:9621)
- knowledge.ecohatun.com(domainId BYb9EnCUb2JdtHZDtGuBI, compose knowledge-mcp-prod / knowledge-mcp:8080)
Traefik deja de enrutar de inmediato; los contenedores siguen corriendo solo en red interna.
Los registros DNS A en Cloudflare (zona ca1ba8f5ca253434dd878b932bffaabd, DNS-only) pueden
eliminarse o dejarse sin efecto; eliminarlos NO restaura el piloto.

## 2. Revertir configuración (servicios Dokploy)
Proyecto "Ecohatun Smart" (id 1YosGHCZzSNVOPtQqals_), entorno production (id tz1Mh0SJWTsXEmVYh_e6u):
1. compose.stop y luego compose.delete de:
   - dify-prod           (composeId UOnheWADcnVWchYpPupVJ, appName ecohatun-dify-prod-wcvsja)
   - knowledge-mcp-prod  (composeId zYfqgAtiFu3-g1MYKHKdK, appName ecohatun-knowledge-mcp-prod-eysay0)
   - lightrag-prod       (composeId aYmXnQAyV4OFNN-eAfiFe, appName ecohatun-lightrag-prod-vzbbid)
2. Esto baja los contenedores y los retira del panel. Las variables vivían en Environment de
   cada servicio (borradas con el servicio); las copias 0600 en el VPS se eliminan en §3.

## 3. Revertir datos
- Volumen del índice LightRAG prod: docker volume rm ecohatun-smart-lightrag-e5-large-prod-data
  (solo existe en prod; el índice canónico vive en el piloto y en el respaldo de referencia).
- Stack Dify prod: rm -rf /root/ecohatun-dify-prod (configs + volumes locales del stack).
- Archivos de configuración prod: rm -rf /root/ecohatun-lightrag-github/deploy/ecohatun-prod
  (la versión en git queda como registro; ver tag/commit abajo).
- Credenciales efímeras de despliegue ya borradas; credenciales persistentes SOLO en el vault
  del usuario (ítems "Dify producción (dify.ecohatun.com)", "Dify producción T-200 API key",
  "OmniRoute admin (Ecohatun Smart)") y /etc/dokploy/secrets/lightrag-prod.env (0600).
- Clave OmniRoute prod: revocar en el panel OmniRoute la key "lightrag-e5-large-prod"
  (id 7ef08582-b524-4f4c-91bd-0b8622c817a6, restringida al combo ecohatun-smart-deepseek).

## 4. Restaurar el índice validado (si se reconstruye prod)
Respaldo de referencia oficial: /root/prod-promotion-20261107-0300UTC/validated-index-20261107-0300UTC.tar.gz
(6 documentos del Manual, 15 fragmentos con vectores, 254 nodos / 357 aristas).
Método documentado: docker pause <contenedor LightRAG> → tar del directorio de datos → docker unpause.
Restauración (ya ensayada el 2026-11-07 al sembrar prod): crear volumen vacío, extraer el tar en su
raíz, vaciar la caché LLM, arrancar el servicio y validar con la consulta T-200 (debe responder
"20 tubos" citando exclusivamente el Manual p.2).

## 5. Piloto (referencia, no reversión)
El piloto siguió corriendo durante toda la promoción y permanece intacto.
Único cambio autorizado sobre él (2026-11-07 03:10 UTC): clave DIFY_AGENT_SERVER_SECRET_KEY
coherente en los 7 componentes de staging; config anterior en
/tmp/ecohatun-dify-config.SkQseEgl/src/docker/.env.bak-20261107-agentkey para rollback puntual.

## Referencias de versiones
- Tag: piloto-validado-2026-11-07 (commit validado del piloto).
- Commit de configuración prod: ver git log de deploy/ecohatun-prod/ (commit de cierre 2026-11-07).
- Imágenes fijadas por digest: REGISTRY.md en /root/prod-promotion-20261107-0300UTC/ (VPS).
