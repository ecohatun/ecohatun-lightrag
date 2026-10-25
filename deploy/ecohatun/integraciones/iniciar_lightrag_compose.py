import os
import sys
from pathlib import Path

token_file = Path(
    os.environ.get(
        "PROXY_TOKEN_FILE",
        "/run/secrets/proxy_access_token"
    )
)

if not token_file.is_file():
    raise SystemExit("ERROR: TOKEN_INTERNO_NO_DISPONIBLE")

token = token_file.read_text(encoding="utf-8").strip()

if not token:
    raise SystemExit("ERROR: TOKEN_INTERNO_VACIO")

os.environ["LLM_BINDING_API_KEY"] = token

os.execv(
    sys.executable,
    [
        sys.executable,
        "-m",
        "lightrag.api.lightrag_server"
    ]
)
