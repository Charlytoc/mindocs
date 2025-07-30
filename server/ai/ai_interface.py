import os

import inspect
import json

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
    messages: list[dict] = []

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

        return response

    def agent_loop(
        self,
        messages: list[dict] = None,
        model: str | None = None,
        tools: list[dict] | list[callable] = [],
        tools_fn_map: dict = None,
        on_message: callable = None,
    ):
        """
        Ejecuta un ciclo function-calling hasta que no haya tool_calls.
        Llama a on_message(response) en cada iteración.
        """
        self.messages = messages.copy() if messages else self.messages.copy()
        turns = 0

        while True:
            printer.yellow(self.messages, "MESSAGES")
            response = self.chat(
                messages=self.messages,
                model=model,
                stream=False,
                tools=tools,
            )
            printer.yellow(response.choices[0].message, "RESPONSE")

            # OpenAI: response.choices[0].message
            if hasattr(response, "choices"):
                msg = response.choices[0].message
                if on_message:
                    on_message(msg)

                tool_calls = getattr(msg, "tool_calls", None)
                if tool_calls:
                    # Añade el mensaje assistant con tool_calls
                    self.messages.append(
                        {
                            "role": "assistant",
                            "content": msg.content or "",
                            "tool_calls": [tc.model_dump() for tc in tool_calls],
                        }
                    )
                    # Ejecuta tools
                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        # Ejecuta función local si está en el mapa
                        if tools_fn_map and tool_name in tools_fn_map:
                            result = tools_fn_map[tool_name](**args)
                        else:
                            result = f"Function {tool_name} not implemented."
                        # Mensaje de tool
                        self.messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": str(result),
                            }
                        )
                    # Sigue el loop (nuevo turno)
                    turns += 1
                    continue
                else:
                    # Final, no hay tool_calls
                    self.messages.append(
                        {
                            "role": "assistant",
                            "content": msg.content or "",
                        }
                    )
                    if on_message:
                        on_message(msg)
                    break

        return "Agent loop terminated"


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

    def agent_loop(
        self,
        messages: list[dict] = None,
        model: str | None = None,
        tools: list[dict] | list[callable] = [],
        tools_fn_map: dict = None,
        on_message: callable = None,
    ):
        return self.client.agent_loop(
            messages=messages,
            model=model,
            tools=tools,
            tools_fn_map=tools_fn_map,
            on_message=on_message,
        )

    def check_model(self, model: str):
        return self.client.check_model(model)


def function_to_openai_schema(fn, description=None):
    sig = inspect.signature(fn)
    props = {}
    required = []
    for name, param in sig.parameters.items():
        # Solo soporta tipos simples: str, int, float, bool
        ann = param.annotation
        if ann == str:
            type_ = "string"
        elif ann == int:
            type_ = "integer"
        elif ann == float:
            type_ = "number"
        elif ann == bool:
            type_ = "boolean"
        else:
            type_ = "string"  # fallback, podrías mejorar esto
        props[name] = {"type": type_}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    schema = {
        "type": "object",
        "properties": props,
        "required": required,
        "additionalProperties": False,
    }
    return {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": description or fn.__doc__ or fn.__name__,
            "parameters": schema,
            "strict": True,
        },
    }
