# AI Chef 🧑‍🍳

Buzdolabı fotoğrafından malzemeleri tespit edip yemek tarifi öneren Streamlit uygulaması. Ollama üzerinde çalışan bir görsel model (VLM) ile malzemeleri çıkarır, ardından bir LLM ile Türkçe tarif üretir.

## Gereksinimler

- Python >= 3.12
- [Ollama](https://ollama.com) kurulu ve çalışıyor olmalı
- `uv` paket yöneticisi

## Kurulum

```bash
uv sync
ollama pull gemma3:4b
```

## Çalıştırma

```bash
uv run streamlit run src/ai_chef/app.py
```

## Nasıl çalışır?

1. Buzdolabı fotoğrafı yüklenir.
2. Görsel model (VLM) fotoğraftaki malzemeleri JSON olarak çıkarır.
3. Malzemeler düzenlenip (opsiyonel not eklenerek) LLM'e gönderilir.
4. LLM, mevcut malzemelerle hazırlanabilecek tarifleri Türkçe olarak önerir.
