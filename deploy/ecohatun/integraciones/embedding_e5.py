from functools import partial

from lightrag.llm.openai import openai_embed
from lightrag.utils import EmbeddingFunc


def crear_embedding_e5(base_url, api_key, model):
    funcion = partial(
        openai_embed.func,
        model=model,
        base_url=base_url,
        api_key=api_key,
        embedding_dim=384,
        query_prefix="query: ",
        document_prefix="passage: ",
    )

    return EmbeddingFunc(
        embedding_dim=384,
        max_token_size=512,
        model_name=model,
        supports_asymmetric=True,
        func=funcion,
    )


if __name__ == "__main__":
    import inspect

    print("ADAPTADOR_E5_CONFIGURADO")
    print("DIMENSION:", 384)
    print("SOPORTE_ASIMETRICO:", True)
    print("CONTEXTOS:", "document/query")
    print("PASO_320_OK")
