
from lightrag.llm.openai import openai_complete_if_cache

def crear_llm_proxy(base_url, api_key):
    async def completar(prompt, system_prompt=None, history_messages=None, **kwargs):
        kwargs.pop("model", None)
        kwargs.pop("base_url", None)
        kwargs.pop("api_key", None)
        kwargs.pop("timeout", None)

        return await openai_complete_if_cache(
            "deepseek-chat",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages or [],
            base_url=base_url,
            api_key=api_key,
            timeout=45,
            **kwargs
        )

    return completar
