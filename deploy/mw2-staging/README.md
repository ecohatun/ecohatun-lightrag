# Piloto MW2 con Hindsight y Headroom

Estado PREPARADO. Build, despliegue, autenticación, aislamiento y ahorro pendientes de prueba.

Hindsight 1.2.0 y Headroom 0.43.1 se evalúan para memoria e inferencia de MW2.
La base API/panel FastAPI de MW2 sigue pendiente.

## Servicios

- Hindsight expone API y MCP con dos identidades autenticadas.
- PostgreSQL con pgvector guarda una base exclusiva del piloto.
- Headroom recibe una credencial propia y sustituye la cabecera de salida por la credencial de staging de OmniRoute.
- E5-Large existente recibe las solicitudes de embeddings con lote uno.
- OmniRoute debe autorizar un alias y una credencial propios para el piloto.

Headroom y la pareja Hindsight/PostgreSQL tienen Compose separados. Los puertos quedan en redes Docker.
El despliegue objetivo se administra en SMART ECOHATUN, entorno staging de Dokploy.

## Referencias fijadas

Hindsight upstream v1.2.0, commit 34a138684a899b6ec34175f7a2b633860466d289.
La extensión de claves está copiada literalmente de esa release. Su licencia y atribución se conservan en vendor.
Hindsight slim amd64 digest bb117258681a4a44289bc042185a16d2bb0b30d4a94adcd0dc799d445794f0cb.
PGVector pg17 amd64 digest 2017da03379b27508603c44e9041a082ef53ef711fed614ccd5044eaf9df6e31.
El digest de Python 3.12 y los digests de las imágenes construidas deben registrarse antes de ejecutar.

## Preparación

Completar staging.env.example mediante Dokploy o un staging.env local con permisos 600.
Conservar las claves de cada identidad por separado en el gestor de secretos.
Verificar el proveedor E5, los prefijos query/passage y los límites efectivos antes de indexar.
Crear la red ecohatun-mw2-staging una vez y comprobar que no colisiona.
Validar ambos Compose con config --quiet, construir y registrar digests.
El orden de arranque es PostgreSQL, Headroom y Hindsight.

Los modelos locales de embeddings y reranking se omiten en este piloto. Se desactiva reranking y se impide la descarga de pesos.
La disponibilidad de la imagen slim con esta configuración debe validarse en el arranque.
Headroom arranca en passthrough para verificar credenciales y respuesta estructurada. Activar HEADROOM_OPTIMIZE=1 solo para la comparación posterior.

## Aceptación

1. Verificar que E5 devuelve 1024 componentes y que el índice nuevo registra esa dimensión.
2. Comprobar API y MCP con credenciales válidas, ausentes e inválidas.
3. Guardar un recuerdo sintético con identidad A y recuperarlo por significado.
4. Repetir el mismo bank_id y consulta con identidad B y comprobar separación efectiva.
5. Reiniciar Hindsight y comprobar persistencia.
6. Verificar una extracción estructurada vía Headroom y el alias autorizado de OmniRoute.
7. Comparar los mismos casos con optimización apagada y encendida. Medir entrada/salida reportada, latencia y conservación de importes, unidades, SKU, fechas y resultados.

El indicador bank_id o una etiqueta libre no representa autorización. El backend resuelve el esquema por la credencial.
La extensión usa esquemas por identidad bajo un mismo usuario de base. Revisar permisos del rol y sus posibilidades de acceso antes de ampliar el piloto.

## Reversión

Detener los dos proyectos de staging conservando sus volúmenes. Registrar el commit y los digests.
Restaurar configuración e imágenes previas si existe un despliegue anterior del piloto.
Respaldar y ensayar la restauración del volumen PostgreSQL antes de una migración de esquema.
La sustitución de Claude-Mem requiere inventario de consumidores, migración y aceptación independientes.

## Pendientes

- Seleccionar y registrar la imagen base Python por digest.
- Crear la credencial y alias de OmniRoute de staging mediante su interfaz soportada.
- Autorizar E5 para este consumidor.
- Registrar los servicios en Dokploy staging.
- Ejecutar las pruebas y la restauración.
- Decidir entre Hindsight y AnythingLLM con los resultados.
