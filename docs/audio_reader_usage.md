# Audio Reader - Transcripción de Audio con Whisper

Este módulo proporciona funcionalidad para transcribir archivos de audio usando Whisper, siguiendo el mismo patrón que los otros lectores del proyecto (`pdf_reader.py`, `image_reader.py`).

## Características

- ✅ Transcripción de audio usando Whisper local
- ✅ Soporte para múltiples formatos de audio (MP3, WAV, M4A, FLAC, OGG, WEBM)
- ✅ Opción de incluir timestamps en la transcripción
- ✅ Múltiples modelos de Whisper disponibles
- ✅ Manejo de errores robusto
- ✅ Logging detallado con colores
- ✅ Patrón de estrategia similar a otros lectores

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Verificar instalación de Whisper

El módulo requiere que Whisper esté instalado. Si no está en requirements.txt, instálalo manualmente:

```bash
pip install openai-whisper
```

## Uso Básico

### Transcripción Simple

```python
from server.utils.audio_reader import AudioReader

# Crear lector de audio con modelo base
reader = AudioReader(model_name="base")

# Transcribir archivo de audio
text = reader.read("ruta/al/archivo.mp3")
print(text)
```

### Transcripción con Timestamps

```python
from server.utils.audio_reader import AudioReader

# Crear lector con timestamps
reader = AudioReader(model_name="base", include_timestamps=True)

# Transcribir con timestamps
text_with_timestamps = reader.read("ruta/al/archivo.mp3")
print(text_with_timestamps)
```

### Función de Conveniencia

```python
from server.utils.audio_reader import transcribe_audio_file

# Transcripción rápida
text = transcribe_audio_file("ruta/al/archivo.mp3", model_name="base")
print(text)
```

## Modelos de Whisper Disponibles

| Modelo   | Parámetros | Velocidad | Precisión  | Uso Recomendado  |
| -------- | ---------- | --------- | ---------- | ---------------- |
| `tiny`   | 39M        | ⚡⚡⚡    | ⭐         | Pruebas rápidas  |
| `base`   | 74M        | ⚡⚡      | ⭐⭐       | **Uso general**  |
| `small`  | 244M       | ⚡        | ⭐⭐⭐     | Mejor precisión  |
| `medium` | 769M       | 🐌        | ⭐⭐⭐⭐   | Alta precisión   |
| `large`  | 1550M      | 🐌🐌      | ⭐⭐⭐⭐⭐ | Máxima precisión |

## Formatos de Audio Soportados

- `.mp3` - MPEG Audio Layer III
- `.wav` - Waveform Audio File Format
- `.m4a` - MPEG-4 Audio
- `.flac` - Free Lossless Audio Codec
- `.ogg` - Ogg Vorbis
- `.webm` - WebM Audio

## API Completa

### AudioReader

Clase principal para transcribir archivos de audio.

```python
class AudioReader:
    def __init__(self, model_name: str = "base", include_timestamps: bool = False)
    def read(self, path: str) -> str
    def get_hash(self) -> str
    def get_model_info(self) -> str
```

**Parámetros:**

- `model_name`: Nombre del modelo de Whisper a usar
- `include_timestamps`: Si incluir timestamps en la transcripción

### Funciones de Utilidad

```python
def get_supported_audio_formats() -> list[str]
def is_audio_file(path: str) -> bool
def transcribe_audio_file(path: str, model_name: str = "base", include_timestamps: bool = False) -> str
```

## Ejemplos de Uso

### Ejemplo 1: Transcripción Básica

```python
from server.utils.audio_reader import AudioReader

reader = AudioReader(model_name="base")
text = reader.read("audio.mp3")
print(f"Transcripción: {text}")
print(f"Hash: {reader.get_hash()}")
print(f"Modelo: {reader.get_model_info()}")
```

### Ejemplo 2: Transcripción con Timestamps

```python
from server.utils.audio_reader import AudioReader

reader = AudioReader(model_name="medium", include_timestamps=True)
text = reader.read("audio.mp3")
print(text)
# Salida: [00:00-00:02] Hola mundo
#         [00:02-00:04] ¿Cómo estás?
```

### Ejemplo 3: Verificación de Formato

```python
from server.utils.audio_reader import is_audio_file, get_supported_audio_formats

# Verificar formatos soportados
formats = get_supported_audio_formats()
print(f"Formatos soportados: {formats}")

# Verificar si un archivo es de audio
if is_audio_file("archivo.mp3"):
    print("Es un archivo de audio válido")
else:
    print("No es un archivo de audio válido")
```

### Ejemplo 4: Manejo de Errores

```python
from server.utils.audio_reader import AudioReader

reader = AudioReader()

try:
    text = reader.read("archivo_inexistente.mp3")
except FileNotFoundError:
    print("Archivo no encontrado")
except Exception as e:
    print(f"Error durante la transcripción: {e}")
```

## Integración con el Sistema

El `AudioReader` sigue el mismo patrón que los otros lectores del proyecto:

1. **Patrón de Estrategia**: Usa estrategias diferentes para diferentes tipos de procesamiento
2. **Logging**: Utiliza el sistema de logging con colores del proyecto
3. **Manejo de Errores**: Manejo robusto de errores con mensajes informativos
4. **Configuración**: Soporte para variables de entorno

## Rendimiento

### Recomendaciones de Modelo

- **Desarrollo/Pruebas**: Usa `tiny` o `base`
- **Producción General**: Usa `base` o `small`
- **Alta Precisión**: Usa `medium` o `large`

### Optimización

- Los modelos más grandes requieren más memoria RAM
- El primer uso de un modelo puede ser lento (descarga)
- Los modelos se cachean en memoria para reutilización

## Troubleshooting

### Error: "No module named 'whisper'"

```bash
pip install openai-whisper
```

### Error: "CUDA not available"

Whisper puede usar CPU o GPU. Si no tienes CUDA, funcionará en CPU (más lento).

### Error: "File not found"

Verifica que el archivo existe y la ruta es correcta.

### Error: "Unsupported audio format"

Aunque Whisper soporta muchos formatos, algunos pueden requerir codecs adicionales.

## Archivos Relacionados

- `server/utils/audio_reader.py` - Implementación principal
- `example_audio_reader.py` - Ejemplos de uso
- `test_audio_reader.py` - Tests unitarios
- `requirements.txt` - Dependencias

## Contribuir

Para agregar nuevas funcionalidades:

1. Sigue el patrón de estrategia existente
2. Agrega tests unitarios
3. Actualiza la documentación
4. Verifica compatibilidad con otros lectores
