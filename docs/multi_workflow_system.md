# Sistema Multi-Workflow

## Descripción

El sistema ha sido actualizado para soportar múltiples workflows en lugar de estar limitado solo a demandas. Ahora los usuarios pueden:

1. **Autenticarse** con email y contraseña
2. **Seleccionar workflows** de una lista de procesos disponibles
3. **Subir archivos** específicos para cada tipo de workflow
4. **Procesar documentos** con IA según el workflow seleccionado
5. **Ver resultados** organizados por tipo de documento

## Nuevas Funcionalidades

### Autenticación

- Registro de usuarios con email, contraseña y nombre opcional
- Inicio de sesión con credenciales
- Persistencia de sesión en localStorage
- Cerrar sesión

### Gestión de Workflows

- Lista de workflows disponibles para el usuario
- Información detallada de cada workflow (nombre, descripción, instrucciones)
- Selección de workflow antes de subir archivos

### Carga de Archivos Mejorada

- Interfaz específica para cada workflow
- Descripciones opcionales para cada archivo
- Validación de archivos según el tipo de workflow
- Vista previa de archivos seleccionados

### Procesamiento y Resultados

- Seguimiento del estado de procesamiento
- Visualización de archivos subidos vs generados
- Resultados organizados por tipo de documento
- Edición de documentos generados

## Estructura de la Base de Datos

### Nuevas Tablas

- **users**: Información de usuarios autenticados
- **workflows**: Definición de tipos de procesos
- **workflow_executions**: Ejecuciones específicas de workflows
- **assets**: Archivos subidos y documentos generados

### Relaciones

- Un usuario puede tener múltiples workflows
- Cada workflow puede tener múltiples ejecuciones
- Cada ejecución puede tener múltiples assets (archivos)

## API Endpoints

### Autenticación

- `POST /api/signup` - Registro de usuarios
- `POST /api/login` - Inicio de sesión
- `DELETE /api/delete-account` - Eliminación de cuenta

### Gestión de Workflows

- `GET /api/workflows` - Lista de workflows del usuario
- `GET /api/workflow/{id}` - Detalles de un workflow específico

### Ejecución de Workflows

- `POST /api/start/{workflow_id}` - Iniciar una ejecución de workflow
- `GET /api/workflow-execution/{id}/assets` - Obtener assets de una ejecución
- `GET /api/workflow-executions` - Lista de ejecuciones del usuario

## Configuración Inicial

### 1. Crear Workflows de Prueba

```bash
python create_sample_workflows.py
```

### 2. Credenciales de Prueba

- Email: `test@example.com`
- Contraseña: `test123`

### 3. Workflows Disponibles

1. **Generación de Demandas** - Para crear demandas iniciales
2. **Creación de Convenios** - Para generar convenios legales
3. **Análisis de Contratos** - Para analizar contratos
4. **Generación de Recursos** - Para crear recursos legales

## Flujo de Usuario

1. **Autenticación**: El usuario se registra o inicia sesión
2. **Selección de Workflow**: Elige el tipo de proceso a ejecutar
3. **Carga de Archivos**: Sube los documentos necesarios con descripciones
4. **Procesamiento**: El sistema procesa los archivos con IA
5. **Resultados**: Visualiza y edita los documentos generados

## Componentes de la UI

### Nuevos Componentes

- `Auth.tsx` - Autenticación (login/signup)
- `Navigation.tsx` - Barra de navegación con información del usuario
- `WorkflowList.tsx` - Lista de workflows disponibles
- `WorkflowUpload.tsx` - Carga de archivos para un workflow específico

### Componentes Actualizados

- `App.tsx` - Manejo de estados de la aplicación
- `Waiter.tsx` - Procesamiento con nuevo sistema de ejecuciones
- `Results.tsx` - Resultados con assets y documentos generados

## Compatibilidad

El sistema mantiene compatibilidad con el sistema anterior:

- URLs con parámetro `case` siguen funcionando
- APIs legacy siguen disponibles
- Transición gradual al nuevo sistema

## Próximos Pasos

1. **Implementar procesamiento específico** para cada tipo de workflow
2. **Agregar más tipos de workflows** según necesidades
3. **Mejorar la gestión de assets** con descargas y vistas previas
4. **Implementar notificaciones** en tiempo real
5. **Agregar roles y permisos** para diferentes tipos de usuarios
