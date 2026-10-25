import os
import json
import hmac
import sqlite3
import threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

import requests

BASE = Path(__file__).resolve().parent
TOKEN = Path(os.environ.get("PROXY_TOKEN_FILE", str(BASE / "proxy_access.token"))).read_text().strip()

REAL = os.getenv("ENABLE_REAL_DEEPSEEK") == "YES"

DATA_DIR = Path(os.environ.get("PROXY_DATA_DIR", "/proxy-data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB = DATA_DIR / (
    "proxy_real_counter.sqlite3"
    if REAL else "proxy_sim_counter.sqlite3"
)

MAX_REQUESTS = int(os.environ.get("PROXY_MAX_REQUESTS", "2"))
MAX_BODY = int(os.environ.get("PROXY_MAX_BODY", "20480"))
MAX_OUTPUT_TOKENS = int(os.environ.get("PROXY_MAX_OUTPUT_TOKENS", "512"))
lock = threading.Lock()

if REAL:
    host = os.environ["LLM_BINDING_HOST"].rstrip("/")
    parsed = urlparse(host)

    if (
        parsed.scheme != "https"
        or parsed.hostname != "api.deepseek.com"
        or parsed.path != "/v1"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in (None, 443)
    ):
        raise SystemExit("DESTINO_DEEPSEEK_NO_AUTORIZADO")

    credential_fd = os.getenv("DEEPSEEK_KEY_FD")
    if credential_fd:
        with os.fdopen(int(credential_fd), "r") as stream:
            API_KEY = stream.read().strip()
    else:
        import sys
        if not sys.stdin.isatty():
            API_KEY = sys.stdin.readline().strip()
        else:
            raise SystemExit("FALTA_CREDENCIAL")
    if not API_KEY:
        raise SystemExit("CREDENCIAL_VACIA")
else:
    host = ""
    API_KEY = ""

with sqlite3.connect(DB) as db:
    db.execute(
        "CREATE TABLE IF NOT EXISTS requests "
        "(id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    db.commit()

os.chmod(DB, 0o600)


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            return self.reply(404, {"error": "Ruta no permitida"})

        auth = self.headers.get("Authorization", "")
        supplied = auth[7:] if auth.startswith("Bearer ") else ""

        if not hmac.compare_digest(supplied, TOKEN):
            return self.reply(401, {"error": "No autorizado"})

        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.reply(400, {"error": "Longitud invalida"})

        if not 0 < size <= MAX_BODY:
            return self.reply(413, {"error": "Entrada fuera de limite"})

        try:
            payload = json.loads(self.rfile.read(size))
        except (ValueError, UnicodeDecodeError):
            return self.reply(400, {"error": "JSON invalido"})

        if not isinstance(payload, dict):
            return self.reply(400, {"error": "Formato invalido"})

        if not isinstance(payload.get("messages"), list):
            return self.reply(400, {"error": "Mensajes invalidos"})

        payload["model"] = "deepseek-chat"
        payload["max_tokens"] = MAX_OUTPUT_TOKENS
        payload["stream"] = False

        with lock:
            with sqlite3.connect(DB) as db:
                db.execute("BEGIN IMMEDIATE")
                count = db.execute(
                    "SELECT COUNT(*) FROM requests"
                ).fetchone()[0]

                if count >= MAX_REQUESTS:
                    db.rollback()
                    return self.reply(
                        429, {"error": "Limite experimental alcanzado"}
                    )

                db.execute("INSERT INTO requests DEFAULT VALUES")
                db.commit()
                number = count + 1

        print(
            f"SOLICITUD={number} MODO={'REAL' if REAL else 'SIMULADO'}",
            flush=True
        )

        if not REAL:
            return self.reply(200, {
                "id": f"chatcmpl-simulado-{number}",
                "object": "chat.completion",
                "created": 0,
                "model": "deepseek-chat",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Respuesta simulada"
                    },
                    "finish_reason": "stop"
                }]
            })

        try:
            response = requests.post(
                host + "/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=45,
                allow_redirects=False
            )
            return self.reply(response.status_code, response.json())
        except (requests.RequestException, ValueError):
            return self.reply(502, {"error": "Error del proveedor"})

    def log_message(self, *args):
        pass


HTTPServer(("0.0.0.0", 8769), Handler).serve_forever()
