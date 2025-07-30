import os
import hashlib
from abc import ABC, abstractmethod
from PIL import Image
import base64
import io

from dotenv import load_dotenv

# IMPORTA TU INTERFAZ DE IA
from server.ai.ai_interface import AIInterface

# =========================
# Configuración flexible
# =========================

load_dotenv()

# =========================
# Estrategia base
# =========================


class ImageStrategy(ABC):
    @abstractmethod
    def read(self, path: str) -> str:
        pass

    def hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


# =========================
# Utilidad para base64
# =========================


def get_base64_image(path: str) -> str:
    img = Image.open(path)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


# =========================
# Estrategias específicas
# =========================


class AIImageStrategy(ImageStrategy):
    def read(self, path: str, context: str = "Archivo adjunto") -> str:
        ai = AIInterface(
            provider=os.getenv("PROVIDER", "ollama"),
            api_key=os.getenv("PROVIDER_API_KEY", "asdasd"),
            base_url=os.getenv("PROVIDER_BASE_URL", None),
        )
        img_str = get_base64_image(path)
        res = ai.chat(
            model=os.getenv("MODEL", "gemma3"),
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente de IA que extrae información útil de imágenes. Si no hay texto, solo explica en qué consiste la imagen de forma detallada. Si hay texto, la extracción debe contener exactamente todo el texto disponible en la imagen junto con la interpretación de lo que significa la imagen. Dicen que una imagen vale más que mil palabras.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": context,
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_str}"},
                        },
                    ],
                },
            ],
        )
        return res.choices[0].message.content.strip()


# =========================
# Lector de imágenes
# =========================


class ImageReader:
    text: str | None = None

    def __init__(self):
        self.strategy: ImageStrategy = AIImageStrategy()

    def read(self, path: str, context: str = "Archivo adjunto") -> str:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Archivo no encontrado: {path}")

        self.text = self.strategy.read(path, context)
        return self.text

    def get_hash(self) -> str:
        if self.text is None:
            raise ValueError("No se ha leído ninguna imagen todavía")
        return self.strategy.hash_text(self.text)
