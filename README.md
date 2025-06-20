# Sistema de Generación de Demandas Iniciales y Convenios

Sistema automatizado para generar demandas iniciales y convenios de divorcio incausado utilizando inteligencia artificial y análisis de documentos.

## Características Principales

- **Subida de archivos múltiples**: Soporta PDF, DOCX, imágenes y archivos de texto
- **Extracción automática de texto**: Utiliza OCR y procesamiento de documentos
- **Análisis con IA**: Extrae información relevante de los documentos
- **Generación automática de documentos**: Crea HTML de demanda y convenio basándose en plantillas y datos extraídos
- **Procesamiento paralelo**: Genera demanda y convenio simultáneamente
- **Notificaciones en tiempo real**: Seguimiento del progreso vía WebSocket
- **API REST completa**: Endpoints para gestión de casos y documentos

## Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Base de       │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Datos         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Celery        │
                       │   (Workers)     │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   IA Service    │
                       │   (Ollama/      │
                       │    OpenAI)      │
                       └─────────────────┘
```

## Flujo de Procesamiento

1. **Subida de archivos** → Creación de caso
2. **Extracción de texto** → Análisis con IA
3. **Generación paralela** → Demanda + Convenio simultáneamente
4. **Notificación final** → Ambos documentos listos

## Instalación

### Requisitos Previos

- Python 3.10+
- PostgreSQL
- Redis
- Node.js 18+ (para el frontend)

### Configuración del Backend

1. **Clonar el repositorio**:

```bash
git clone <repository-url>
cd demandas
```

2. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. **Configurar base de datos**:

```bash
# Ejecutar migraciones
alembic upgrade head
```

5. **Configurar IA**:
   - Para Ollama: Ver [docs/install_vllm.md](docs/install_vllm.md)
   - Para OpenAI: Configurar API key en `.env`

### Configuración del Frontend

```bash
cd client
npm install
npm run dev
```

## Uso del Sistema

### 1. Subida de Archivos

Los usuarios pueden subir múltiples archivos a través de la interfaz web o directamente via API:

```bash
curl -X POST "http://localhost:8000/api/upload-files" \
  -F "files=@documento1.pdf" \
  -F "files=@documento2.docx" \
  -F "resumen_del_caso=Descripción del caso de divorcio"
```

### 2. Proceso Automático

Una vez subidos los archivos, el sistema ejecuta automáticamente:

1. **Extracción de texto** de cada archivo
2. **Análisis con IA** para extraer información relevante
3. **Generación paralela** de demanda inicial y convenio
4. **Almacenamiento** en base de datos
5. **Notificación** cuando ambos documentos están listos

### 3. Notificaciones en Tiempo Real

El sistema envía notificaciones sobre el progreso:

- "Generando demanda inicial."
- "Generando convenio inicial."
- "¡Proceso completado! Demanda inicial y convenio generados exitosamente."

## Estructura del Proyecto

```
demandas/
├── server/                     # Backend (FastAPI)
│   ├── ai/                    # Interfaz de IA
│   ├── generator/             # Generadores de documentos
│   │   ├── generate_initial_demand.py
│   │   └── generate_initial_agreement.py
│   ├── machotes/              # Plantillas HTML
│   │   ├── divorcio_incausado.html
│   │   └── convenio_divorcio_incausado.html
│   ├── models.py              # Modelos de base de datos
│   ├── routes.py              # Endpoints de la API
│   └── tasks.py               # Tareas de Celery
├── client/                    # Frontend (React)
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   └── utils/             # Utilidades
│   └── package.json
├── docs/                      # Documentación
├── alembic/                   # Migraciones de BD
└── requirements.txt           # Dependencias Python
```

## Configuración de IA

### Ollama (Recomendado)

1. Instalar Ollama: https://ollama.ai/
2. Descargar modelo:

```bash
ollama pull gemma3:1b
```

3. Configurar variables de entorno:

```env
PROVIDER=ollama
MODEL=gemma3:1b
```

### OpenAI

1. Configurar API key:

```env
PROVIDER=openai
PROVIDER_API_KEY=tu-api-key
MODEL=gpt-4o-mini
```

## Pruebas

### Ejecutar prueba de generación de ambos documentos:

```bash
python test_both_documents_generation.py
```

### Ejecutar pruebas de conexión IA:

```bash
python test_vllm_connection.py
```

## API Endpoints

### Casos

- `POST /api/upload-files` - Subir archivos y crear caso

### Documentos (futuros endpoints)

- `GET /api/case/{case_id}/demand/{demand_id}` - Ver HTML de demanda
- `GET /api/case/{case_id}/agreement/{agreement_id}` - Ver HTML de convenio
- `GET /api/case/{case_id}/demand/{demand_id}/download` - Descargar demanda
- `GET /api/case/{case_id}/agreement/{agreement_id}/download` - Descargar convenio

## Variables de Entorno

```env
# Base de datos
POSTGRES_USER=usuario
POSTGRES_PASSWORD=password
POSTGRES_DB=demandas
POSTGRES_HOST=localhost
POSTGRES_HOST_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# IA
PROVIDER=ollama
PROVIDER_API_KEY=asdasd
PROVIDER_BASE_URL=http://localhost:11434
MODEL=gemma3:1b
CONTEXT_WINDOW_SIZE=20000

# Servidor
HOST=0.0.0.0
PORT=8000
```

## Desarrollo

### Ejecutar en modo desarrollo:

```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Celery worker
celery -A server.celery_app worker --loglevel=info

# Terminal 3: Frontend
cd client && npm run dev
```

### Logs y Monitoreo:

- Logs del servidor: `logs/`
- Estado de Celery: `celery -A server.celery_app inspect active`
- Redis: `redis-cli monitor`

## Procesamiento Paralelo

El sistema utiliza Celery para procesar ambos documentos simultáneamente:

```python
# Generación paralela de documentos
demand_task = generate_initial_demand_task.delay(case_id)
agreement_task = generate_initial_agreement_task.delay(case_id)

# Esperar que ambos terminen
chord([demand_task, agreement_task])(on_both_documents_generated.s(case_id))
```

## Documentación Adicional

- [Instalación de vLLM](docs/install_vllm.md)
- [Generación de Documentos](docs/demanda_inicial_generation.md)
- [Guía de Uso](docs/usage.md)

## Contribución

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.
