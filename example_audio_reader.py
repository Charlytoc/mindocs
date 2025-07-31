#!/usr/bin/env python3
"""
Ejemplo de uso del AudioReader para transcribir archivos de audio usando Whisper.
"""

import os
import sys
from server.utils.audio_reader import (
    AudioReader,
    transcribe_audio_file,
    get_supported_audio_formats,
    is_audio_file,
)


def main():
    """Ejemplo de uso del AudioReader."""

    print("🎵 Ejemplo de AudioReader con Whisper")
    print("=" * 50)

    # Mostrar formatos soportados
    print(f"Formatos de audio soportados: {', '.join(get_supported_audio_formats())}")
    print()

    # Ejemplo 1: Uso básico con modelo base
    print("📝 Ejemplo 1: Transcripción básica con modelo 'base'")
    print("-" * 40)

    # Verificar si hay un archivo de audio de ejemplo
    audio_file = "example_audio.mp3"  # Cambiar por la ruta de tu archivo de audio

    if not os.path.exists(audio_file):
        print(f"⚠️  Archivo de ejemplo '{audio_file}' no encontrado.")
        print(
            "   Por favor, coloca un archivo de audio en el directorio raíz o modifica la variable 'audio_file'"
        )
        print()
        print("📋 Uso del AudioReader:")
        print("   reader = AudioReader(model_name='base')")
        print("   text = reader.read('ruta/al/archivo.mp3')")
        print("   print(text)")
        return

    if not is_audio_file(audio_file):
        print(f"⚠️  El archivo '{audio_file}' no es un archivo de audio soportado.")
        return

    try:
        # Crear lector de audio con modelo base
        reader = AudioReader(model_name="base")

        # Transcribir el archivo
        print(f"🎤 Transcribiendo: {audio_file}")
        transcribed_text = reader.read(audio_file)

        print("📄 Transcripción:")
        print(transcribed_text)
        print()

        # Mostrar información del modelo
        print(f"ℹ️  {reader.get_model_info()}")
        print()

        # Mostrar hash del texto
        print(f"🔐 Hash del texto: {reader.get_hash()}")
        print()

    except Exception as e:
        print(f"❌ Error durante la transcripción: {e}")
        print()

    # Ejemplo 2: Transcripción con timestamps
    print("⏰ Ejemplo 2: Transcripción con timestamps")
    print("-" * 40)

    try:
        # Crear lector de audio con timestamps
        reader_with_timestamps = AudioReader(model_name="base", include_timestamps=True)

        # Transcribir el archivo con timestamps
        print(f"🎤 Transcribiendo con timestamps: {audio_file}")
        transcribed_with_timestamps = reader_with_timestamps.read(audio_file)

        print("📄 Transcripción con timestamps:")
        print(transcribed_with_timestamps)
        print()

    except Exception as e:
        print(f"❌ Error durante la transcripción con timestamps: {e}")
        print()

    # Ejemplo 3: Función de conveniencia
    print("🚀 Ejemplo 3: Función de conveniencia")
    print("-" * 40)

    try:
        # Usar la función de conveniencia
        text = transcribe_audio_file(
            audio_file, model_name="base", include_timestamps=False
        )

        print("📄 Transcripción usando función de conveniencia:")
        print(text)
        print()

    except Exception as e:
        print(f"❌ Error usando función de conveniencia: {e}")
        print()

    # Información sobre modelos disponibles
    print("📚 Modelos de Whisper disponibles:")
    print("   - tiny: Modelo más pequeño y rápido (39M parámetros)")
    print("   - base: Modelo base (74M parámetros) - RECOMENDADO")
    print("   - small: Modelo pequeño (244M parámetros)")
    print("   - medium: Modelo mediano (769M parámetros)")
    print("   - large: Modelo grande (1550M parámetros)")
    print()
    print("💡 Para mejor precisión, usa 'medium' o 'large'")
    print("💡 Para mayor velocidad, usa 'tiny' o 'base'")


if __name__ == "__main__":
    main()
