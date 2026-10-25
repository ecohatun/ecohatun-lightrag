import asyncio
import json
import os
from pathlib import Path

from lightrag import LightRAG
from embedding_e5 import crear_embedding_e5
from llm_proxy import crear_llm_proxy

DOCUMENTO = Path(os.environ.get("OCR_DOCUMENT_PATH", "/data/documento-ocr-prueba.json"))
ALMACENAMIENTO = os.environ.get("RAG_STORAGE_DIR", "/app/rag_storage")


async def main():
    data = json.loads(DOCUMENTO.read_text(encoding="utf-8"))

    texto = (
        f"DOCUMENTO: {data['document_id']}\n"
        f"ORIGEN: {data['source']}\n"
        f"PAGINA: {data['page']}\n"
        f"ESTADO: {data['review_status']}\n\n"
        f"{data['ocr_original']}"
    )

    embedding = crear_embedding_e5(
        base_url=os.environ["EMBEDDING_BINDING_HOST"],
        api_key=os.environ["EMBEDDING_BINDING_API_KEY"],
        model=os.environ["EMBEDDING_MODEL"],
    )

    llm = crear_llm_proxy(
        base_url=os.environ["LLM_BINDING_HOST"],
        api_key=os.environ["LLM_BINDING_API_KEY"],
    )

    rag = LightRAG(
        working_dir=ALMACENAMIENTO,
        workspace="ocr_ecohatun_test",
        embedding_func=embedding,
        llm_model_func=llm,
        entity_extract_max_gleaning=0,
        llm_model_max_async=1,
        embedding_func_max_async=1,
        max_parallel_insert=1,
    )

    await rag.initialize_storages()

    try:
        await rag.ainsert(
            texto,
            ids=[data["document_id"]],
            file_paths=[f"{data['source']}/pagina_{data['page']}"],
        )
        print("INDEXACION_FINALIZADA")
    finally:
        await rag.finalize_storages()


if __name__ == "__main__":
    asyncio.run(main())
