"""Start Headroom with separate inbound and OmniRoute credentials."""
import json
import os

upstream_key = os.environ.pop("OMNIROUTE_API_KEY")
os.environ["OPENAI_TARGET_API_HEADERS"] = json.dumps(
    {"Authorization": "Bearer " + upstream_key}
)
arguments = [
    "headroom", "proxy",
    "--host", "0.0.0.0",
    "--port", "8787",
    "--mode", "token",
    "--no-cache",
]
if os.environ.get("HEADROOM_OPTIMIZE", "0") != "1":
    arguments.append("--no-optimize")
os.execvp(arguments[0], arguments)
