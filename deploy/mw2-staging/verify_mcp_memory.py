import argparse
import concurrent.futures
import json
import os
import re
import time
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

def post(url, payload, token=None, extra_headers=None, timeout=15):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    headers.update(extra_headers or {})
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    with urlopen(request, timeout=timeout) as response:
        session = response.headers.get("Mcp-Session-Id")
        if response.status == 202:
            return {}, session
        if "text/event-stream" in response.headers.get("Content-Type", ""):
            for line in response:
                if line.startswith(b"data:"):
                    message = json.loads(line[5:])
                    if message.get("id") == payload.get("id"):
                        return message, session
            raise RuntimeError("SSE_WITHOUT_RESULT")
        return json.load(response), session

parser = argparse.ArgumentParser()
parser.add_argument("--recall-bank", help="Read a previously verified synthetic test bank")
args = parser.parse_args()
if args.recall_bank and not re.fullmatch(r"mw2-acceptance-[0-9a-f]{12}", args.recall_bank):
    parser.error("--recall-bank must name a synthetic MW2 acceptance bank")

phase = "CONFIG"
try:
    identities = {}
    for entry in os.environ["HINDSIGHT_API_TENANT_USERS"].split(","):
        name, key = entry.strip().split(":", 1)
        identities.setdefault(name, key)
    assert len(identities) == 2 and len(set(identities.values())) == 2
    assert os.environ["HINDSIGHT_API_LLM_BASE_URL"].rstrip("/") == "http://mw2-headroom-staging:8787/v1"
    print("TWO_DISTINCT_IDENTITIES_AND_HEADROOM_ROUTE", flush=True)
    if not args.recall_bank:
        phase = "E5"
        e5 = "http://compose-quantify-primary-hard-drive-dgule3-e5-large-1:8080/v1"
        assert os.environ["HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL"].rstrip("/") == e5
        embedding, _ = post(e5 + "/embeddings", {
            "model": "intfloat/multilingual-e5-large",
            "input": ["query: comprobacion sintetica de dimension MW2"],
        }, os.environ["HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY"])
        dimension = len(embedding["data"][0]["embedding"])
        print("E5_DIMENSION", dimension, flush=True)
        assert dimension == 1024
    bank = args.recall_bank or ("mw2-acceptance-" + uuid.uuid4().hex[:12])
    endpoint = "http://127.0.0.1:8888/mcp/" + bank + "/"
    initialize = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "ecohatun-mw2-acceptance", "version": "1.0"},
        },
    }
    phase = "MCP_AUTH_NEGATIVE"
    for label, token in (("ABSENT", None), ("INVALID", uuid.uuid4().hex)):
        try:
            post(endpoint, initialize, token)
        except HTTPError as error:
            print("MCP_AUTH_" + label, error.code, flush=True)
            assert error.code in (401, 403)
        else:
            raise RuntimeError("UNAUTHORIZED_MCP_ACCEPTED")

    def connect(token):
        reply, session = post(endpoint, initialize, token)
        protocol = reply["result"]["protocolVersion"]
        headers = {"MCP-Protocol-Version": protocol}
        if session:
            headers["Mcp-Session-Id"] = session
        post(endpoint, {"jsonrpc": "2.0", "method": "notifications/initialized"}, token, headers)
        return headers

    def rpc(token, headers, method, params, timeout=15):
        reply, _ = post(endpoint, {"jsonrpc": "2.0", "id": 2, "method": method, "params": params}, token, headers, timeout)
        result = reply["result"]
        if result.get("isError"):
            raise RuntimeError("MCP_TOOL_ERROR")
        return result

    cases = list(zip(identities.values(), ("AZUL-7419", "VERDE-5824"), ("Pabellon Mirlo", "Pabellon Alondra")))

    def retain(case):
        token, marker, building = case
        headers = connect(token)
        catalog = rpc(token, headers, "tools/list", {})
        assert {"sync_retain", "recall"} <= {tool["name"] for tool in catalog["tools"]}
        start = time.monotonic()
        rpc(token, headers, "tools/call", {
            "name": "sync_retain",
            "arguments": {
                "content": f"Prueba sintetica de MW2. Las piezas de sustitucion se guardan en {building}. Su identificador es {marker}.",
                "context": "prueba_sintetica_mw2",
            },
        }, timeout=45)
        return round((time.monotonic() - start) * 1000)

    if not args.recall_bank:
        phase = "MCP_RETAIN"
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            retention = list(executor.map(retain, cases))
        print("RETAIN_MS_A_B", *retention, flush=True)

    def recall(case):
        token, marker, _ = case
        start = time.monotonic()
        result = rpc(token, connect(token), "tools/call", {
            "name": "recall",
            "arguments": {
                "query": "En que edificio estan los repuestos y cual es su referencia",
                "max_tokens": 512,
                "include_chunks": True,
            },
        }, timeout=20)
        serialized = json.dumps(result, ensure_ascii=False)
        own = marker in serialized
        other = any(value in serialized for _, value, _ in cases if value != marker)
        return own, other, round((time.monotonic() - start) * 1000)

    phase = "MCP_RECALL_ISOLATION"
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        recalls = list(executor.map(recall, cases))
    for label, (own, other, elapsed) in zip(("A", "B"), recalls):
        print("IDENTITY", label, "OWN_MEMORY", own, "OTHER_MEMORY", other, "RECALL_MS", elapsed, flush=True)
    assert all(own and not other for own, other, _ in recalls)
    result = "MCP_EXISTING_MEMORY_PASS" if args.recall_bank else "MCP_MEMORY_AND_ISOLATION_PASS"
    print(result, bank, flush=True)
except Exception as error:
    print("TEST_FAILED", phase, type(error).__name__, getattr(error, "code", ""), flush=True)
    raise SystemExit(1)
