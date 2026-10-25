# MCP LightRAG Ecohatun: isolated test

Remote Streamable HTTP MCP endpoint: `/mcp`; local health check `/health`.
One read-only tool: `buscar_conocimiento_ecohatun(pregunta)`.
The tool can generate DeepSeek API usage through LightRAG.

Configuration: `LIGHTRAG_URL=http://lightrag-ecohatun-test:9621`,
`MCP_AUTH_TOKEN` (at least 24 characters, keep secret).

Attach test container to **both** private Docker networks:
- `dokploy-network` (OpenCode)
- `ecohatun-ligraghost-qmkoxi_lightrag-network` (LightRAG)

Never publish Docker host ports. OpenCode remote MCP URL:
`http://ecohatun-lightrag-mcp-test:8080/mcp` with header
`Authorization: Bearer {file:/path/to/protected/token}`.

Do not connect this test endpoint to customers. No write or delete tools.
