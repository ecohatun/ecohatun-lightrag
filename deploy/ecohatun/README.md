# Ecohatun - LightRAG + E5 + DeepSeek

## Estado

Configuracion experimental validada parcialmente.
No sustituir la instalacion de produccion sin pruebas y respaldo.

## Arquitectura

- LightRAG: API y motor RAG, puerto interno 9622.
- E5 multilingual: embeddings de 384 dimensiones.
- Proxy DeepSeek: intermediario autenticado con limites de consumo.

## Embeddings

Modelo: MintplexLabs/multilingual-e5-small

Configuracion:
- EMBEDDING_ASYMMETRIC=true
- EMBEDDING_QUERY_PREFIX=query:
- EMBEDDING_DOCUMENT_PREFIX=passage:

## Preparacion

1. Clonar el repositorio y seleccionar la rama desarrollo.
2. Revisar deploy/ecohatun/compose.yml.
3. Copiar .env.example a .env fuera del control de Git.
4. Configurar credenciales reales fuera del repositorio.
5. Preparar el volumen Docker con los archivos del modelo E5.
6. Crear las redes Docker externas definidas en las variables de entorno.
7. Validar Docker Compose antes de iniciar los servicios.

## Credenciales

- DEEPSEEK_KEY_FILE: archivo con la clave de DeepSeek.
- PROXY_TOKEN_FILE_HOST: archivo con el token interno del proxy.
- EMBEDDING_BINDING_API_KEY: clave de autenticacion E5.

No publicar estos valores en GitHub.

## Recursos externos

Variables configurables:
- E5_VOLUME_NAME
- RAG_INTERNAL_NETWORK
- PROXY_EGRESS_NETWORK

Los recursos deben existir previamente en Docker.
Los valores predeterminados corresponden al entorno experimental.

## Limites experimentales

- PROXY_MAX_REQUESTS=2
- PROXY_MAX_BODY=20480
- PROXY_MAX_OUTPUT_TOKENS=512

Estos limites no sustituyen controles de presupuesto y seguridad
para una instalacion de produccion.

## Comprobaciones realizadas

- E5: HTTP 200 y embeddings de 384 dimensiones.
- LightRAG: contenedor saludable.
- Embeddings asimetricos: configuracion reconocida.
- Proxy: contenedor saludable.
- Solicitudes sin autorizacion: HTTP 401.
- Solicitudes superiores al limite: HTTP 413.

## Pendiente antes de produccion

- Validar el limite HTTP 429.
- Probar consultas completas con DeepSeek.
- Revisar la gestion de secretos en Dokploy.
- Comprobar persistencia y recuperacion de datos.
- Preparar respaldos y procedimiento de migracion.
- Verificar permisos, aislamiento y acceso a las APIs.

## Seguridad

No conectar este despliegue a clientes reales hasta completar
las pruebas pendientes.

No reutilizar los volumenes de produccion durante las pruebas.

## Autenticacion de LightRAG

Configurar LIGHTRAG_API_KEY con una clave aleatoria segura.
No publicar la clave en GitHub.

Prueba realizada en LightRAG 1.5.8:
- GET /documents/status_counts sin X-API-Key: HTTP 403.
- GET /documents/status_counts con X-API-Key valida: HTTP 200.

El campo auth_mode de /health refleja la configuracion de cuentas de usuario y no demuestra por si solo si la API key protege los endpoints.

Antes de publicar la interfaz web, configurar y verificar por separado su autenticacion y el control de acceso de red.
