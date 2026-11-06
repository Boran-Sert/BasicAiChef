"""
app.py
Tek merkezli konfigürasyon (CONFIG), ortak Ollama istemcisi ve Streamlit arayüzü.
Diğer tüm modüller (vision_service, llm_service) ayarları doğrudan buradan çeker.

Çalıştırmak için:
    streamlit run app.py
"""

import sys
from typing import Any
import ollama
import streamlit as st

# =====================================================================
#   KONFİGÜRASYON 
# =====================================================================
CONFIG: dict[str, Any] = {
    "OLLAMA_HOST": "http://localhost:11434",
    "KEEP_ALIVE": "5m",

    "VISION_MODEL": "gemma3:4b",
    "VISION_TEMPERATURE": 0.0,
    "VISION_PROMPT": (
        "List the food items and ingredients you can clearly see in this photo. "
        "Do not guess. Write each name once."
    ),

    "LLM_MODEL": "gemma3:4b",
    "LLM_TEMPERATURE": 0.4,
    "LLM_SYSTEM_PROMPT": (
        "Persona: Practical Turkish home chef.\n"
        "Goal: Prevent food waste by creating delicious, easy home meals.\n"
        "Context: The user provides available fridge ingredients. "
        "Assume only basic pantry staples (water, oil, salt, black pepper, spices) are also available.\n"
        "Task: Suggest 2 practical recipes using ONLY ingredients user provided nothing else. "
        "Include Dish Name, Prep Time, Ingredients, and Step-by-Step Instructions. "
        "Respond strictly in Turkish."
    ),
}


def get_ollama_client() -> ollama.Client:
    """Tüm servislerin ortak kullandığı tekil Ollama istemcisini döndürür."""
    return ollama.Client(host=CONFIG["OLLAMA_HOST"])


sys.modules.setdefault("app", sys.modules[__name__])

from vision_service import extract_ingredients_from_image  
from llm_service import stream_recipe  


def main() -> None:
    st.set_page_config(page_title="Akıllı Buzdolabı Şefi", page_icon="🧑‍🍳", layout="centered")
    st.session_state.setdefault("ingredients", [])
    st.session_state.setdefault("raw_json", "")

    st.title("🧑‍🍳 Buzdolabı Fotoğrafından Yemek Tarifi")
    st.caption("Ollama Structured Outputs (JSON Schema) + Küçük LLM Mimari")

    with st.sidebar:
        st.header("⚙️ Sistem Ayarları")
        CONFIG["OLLAMA_HOST"] = st.text_input("Ollama Host", value=CONFIG["OLLAMA_HOST"])
        CONFIG["VISION_MODEL"] = st.selectbox(
            "1. Görsel Model (VLM)",
            options=CONFIG["VISION_MODEL"],
            index=CONFIG["VISION_MODEL"].index(CONFIG["VISION_MODEL"]),
        )
        CONFIG["LLM_MODEL"] = st.selectbox(
            "2. Tarif Modeli (LLM)",
            options=CONFIG["LLM_MODEL"],
            index=CONFIG["LLM_MODEL"].index(CONFIG["LLM_MODEL"]),
        )
        CONFIG["LLM_TEMPERATURE"] = st.slider(
            "LLM Temperature", 0.0, 1.0, float(CONFIG["LLM_TEMPERATURE"]), 0.1
        )
        st.code(
            f"ollama pull {CONFIG['VISION_MODEL']}\nollama pull {CONFIG['LLM_MODEL']}",
            language="bash",
        )

    uploaded_file = st.file_uploader(
        "1. Buzdolabı fotoğrafını yükleyin", type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_file:
        image_bytes = uploaded_file.getvalue()
        st.image(image_bytes, use_container_width=True)

        if st.button("🔍 Malzemeleri Çıkar (JSON)", type="primary", use_container_width=True):
            with st.spinner(f"`{CONFIG['VISION_MODEL']}` analiz ediyor..."):
                try:
                    result = extract_ingredients_from_image(image_bytes)
                    st.session_state.ingredients = result.ingredients
                    st.session_state.raw_json = result.model_dump_json(indent=2)
                except Exception as exc:
                    st.error(f"Görsel model hatası: {exc}")

    if st.session_state.raw_json:
        with st.expander("📄 Görsel Model JSON Çıktısı (Structured Output)"):
            st.code(st.session_state.raw_json, language="json")

        edited_text = st.text_area(
            "2. Tespit Edilen Malzemeler (virgülle düzenleyebilirsiniz):",
            value=", ".join(st.session_state.ingredients),
        )
        extra_notes = st.text_input(
            "Ek Not (Opsiyonel):",
            placeholder="Örn: Kahvaltılık olsun, 15 dakikada hazırlansın...",
        )

        if st.button("🍳 Tarif Üret", type="primary", use_container_width=True):
            items = [i.strip() for i in edited_text.split(",") if i.strip()]
            if not items:
                st.warning("En az bir malzeme girin.")
            else:
                st.subheader("🍽️ Önerilen Tarifler")
                try:
                    st.write_stream(stream_recipe(items, extra_notes))
                except Exception as exc:
                    st.error(f"LLM hatası: {exc}")


if __name__ == "__main__":
    main()