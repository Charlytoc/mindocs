import os
import hashlib
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import whisper
from server.utils.printer import Printer

# =========================
# Configuración flexible
# =========================

load_dotenv()

# =========================
# Estrategia base
# =========================

printer = Printer("AUDIO_READER")


class AudioStrategy(ABC):
    @abstractmethod
    def read(self, path: str) -> str:
        pass

    def hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


# =========================
# Estrategias específicas
# =========================


class WhisperStrategy(AudioStrategy):
    def __init__(self, model_name: str = "base"):
        """
        Inicializa la estrategia de Whisper con el modelo especificado.

        Args:
            model_name: Nombre del modelo de Whisper a usar ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_name = model_name
        self.model = None
        printer.yellow(f"WhisperStrategy inicializada con modelo: {model_name}")

    def _load_model(self):
        """Carga el modelo de Whisper si no está cargado."""
        if self.model is None:
            printer.yellow(f"Cargando modelo Whisper: {self.model_name}")
            try:
                self.model = whisper.load_model(self.model_name)
                printer.green(f"Modelo Whisper {self.model_name} cargado exitosamente")
            except Exception as e:
                printer.red(f"Error cargando modelo Whisper: {e}")
                raise

    def read(self, path: str) -> str:
        """
        Transcribe el archivo de audio usando Whisper.

        Args:
            path: Ruta al archivo de audio

        Returns:
            str: Texto transcrito del audio
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Archivo de audio no encontrado: {path}")

        # Verificar extensión de archivo
        supported_formats = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"]
        file_ext = os.path.splitext(path)[1].lower()

        if file_ext not in supported_formats:
            printer.yellow(
                f"Formato de archivo {file_ext} no está en la lista de formatos soportados, pero se intentará procesar"
            )

        try:
            self._load_model()

            printer.yellow(f"Transcribiendo archivo: {path}")

            # Transcribir el audio
            result = self.model.transcribe(path)

            # Extraer el texto transcrito
            transcribed_text = result["text"].strip()

            if not transcribed_text:
                printer.yellow("No se detectó texto en el audio")
                return "No se detectó texto en el archivo de audio."

            printer.green(
                f"Transcripción completada. Longitud del texto: {len(transcribed_text)} caracteres"
            )

            return transcribed_text

        except Exception as e:
            printer.red(f"Error durante la transcripción: {e}")
            raise


class WhisperWithTimestampsStrategy(WhisperStrategy):
    def read(self, path: str) -> str:
        """
        Transcribe el archivo de audio usando Whisper y incluye timestamps.

        Args:
            path: Ruta al archivo de audio

        Returns:
            str: Texto transcrito con timestamps
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Archivo de audio no encontrado: {path}")

        try:
            self._load_model()

            printer.yellow(f"Transcribiendo archivo con timestamps: {path}")

            # Transcribir el audio con timestamps
            result = self.model.transcribe(path, verbose=True)

            # Construir texto con timestamps
            segments = result.get("segments", [])
            if not segments:
                return result.get("text", "").strip()

            transcribed_text = []
            for segment in segments:
                start_time = segment.get("start", 0)
                end_time = segment.get("end", 0)
                text = segment.get("text", "").strip()

                if text:
                    # Formatear tiempo como MM:SS
                    start_str = f"{int(start_time//60):02d}:{int(start_time%60):02d}"
                    end_str = f"{int(end_time//60):02d}:{int(end_time%60):02d}"

                    transcribed_text.append(f"[{start_str}-{end_str}] {text}")

            final_text = "\n".join(transcribed_text)

            printer.green(
                f"Transcripción con timestamps completada. Longitud del texto: {len(final_text)} caracteres"
            )

            return final_text

        except Exception as e:
            printer.red(f"Error durante la transcripción con timestamps: {e}")
            raise


# =========================
# Lector de audio
# =========================


class AudioReader:
    text: str | None = None

    def __init__(self, model_name: str = "base", include_timestamps: bool = False):
        """
        Inicializa el lector de audio.

        Args:
            model_name: Nombre del modelo de Whisper a usar
            include_timestamps: Si incluir timestamps en la transcripción
        """
        if include_timestamps:
            self.strategy: AudioStrategy = WhisperWithTimestampsStrategy(model_name)
        else:
            self.strategy: AudioStrategy = WhisperStrategy(model_name)

    def read(self, path: str) -> str:
        """
        Lee y transcribe un archivo de audio.

        Args:
            path: Ruta al archivo de audio

        Returns:
            str: Texto transcrito del audio
        """
        print("Procesando audio...")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Archivo no encontrado: {path}")

        self.text = self.strategy.read(path)
        return self.text

    def get_hash(self) -> str:
        """
        Obtiene el hash del texto transcrito.

        Returns:
            str: Hash SHA256 del texto
        """
        if self.text is None:
            raise ValueError("No se ha leído ningún archivo de audio todavía")
        return self.strategy.hash_text(self.text)

    def get_model_info(self) -> str:
        """
        Obtiene información sobre el modelo de Whisper usado.

        Returns:
            str: Información del modelo
        """
        if hasattr(self.strategy, "model_name"):
            return f"Modelo Whisper: {self.strategy.model_name}"
        return "Información del modelo no disponible"


# =========================
# Funciones de utilidad
# =========================


def get_supported_audio_formats() -> list[str]:
    """
    Retorna la lista de formatos de audio soportados.

    Returns:
        list[str]: Lista de extensiones de archivo soportadas
    """
    return [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"]


def is_audio_file(path: str) -> bool:
    """
    Verifica si un archivo es un archivo de audio soportado.

    Args:
        path: Ruta al archivo

    Returns:
        bool: True si es un archivo de audio soportado
    """
    if not os.path.isfile(path):
        return False

    file_ext = os.path.splitext(path)[1].lower()
    return file_ext in get_supported_audio_formats()


def transcribe_audio_file(
    path: str, model_name: str = "base", include_timestamps: bool = False
) -> str:
    """
    Función de conveniencia para transcribir un archivo de audio.

    Args:
        path: Ruta al archivo de audio
        model_name: Nombre del modelo de Whisper a usar
        include_timestamps: Si incluir timestamps en la transcripción

    Returns:
        str: Texto transcrito del audio
    """
    reader = AudioReader(model_name=model_name, include_timestamps=include_timestamps)
    return reader.read(path)
