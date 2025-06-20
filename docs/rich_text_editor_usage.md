# Rich Text Editor - Funcionalidad de Edición

## Descripción

Se ha implementado un editor de texto rico (Rich Text Editor) en el componente de resultados que permite a los usuarios editar las demandas y convenios generados por la IA.

## Características

### 1. Editor de Texto Rico

- **Tecnología**: ContentEditable nativo (compatible con React 19)
- **Funcionalidades**:
  - Formato de texto (negrita, cursiva, subrayado)
  - Encabezados (H1, H2, H3)
  - Listas ordenadas y no ordenadas
  - Alineación de texto (izquierda, centro, derecha)
  - Párrafos
  - Atajos de teclado (Ctrl+Enter para guardar)

### 2. Botones de Acción

- **Editar**: Permite entrar en modo de edición
- **Guardar**: Guarda los cambios en el backend
- **Cancelar**: Cancela la edición y vuelve al modo de visualización
- **Solicitar Cambios a la IA**: Permite enviar feedback para que la IA mejore el documento

### 3. Resumen del Caso

- **Visualización**: Se muestra el resumen del caso proporcionado por el abogado
- **Contexto**: El resumen se incluye en el análisis de documentos y generación de documentos
- **Importancia**: Ayuda a la IA a entender mejor el contexto del caso

### 4. Endpoints del Backend

#### PUT `/api/case/{case_id}/demand`

Actualiza el contenido HTML de la demanda.

**Parámetros**:

- `html_content` (string): El contenido HTML de la demanda

**Respuesta**:

```json
{
  "message": "Demand updated successfully",
  "case_id": "uuid"
}
```

#### PUT `/api/case/{case_id}/agreement`

Actualiza el contenido HTML del convenio.

**Parámetros**:

- `html_content` (string): El contenido HTML del convenio

**Respuesta**:

```json
{
  "message": "Agreement updated successfully",
  "case_id": "uuid"
}
```

#### POST `/api/case/{case_id}/request-ai-changes`

Envía una solicitud de cambios a la IA.

**Parámetros**:

- `document_type` (string): "demand" o "agreement"
- `user_feedback` (string): Descripción de los cambios deseados

**Respuesta**:

```json
{
  "message": "AI change request received successfully",
  "case_id": "uuid",
  "document_type": "demand",
  "feedback": "user feedback text"
}
```

#### GET `/api/case/{case_id}/results` (Actualizado)

Obtiene los resultados del caso incluyendo el summary.

**Respuesta**:

```json
{
  "demand": "html content",
  "agreement": "html content",
  "summary": "resumen del caso proporcionado por el abogado",
  "status": "DONE"
}
```

## Flujo de Uso

1. **Visualización**: El usuario ve el documento generado por la IA y el resumen del caso
2. **Edición**: Hace clic en "Editar" para entrar en modo de edición
3. **Modificación**: Usa el editor de texto rico para hacer cambios
4. **Guardado**: Hace clic en "Guardar Cambios" o usa Ctrl+Enter para persistir los cambios
5. **Feedback IA** (opcional): Puede solicitar cambios adicionales a la IA

## Componentes

### RichTextEditor

Componente principal del editor que incluye:

- Barra de herramientas con botones de formato
- Editor contentEditable
- Sección de feedback para IA
- Botones de acción (Guardar/Cancelar)

### Results (Modificado)

Componente principal que ahora incluye:

- Modo de visualización/edición
- Visualización del resumen del caso
- Integración con el editor
- Manejo de estados de carga

## Mejoras en el Backend

### Análisis de Documentos

- **Contexto del Caso**: El summary del caso se incluye en el análisis de cada documento
- **Mejor Extracción**: La IA considera el contexto al extraer información relevante

### Generación de Documentos

- **Contexto del Caso**: El summary se incluye en la generación de demandas y convenios
- **Documentos Más Precisos**: Los documentos reflejan mejor los hechos descritos por el abogado

## Estilos CSS

Se han agregado estilos personalizados para el editor en `client/src/index.css`:

- Barra de herramientas con botones de formato
- Editor con altura mínima y bordes redondeados
- Colores consistentes con el diseño

## Dependencias

### Frontend

- No se requieren dependencias adicionales (usa contentEditable nativo)
- `react-hot-toast`: Notificaciones

### Backend

- No se requieren dependencias adicionales

## Notas Técnicas

1. **Compatibilidad**: El editor usa contentEditable nativo, compatible con React 19
2. **Versionado**: Los documentos mantienen un número de versión que se incrementa en cada actualización
3. **Feedback**: El feedback del usuario se almacena en el campo `feedback` de la base de datos
4. **Contexto**: El summary del caso se incluye en todos los procesos de IA
5. **Estados de Carga**: Se muestran indicadores de carga durante las operaciones

## Próximos Pasos

1. **Procesamiento de IA**: Implementar el procesamiento real de las solicitudes de cambios por parte de la IA
2. **Historial de Versiones**: Mostrar el historial de versiones de los documentos
3. **Comparación**: Permitir comparar diferentes versiones de un documento
4. **Colaboración**: Permitir múltiples usuarios editen el mismo documento
