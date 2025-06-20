# Generación de Demanda Inicial y Convenio

## Descripción General

El sistema de generación de documentos legales utiliza inteligencia artificial para crear automáticamente tanto la demanda inicial como el convenio de divorcio incausado, basándose en los attachments (documentos adjuntos) analizados y utilizando plantillas HTML predefinidas.

## Flujo del Proceso

### 1. Subida de Archivos

- Los usuarios suben archivos (PDF, DOCX, imágenes, etc.) a través del endpoint `/api/upload-files`
- Se crea un caso en la base de datos con estado `PENDING`
- Se crean registros de attachments para cada archivo

### 2. Lectura y Extracción de Texto

- El sistema lee cada archivo y extrae el texto contenido
- Soporta múltiples formatos: PDF, DOCX, imágenes (JPG, PNG, etc.), archivos de texto
- El texto extraído se guarda en el campo `extracted_text` de cada attachment

### 3. Análisis con IA

- Para cada attachment, se ejecuta un análisis con IA
- La IA extrae información relevante y la estructura en:
  - `brief`: Resumen del documento
  - `findings`: Puntos relevantes y datos específicos
- Se buscan variables específicas como nombres, fechas, domicilios, etc.

### 4. Generación Paralela de Documentos

- Una vez que todos los attachments han sido analizados
- El sistema inicia **en paralelo** la generación de:
  - **Demanda inicial** usando el template de divorcio incausado
  - **Convenio inicial** usando el template de convenio
- Ambos procesos utilizan la IA para completar los templates con la información extraída

### 5. Notificación de Completado

- Cuando ambos documentos han sido generados exitosamente
- Se notifica al cliente que el proceso está completo
- Los documentos se almacenan en la base de datos

## Archivos Principales

### `server/generator/generate_initial_demand.py`

Contiene la lógica para generar la demanda inicial:

- `read_machote_template()`: Lee el template HTML del machote de demanda
- `get_attachments_data()`: Obtiene datos de attachments analizados
- `generate_initial_demand()`: Función principal que coordina el proceso

### `server/generator/generate_initial_agreement.py`

Contiene la lógica para generar el convenio inicial:

- `read_machote_template()`: Lee el template HTML del machote de convenio
- `get_attachments_data()`: Obtiene datos de attachments analizados
- `generate_initial_agreement()`: Función principal que coordina el proceso

### `server/machotes/`

Directorio que contiene las plantillas HTML:

- `divorcio_incausado.html`: Template para demanda de divorcio incausado
- `convenio_divorcio_incausado.html`: Template para convenio de divorcio

### `server/tasks.py`

Define las tareas de Celery con procesamiento paralelo:

- `read_attachments`: Lee y extrae texto de archivos
- `analyze_attachment`: Analiza cada attachment con IA
- `on_all_analyses_done`: Se ejecuta cuando todos los análisis terminan
- `generate_initial_demand_task`: Genera la demanda inicial
- `generate_initial_agreement_task`: Genera el convenio inicial
- `on_both_documents_generated`: Se ejecuta cuando ambos documentos están listos

## Procesamiento Paralelo

El sistema utiliza Celery para procesar ambos documentos en paralelo:

```python
# Iniciar generación de demanda y convenio en paralelo
demand_task = generate_initial_demand_task.delay(case_id)
agreement_task = generate_initial_agreement_task.delay(case_id)

# Crear chord para esperar que ambas tareas terminen
chord([demand_task, agreement_task])(on_both_documents_generated.s(case_id))
```

## Variables de los Templates

### Demanda Inicial

El sistema busca y reemplaza las siguientes variables en el template de demanda:

- `{{ nombre_del_promovente }}`: Nombre completo de quien promueve el divorcio
- `{{ nombre_completo_del_demandado }}`: Nombre completo de la persona demandada
- `{{ domicilio_del_promovente }}`: Domicilio del promovente
- `{{ domicilio_del_demandado }}`: Domicilio del demandado
- `{{ domicilio_conyugal }}`: Último domicilio conyugal
- `{{ fecha_matrimonio }}`: Fecha del matrimonio
- `{{ tipo_regimen_conyugal }}`: Tipo de régimen conyugal
- `{{ detalle_hijos }}`: Información sobre hijos si los hay
- `{{ fecha_de_cuidado }}`: Fecha desde cuando se cuida a los hijos
- `{{ detalle_bienes_inmuebles }}`: Bienes inmuebles a repartir
- `{{ detalles_abogados }}`: Información de los abogados
- `{{ persona_autorizada_notificaciones }}`: Persona autorizada para notificaciones
- `{{ persona_abogada_acceso_al_sistema }}`: Abogado con acceso al sistema

