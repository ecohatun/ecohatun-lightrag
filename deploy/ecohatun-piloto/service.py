import hmac
import os

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import PlainTextResponse

mcp = FastMCP("Ecohatun Knowledge Staging", stateless_http=True, json_response=True,
    transport_security=TransportSecuritySettings(allowed_hosts=["knowledge-mcp-piloto:8080"]))

@mcp.tool()
async def buscar_conocimiento_ecohatun(pregunta: str) -> dict:
    """Consulta el conocimiento de Ecohatun y devuelve respuesta y referencias."""
    pregunta = pregunta.strip()
    if not 1 <= len(pregunta) <= 1000:
        raise ValueError("Longitud de pregunta inválida")
    async with httpx.AsyncClient(timeout=90, trust_env=False) as client:
        result = await client.post(
            "http://ecohatun-smart-lightrag-e5-large-piloto:9621/query",
            headers={"X-API-Key": os.environ["LIGHTRAG_API_KEY"]},
            json={"query": pregunta, "mode": "mix", "include_references": True},
        )
        result.raise_for_status()
    data = result.json()
    return {"respuesta": data["response"], "referencias": data["references"]}

service = mcp.streamable_http_app()
auth = ("Bearer " + os.environ["MCP_AUTH_TOKEN"]).encode()

async def app(scope, receive, send):
    if scope["type"] == "http":
        value = dict(scope["headers"]).get(b"authorization", b"")
        if not hmac.compare_digest(value, auth):
            await PlainTextResponse("Unauthorized", status_code=401)(scope, receive, send)
            return
    await service(scope, receive, send)
