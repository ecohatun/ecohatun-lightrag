import os
import runpy
from pathlib import Path

ruta = Path(
    os.environ.get(
        "DEEPSEEK_SECRET_FILE",
        "/run/secrets/deepseek_api_key"
    )
)

if not ruta.is_file():
    raise SystemExit("ERROR: CREDENCIAL_DEEPSEEK_NO_DISPONIBLE")

clave = ruta.read_text(encoding="utf-8").strip()

if not clave:
    raise SystemExit("ERROR: CREDENCIAL_DEEPSEEK_VACIA")

lector, escritor = os.pipe()

try:
    os.write(escritor, clave.encode())
finally:
    os.close(escritor)

del clave

os.environ["DEEPSEEK_KEY_FD"] = str(lector)
os.environ["ENABLE_REAL_DEEPSEEK"] = "YES"
os.environ["LLM_BINDING_HOST"] = "https://api.deepseek.com/v1"

runpy.run_path(
    os.environ.get(
        "PROXY_SCRIPT_PATH",
        "/proxy/proxy_integrado.py"
    ),
    run_name="__main__"
)