### Convenio Inicial

El sistema busca y reemplaza las siguientes variables en el template de convenio:

- `[NOMBRE COMPLETO DE LA PERSONA QUE PROMUEVE EL DIVORCIO]`: Nombre del promovente
- `[DOMICILIO donde habitará la persona que promueve el divorcio]`: Domicilio del promovente
- Información sobre hijos para determinar si son mayores de edad
- Información sobre bienes inmuebles para la repartición
- Información sobre la autosuficiencia económica de las partes

## Notificaciones en Tiempo Real

El sistema utiliza Redis para enviar notificaciones en tiempo real sobre el progreso:

### Durante la Generación de Demanda:

- "Generando demanda inicial."
- "Generando HTML con IA..."
- "Demanda inicial generada exitosamente."

### Durante la Generación de Convenio:

- "Generando convenio inicial."
- "Generando HTML del convenio con IA..."
- "Convenio inicial generado exitosamente."

### Cuando Ambos Documentos Están Listos:

- "¡Proceso completado! Demanda inicial y convenio generados exitosamente."
- `status: "COMPLETED"`
- `both_documents_ready: true`

## Estructura de la Base de Datos

### Tabla `demands`

- `id`: UUID único
- `case_id`: Referencia al caso
- `version`: Versión del documento
- `html`: Contenido HTML de la demanda
- `feedback`: Comentarios o feedback
- `created_at`: Fecha de creación

### Tabla `agreements`

- `id`: UUID único
- `case_id`: Referencia al caso
- `version`: Versión del documento
- `html`: Contenido HTML del convenio
- `feedback`: Comentarios o feedback
- `created_at`: Fecha de creación

## Manejo de Errores

El sistema incluye manejo robusto de errores:

- **Errores Individuales**: Si falla la generación de un documento, se notifica el error específico
- **Errores de IA**: Manejo de errores de conexión con el servicio de IA
- **Errores de Base de Datos**: Rollback de transacciones en caso de error
- **Logging Detallado**: Registro de errores para debugging
- **Notificaciones de Error**: Información de errores enviada al cliente

## Configuración de IA

El sistema utiliza la interfaz de IA configurada en `server/ai/ai_interface.py`:

- **Provider**: Ollama (por defecto) o OpenAI
- **Modelo**: Configurado por variable de entorno `MODEL`
- **Context Window**: Configurado por variable de entorno `CONTEXT_WINDOW_SIZE`

## Pruebas

### Script de Prueba Completo

```bash
python test_both_documents_generation.py
```

Este script:

1. Crea un caso de prueba con attachments simulados
2. Genera tanto la demanda como el convenio
3. Verifica que ambos documentos se crearon correctamente
4. Limpia los datos de prueba

## Optimizaciones

### Procesamiento Paralelo

- Ambos documentos se generan simultáneamente para reducir el tiempo total
- Utiliza Celery para manejo asíncrono de tareas

### Reutilización de Datos

- Los attachments se analizan una sola vez
- Los datos extraídos se reutilizan para ambos documentos

### Caché de Templates

- Los templates HTML se leen una sola vez por proceso
- Reducción de I/O para mejorar el rendimiento

## Endpoints de la API

### Obtener Estado del Caso

```
GET /api/case/{case_id}
```

Retorna información completa del caso, incluyendo attachments y demandas generadas.

### Ver HTML de la Demanda

```
GET /api/case/{case_id}/demand/{demand_id}
```

Retorna el HTML de una demanda específica para visualización.

### Descargar HTML de la Demanda

```
GET /api/case/{case_id}/demand/{demand_id}/download
```

Descarga el HTML de una demanda como archivo.
