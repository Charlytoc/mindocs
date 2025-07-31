#!/usr/bin/env python3
"""
Test para verificar la funcionalidad del AudioReader.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.utils.audio_reader import (
    AudioReader,
    WhisperStrategy,
    WhisperWithTimestampsStrategy,
    get_supported_audio_formats,
    is_audio_file,
    transcribe_audio_file,
)


class TestAudioReader(unittest.TestCase):
    """Test cases para AudioReader."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.test_audio_file = "test_audio.mp3"

        # Crear un archivo de prueba temporal
        with open(self.test_audio_file, "w") as f:
            f.write("test content")

    def tearDown(self):
        """Limpieza después de los tests."""
        if os.path.exists(self.test_audio_file):
            os.remove(self.test_audio_file)

    def test_get_supported_audio_formats(self):
        """Test para verificar los formatos de audio soportados."""
        formats = get_supported_audio_formats()
        expected_formats = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"]

        self.assertEqual(formats, expected_formats)
        self.assertIsInstance(formats, list)

    def test_is_audio_file(self):
        """Test para verificar la detección de archivos de audio."""
        # Test con archivo de audio válido
        self.assertTrue(is_audio_file("test.mp3"))
        self.assertTrue(is_audio_file("test.wav"))
        self.assertTrue(is_audio_file("test.m4a"))

        # Test con archivo no válido
        self.assertFalse(is_audio_file("test.txt"))
        self.assertFalse(is_audio_file("test.pdf"))

        # Test con archivo inexistente
        self.assertFalse(is_audio_file("nonexistent.mp3"))

    @patch("whisper.load_model")
    def test_whisper_strategy_initialization(self, mock_load_model):
        """Test para verificar la inicialización de WhisperStrategy."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model

        strategy = WhisperStrategy(model_name="base")

        self.assertEqual(strategy.model_name, "base")
        self.assertIsNone(strategy.model)

        # Verificar que el modelo se carga cuando se llama read
        mock_result = {"text": "test transcription"}
        mock_model.transcribe.return_value = mock_result

        result = strategy.read(self.test_audio_file)

        self.assertEqual(result, "test transcription")
        mock_load_model.assert_called_once_with("base")

    @patch("whisper.load_model")
    def test_whisper_strategy_empty_transcription(self, mock_load_model):
        """Test para verificar el manejo de transcripciones vacías."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model

        strategy = WhisperStrategy(model_name="base")

        # Simular transcripción vacía
        mock_result = {"text": ""}
        mock_model.transcribe.return_value = mock_result

        result = strategy.read(self.test_audio_file)

        self.assertEqual(result, "No se detectó texto en el archivo de audio.")

    @patch("whisper.load_model")
    def test_whisper_with_timestamps_strategy(self, mock_load_model):
        """Test para verificar la estrategia con timestamps."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model

        strategy = WhisperWithTimestampsStrategy(model_name="base")

        # Simular resultado con segmentos
        mock_result = {
            "text": "test transcription",
            "segments": [
                {"start": 0.0, "end": 2.0, "text": "Hello world"},
                {"start": 2.5, "end": 4.0, "text": "How are you"},
            ],
        }
        mock_model.transcribe.return_value = mock_result

        result = strategy.read(self.test_audio_file)

        # Verificar que contiene timestamps
        self.assertIn("[00:00-00:02]", result)
        self.assertIn("[00:02-00:04]", result)
        self.assertIn("Hello world", result)
        self.assertIn("How are you", result)

    def test_audio_reader_initialization(self):
        """Test para verificar la inicialización de AudioReader."""
        # Test sin timestamps
        reader = AudioReader(model_name="base", include_timestamps=False)
        self.assertIsInstance(reader.strategy, WhisperStrategy)

        # Test con timestamps
        reader_with_timestamps = AudioReader(model_name="base", include_timestamps=True)
        self.assertIsInstance(
            reader_with_timestamps.strategy, WhisperWithTimestampsStrategy
        )

    @patch("whisper.load_model")
    def test_audio_reader_read(self, mock_load_model):
        """Test para verificar la lectura de archivos de audio."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model

        reader = AudioReader(model_name="base")

        mock_result = {"text": "test transcription"}
        mock_model.transcribe.return_value = mock_result

        result = reader.read(self.test_audio_file)

        self.assertEqual(result, "test transcription")
        self.assertEqual(reader.text, "test transcription")

    def test_audio_reader_file_not_found(self):
        """Test para verificar el manejo de archivos no encontrados."""
        reader = AudioReader()

        with self.assertRaises(FileNotFoundError):
            reader.read("nonexistent.mp3")

    def test_audio_reader_get_hash(self):
        """Test para verificar la generación de hash."""
        reader = AudioReader()
        reader.text = "test text"

        hash_result = reader.get_hash()

        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hash length

    def test_audio_reader_get_hash_no_text(self):
        """Test para verificar el error cuando no hay texto."""
        reader = AudioReader()

        with self.assertRaises(ValueError):
            reader.get_hash()

    def test_audio_reader_get_model_info(self):
        """Test para verificar la información del modelo."""
        reader = AudioReader(model_name="base")

        model_info = reader.get_model_info()

        self.assertEqual(model_info, "Modelo Whisper: base")

    @patch("whisper.load_model")
    def test_transcribe_audio_file_function(self, mock_load_model):
        """Test para verificar la función de conveniencia."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model

        mock_result = {"text": "test transcription"}
        mock_model.transcribe.return_value = mock_result

        result = transcribe_audio_file(self.test_audio_file, model_name="base")

        self.assertEqual(result, "test transcription")


if __name__ == "__main__":
    # Crear un archivo de prueba temporal
    test_file = "test_audio.mp3"
    if not os.path.exists(test_file):
        with open(test_file, "w") as f:
            f.write("test content")

    try:
        unittest.main(verbosity=2)
    finally:
        # Limpiar archivo de prueba
        if os.path.exists(test_file):
            os.remove(test_file)
