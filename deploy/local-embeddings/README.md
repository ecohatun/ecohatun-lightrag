# Local E5 embedding service (reference)

- Uses the previously downloaded `MintplexLabs/multilingual-e5-small` ONNX model via `@xenova/transformers@2.17.2`.
- Serves `POST /v1/embeddings/documents` (adds `passage:`) and `POST /v1/embeddings/queries` (adds `query:`). Both accept OpenAI-like JSON `{"input":["some text"]}`, require a bearer token, and return 384-element vectors.
- `GET /health` responds without authentication. Do not expose this container to the public Internet.
- `compose.example.yml` is a **template**, not the live Dokploy compose. It must be deployed from Git source (so `build: .` has access to the Dockerfile); set the build context to this directory. Do not paste it into an isolated Raw Compose deployment without source files.
- Requires Docker Compose volume `subpath` support, a named storage volume containing the model files, and a private Docker network shared with the client.
- Store `EMBEDDINGS_API_KEY`, `MODEL_VOLUME`, and `INTERNAL_DOCKER_NETWORK` only in private Dokploy environment settings.
- Do not touch the original AnythingLLM storage or remove/replace LightRAG's PostgreSQL volumes.
- **Not yet connected to LightRAG.** LightRAG's stock OpenAI embedding binding normally calls a single `/embeddings` path and does not automatically choose query vs document endpoints. The next step is a compatible LightRAG adapter or a carefully tested routing strategy; do not alter `EMBEDDING_DIM` or reprocess documents yet.
- Confirm that the ONNX model can be loaded by a read-only container and that emitted vectors contain exactly 384 finite numbers before enabling any database migration.
- Changing from the existing 1024-dimensional model requires a backed-up database schema adjustment. Existing embeddings cannot be mathematically converted from 1024 dimensions into E5 embeddings; any existing documents would need reindexing.
