"""Compare explicit Headroom compression against the staging passthrough."""
import json
import os
import re
import time
import urllib.error
import urllib.request


BASE = "http://127.0.0.1:8787"
MODEL = "ecohatun-smart-deepseek"
EXPECTED = {
    "modelo": "T-200",
    "tubos": 20,
    "pagina": 2,
    "fuente": "Manual Termas Solares Ecohatun",
}


def post(path, payload, timeout):
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload, ensure_ascii=False).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["HEADROOM_PROXY_TOKEN"],
        },
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.load(response)
    except (urllib.error.URLError, TimeoutError) as error:
        status = error.code if isinstance(error, urllib.error.HTTPError) else type(error).__name__
        raise SystemExit(f"HTTP_FAILURE {path} {status}") from None
    return result, round(1000 * (time.monotonic() - started))


def fixture():
    rows = [
        {"modelo": f"SIM-{number:03d}", "tubos": 30 + number,
         "pagina": 40 + number, "fuente": "Catálogo sintético de ensayo"}
        for number in range(64)
    ]
    rows.insert(len(rows) // 2, EXPECTED)
    return [
        {"role": "system", "content": "Responde solo con un objeto JSON con las claves modelo, tubos, pagina y fuente. Usa exclusivamente el registro del modelo pedido en el resultado de herramienta."},
        {"role": "user", "content": "¿Cuántos tubos tiene la terma T-200? Cita el manual y la página."},
        {"role": "assistant", "content": None, "tool_calls": [{
            "id": "call_catalogo", "type": "function",
            "function": {"name": "consultar_catalogo", "arguments": "{}"},
        }]},
        {"role": "tool", "tool_call_id": "call_catalogo",
         "content": json.dumps(rows, ensure_ascii=False)},
    ]


def inference(label, messages):
    result, elapsed = post("/v1/chat/completions", {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
        "max_tokens": 384,
    }, 24)
    usage = result.get("usage") or {}
    try:
        content = result["choices"][0]["message"]["content"].strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", content, re.S)
        facts_ok = json.loads(fenced.group(1) if fenced else content) == EXPECTED
    except (KeyError, IndexError, AttributeError, TypeError, ValueError):
        facts_ok = False
    prompt_tokens = usage.get("prompt_tokens")
    print(label, "PROMPT_TOKENS", prompt_tokens, "COMPLETION_TOKENS",
          usage.get("completion_tokens"), "FACTS_OK", facts_ok, "MS", elapsed, flush=True)
    return prompt_tokens, facts_ok


def main():
    if os.environ.get("HEADROOM_OPTIMIZE", "0") != "0":
        raise SystemExit("ABORT_PROXY_OPTIMIZATION_ENABLED")
    messages = fixture()
    compressed, elapsed = post("/v1/compress", {
        "model": MODEL,
        "messages": messages,
        "config": {"mode": "lossy_inline", "protect_recent": 0, "target_ratio": 0.5},
    }, 20)
    candidate = compressed.get("messages")
    print("COMPRESS", "BEFORE_ESTIMATE", compressed.get("tokens_before"),
          "AFTER_ESTIMATE", compressed.get("tokens_after"), "MS", elapsed, flush=True)
    if not isinstance(candidate, list) or candidate == messages:
        raise SystemExit("NO_COMPRESSION_APPLIED")
    matching_tool = [
        message for message in candidate
        if message.get("role") == "tool" and message.get("tool_call_id") == "call_catalogo"
    ]
    if len(matching_tool) != 1:
        raise SystemExit("ABORT_TOOL_MESSAGE_CHANGED")
    content = matching_tool[0].get("content") or ""
    if not all(str(value) in content for value in EXPECTED.values()):
        raise SystemExit("ABORT_EXPECTED_FIELDS_MISSING")
    before, original_ok = inference("ORIGINAL", messages)
    after, compressed_ok = inference("COMPRESSED", candidate)
    if not original_ok or not compressed_ok:
        raise SystemExit("FACTS_CHECK_FAILED")
    if type(before) is not int or type(after) is not int or before <= 0 or after <= 0:
        raise SystemExit("PROVIDER_USAGE_MISSING")
    print("PROMPT_TOKENS_SAVED", before - after,
          "SAVED_PERCENT", round(100 * (before - after) / before, 1), flush=True)
    if after >= before:
        raise SystemExit("NO_PROVIDER_TOKEN_SAVINGS")
    print("HEADROOM_AB_PASS", flush=True)


if __name__ == "__main__":
    main()
