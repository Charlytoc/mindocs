import os

from ollama import Client
from ..utils.printer import Printer
from openai import OpenAI

printer = Printer("AI INTERFACE")


# def check_ollama_installation() -> dict:
#     result = {
#         "installed": False,
#         "server_running": False,
#         "version": None,
#         "error": None,
#     }

#     # Verificar si el binario existe
#     if not shutil.which("ollama"):
#         result["error"] = "Ollama no está instalado o no está en el PATH."
#         return result

#     result["installed"] = True

#     # Verificar versión
#     try:
#         version_output = subprocess.check_output(
#             ["ollama", "--version"], text=True
#         ).strip()
#         result["version"] = version_output
#     except subprocess.CalledProcessError:
#         result["error"] = "No se pudo obtener la versión de Ollama."
#         return result

#     # Verificar si el servidor está corriendo
#     try:
#         r = requests.get("http://localhost:11434")
#         if r.status_code == 200:
#             result["server_running"] = True
#     except requests.ConnectionError:
#         result["error"] = "Ollama está instalado pero el servidor no está corriendo."

#     return result


class OllamaProvider:
    def __init__(self):
        self.client = Client()

    def check_model(self, model: str = "gemma3:1b"):
        """Verifica si el modelo está disponible; si no, lo descarga."""
        model_list = self.client.list()
        available = [m.model for m in model_list.models]
        if model not in available:
            print(f"Modelo '{model}' no encontrado. Descargando...")
            self.client.pull(model)
        else:
            print(f"Modelo '{model}' disponible.")

    def embed(self, text: str, model: str = "nomic-embed-text"):
        return self.client.embed(model=model, input=text)

    def chat(
        self,
        messages: list[dict],
        model: str = "gemma3:1b",
        stream: bool = False,
        tools: list[dict] | list[callable] = [],
    ):
        # self.check_model(model)
        printer.blue(f"Generating completion using: {model}")
        context_window_size = int(os.getenv("CONTEXT_WINDOW_SIZE", 20000))
        printer.blue(f"Context window size: {context_window_size}")
        response = self.client.chat(
            model=model,
            messages=messages,
            tools=tools,
            stream=stream,
            options={
                "num_ctx": context_window_size
                # "num_keep": 15,
                # "num_thread": 10,
                # "temperature": 0.8,
            },
        )
        return response.message.content


class OpenAIProvider:
    def __init__(self, api_key: str, base_url: str = None):
        printer.blue(f"Using OpenAI base URL: {base_url}")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def check_model(self, model: str):
        return True

    def chat(
        self,
        messages: list[dict],
        model: str = "gpt-4o-mini",
        stream: bool = False,
        tools: list[dict] | list[callable] = [],
    ):
        printer.blue(f"Generando respuesta con el modelo: {model}")
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            stream=stream,
        )
        # printer.yellow(response, "RESPONSE")

        return response.choices[0].message.content


class AIInterface:
    client: OllamaProvider | OpenAIProvider | None = None

    def __init__(
        self,
        provider: str = "ollama",
        api_key: str = None,
        base_url: str = None,
    ):
        self.provider = provider
        if provider == "ollama":
            self.client = OllamaProvider()
        elif provider == "openai":
            self.client = OpenAIProvider(api_key=api_key, base_url=base_url)
        else:
            raise ValueError(f"Provider {provider} not supported")

        printer.blue("Using AI from", self.provider, "with base URL", base_url)

    def embed(self, text: str, model: str = "nomic-embed-text"):
        return self.client.embed(text, model)

    def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        stream: bool = False,
        tools: list[dict] | list[callable] = [],
    ):
        return self.client.chat(
            model=model,
            messages=messages,
            tools=tools,
            stream=stream,
        )

    def check_model(self, model: str):
        return self.client.check_model(model)
