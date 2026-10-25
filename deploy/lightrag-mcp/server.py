"""Read-only MCP adapter for the isolated Ecohatun LightRAG instance."""
import hmac
import os
from urllib.parse import urlsplit

import httpx
from mcp.server.fastmcp import FastMCP

TOKEN = os.environ["MCP_AUTH_TOKEN"]
RAG_URL = os.getenv("LIGHTRAG_URL", "http://lightrag-ecohatun-test:9621").rstrip("/")
if len(TOKEN) < 24:
    raise RuntimeError("MCP_AUTH_TOKEN must contain at least 24 characters")
parsed = urlsplit(RAG_URL)
if parsed.scheme != "http" or not parsed.hostname or parsed.username or parsed.password:
    raise RuntimeError("LIGHTRAG_URL must be an internal HTTP URL without credentials")

mcp = FastMCP(
    "lightrag-ecohatun",
    host="0.0.0.0",
    stateless_http=True,
    json_response=True,
)

@mcp.tool()
async def buscar_conocimiento_ecohatun(pregunta: str) -> str:
    """Consulta documentación técnica de Ecohatun en LightRAG; incluye referencias. Solo lectura."""
    pregunta = pregunta.strip()
    if not pregunta or len(pregunta) > 800:
        return "ERROR: la pregunta debe contener entre 1 y 800 caracteres."
    try:
        async with httpx.AsyncClient(timeout=100.0, trust_env=False) as client:
            response = await client.post(
                RAG_URL + "/query",
                json={"query": pregunta, "mode": "hybrid"},
            )
            response.raise_for_status()
            data = response.json()
        answer = data.get("response", "") if isinstance(data, dict) else ""
        if not isinstance(answer, str):
            return "ERROR: respuesta inesperada de LightRAG."
        return answer[:4500] + ("\n[Respuesta truncada]" if len(answer) > 4500 else "")
    except (httpx.HTTPError, ValueError):
        return "ERROR: LightRAG no pudo completar la consulta. Revisar logs del adaptador."

inner_app = mcp.streamable_http_app()

class ProtectedMCP:
    """Minimal ASGI Bearer guard, without streaming-incompatible HTTP middleware."""
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path == "/health":
                payload = b'{"status":"ok"}'
                await send({"type": "http.response.start", "status": 200,
                            "headers": [(b"content-type", b"application/json")]})
                await send({"type": "http.response.body", "body": payload})
                return
            headers = dict(scope.get("headers", []))
            supplied = headers.get(b"authorization", b"").decode("latin-1")
            if not hmac.compare_digest(supplied, "Bearer " + TOKEN):
                await send({"type": "http.response.start", "status": 401,
                            "headers": [(b"content-type", b"application/json")]})
                await send({"type": "http.response.body", "body": b'{"error":"unauthorized"}'})
                return
        await inner_app(scope, receive, send)

app = ProtectedMCP()
