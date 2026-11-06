from pydantic import BaseModel, Field
from app import CONFIG, get_ollama_client


class FridgeInventory(BaseModel):
    ingredients: list[str] = Field(description="Fotoğrafta görünen yiyecekler, Türkçe isimlerle.")


def extract_ingredients_from_image(image_bytes: bytes) -> FridgeInventory:
    """Fotoğraftaki malzemeleri Ollama structured outputs ile çıkarır."""
    response = get_ollama_client().chat(
        model=CONFIG["VISION_MODEL"],
        messages=[{
            "role": "user",
            "content": CONFIG["VISION_PROMPT"],
            "images": [image_bytes],
        }],
        format=FridgeInventory.model_json_schema(),
        options={"temperature": CONFIG["VISION_TEMPERATURE"]},
        keep_alive=CONFIG["KEEP_ALIVE"],
    )
    return FridgeInventory.model_validate_json(response.message.content)
