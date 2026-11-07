# Piloto Docling en Ecohatun Smart

Estado PREPARADO. Compose para registrar como `docling-staging` en Dokploy, entorno staging. Docling Serve v1.38.2 en imagen oficial de CPU fijada por digest. Fuente de la imagen y la versión en [GitHub Packages](https://github.com/docling-project/docling-serve/pkgs/container/docling-serve-cpu).

Configurar `DOCLING_STAGING_API_KEY` en el entorno seguro de Dokploy. El Compose usa una red Docker interna y carece de puertos publicados. El servicio queda aislado durante la primera prueba de extracción. Verificar el arranque, la autenticación y los límites antes de conectar una red privada compartida con Dify piloto. Reservar el MCP Multimedia para el contrato autenticado que se valide desde Dify y OpenCode.

El presupuesto inicial es de una vCPU y 2,5 GiB de RAM como límites, con un trabajador de conversión. Cada solicitud admite un archivo, hasta 10 páginas y 10 MiB. Son valores de ensayo sujetos a resultados. El tamaño publicado de la imagen es aproximadamente 4,4 GB.

## Aceptación

- Comprobar que la API rechaza una conversión sin clave y con clave inválida.
- Procesar por `POST /v1/convert/file` un PDF con texto, un PDF escaneado y un Excel sintéticos, uno a la vez. Validar moneda, importe, cantidad y página u hoja cuando el formato la proporcione.
- Medir latencia y pico de RAM y CPU. Comparar la consulta T-200 durante OCR con su línea base en una prueba autorizada.
- Validar después la misma extracción desde una app separada del Dify piloto. Reservar la prueba SaleSmartly y MW1 para cuando el contrato del adjunto esté verificado.

Para revertir el ensayo, detener únicamente `docling-staging` desde Dokploy. Los adjuntos de prueba son sintéticos y su contenido queda fuera del índice comercial.
