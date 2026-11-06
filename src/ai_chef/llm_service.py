"""
llm_service.py
Görsel modelden gelen malzeme listesini alıp merkezi CONFIG'deki
Persona, Amaç, Bağlam ve Görev (Goal/Context/Task) yapısıyla Türkçe tarif üreten LLM modülü.
"""

from typing import Generator
from app import CONFIG, get_ollama_client


def stream_recipe(
    ingredients: list[str],
    extra_notes: str = "",
) -> Generator[str, None, None]:
    """
    Malzeme listesini kısa İngilizce prompt ile LLM'e gönderir ve
    Türkçe yemek tariflerini akıcı (streaming) olarak döndürür.
    """
    client = get_ollama_client()
    user_prompt = (
        f"Fridge ingredients: {', '.join(ingredients)}.\n"
        f"User preference: {extra_notes.strip() or 'None'}.\n"
        "Write the 2 recipes in Turkish."
    )

    stream = client.chat(
        model=CONFIG["LLM_MODEL"],
        messages=[
            {"role": "system", "content": CONFIG["LLM_SYSTEM_PROMPT"]},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": CONFIG["LLM_TEMPERATURE"]},
        keep_alive=CONFIG["KEEP_ALIVE"],
        stream=True,
    )

    for chunk in stream:
        if chunk.message.content:
            yield chunk.message.content