import http from "node:http";
import { pipeline, env } from "@xenova/transformers";

const host = process.env.HOST || "0.0.0.0";
const port = Number(process.env.PORT || 8080);
const model = process.env.MODEL_ID || "MintplexLabs/multilingual-e5-small";
const modelRoot = process.env.MODEL_ROOT || "/models";
const secret = process.env.EMBEDDINGS_API_KEY || "";
if (!secret || secret.length < 24) throw new Error("EMBEDDINGS_API_KEY must be set (at least 24 characters)");
env.allowRemoteModels = false;
env.localModelPath = modelRoot.endsWith("/") ? modelRoot : modelRoot + "/";
env.useBrowserCache = false;
const extractor = await pipeline("feature-extraction", model, { quantized: true });

function send(res, code, body) {
  res.writeHead(code, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" });
  res.end(JSON.stringify(body));
}
function auth(req) {
  const authorization = req.headers.authorization || "";
  return authorization.startsWith("Bearer ") && authorization.slice(7) === secret;
}
async function body(req) {
  let text = "";
  for await (const chunk of req) {
    text += chunk.toString("utf8");
    if (text.length > 512_000) throw new Error("request too large");
  }
  return JSON.parse(text);
}
http.createServer(async (req,res) => {
  try {
    if (req.url === "/health" && req.method === "GET") return send(res, 200, { status: "healthy", model });
    if (req.method !== "POST" || !["/v1/embeddings/documents","/v1/embeddings/queries"].includes(req.url)) return send(res, 404, { error: "not found" });
    if (!auth(req)) return send(res, 401, { error: "unauthorized" });
    const payload = await body(req);
    const arr = typeof payload.input === "string" ? [payload.input] : payload.input;
    if (!Array.isArray(arr) || !arr.length || arr.length > 32 || arr.some(s => typeof s !== "string" || s.length > 20000)) return send(res, 400, { error: "input must be 1-32 strings (max 20000 characters each)" });
    const prefix = req.url.endsWith("/queries") ? "query: " : "passage: ";
    const items = [];
    for (let i=0;i<arr.length;i++) {
      const input = arr[i].replace(/^(query|passage):\s*/i, "");
      const vector = await extractor(prefix + input, { pooling: "mean", normalize: true });
      const embedding = Array.from(vector.data);
      if (embedding.length !== 384) throw new Error("Unexpected embedding dimension: " + embedding.length);
      items.push({ object:"embedding", index:i, embedding });
    }
    return send(res, 200, { object:"list", data:items, model, usage:{ prompt_tokens:0, total_tokens:0 }});
  } catch (err) {
    console.error("embedding error:", err.message);
    return send(res, 500, { error:"embedding request failed" });
  }
}).listen(port, host, () => console.log(`local embedding service listening on ${host}:${port}`));
