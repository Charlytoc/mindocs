# MindDocs - Documento de Arquitectura del Sistema

## 📋 Índice
1. [Misión y Visión](#misión-y-visión)
2. [Tipos de Usuarios](#tipos-de-usuarios)
3. [Arquitectura Actual](#arquitectura-actual)
4. [Arquitectura Ideal](#arquitectura-ideal)
5. [Features y Roadmap](#features-y-roadmap)
6. [Stack Tecnológico](#stack-tecnológico)
7. [Estrategia de Despliegue](#estrategia-de-despliegue)
8. [Escalabilidad](#escalabilidad)
9. [Seguridad](#seguridad)
10. [Recomendaciones](#recomendaciones)

---

## 🎯 Misión y Visión

### Misión
Democratizar la automatización documental mediante IA, permitiendo que profesionales y empresas generen, editen y analicen documentos sin conocimiento técnico, reduciendo el tiempo en tareas administrativas repetitivas.

### Visión
Ser la plataforma no-code líder en automatización documental y visual, facilitando la transformación digital de PyMEs y profesionales mediante IA generativa accesible.

---

## 👥 Tipos de Usuarios

### 1. **Freelancers y Profesionales Individuales** 🧑‍💼
**Perfil:**
- Abogados independientes
- Fotógrafos freelance
- Profesionales de RH
- Agentes inmobiliarios
- Community managers

**Necesidades:**
- Automatización de tareas repetitivas
- Reducción de tiempo administrativo
- Precios asequibles ($19-29/mes)
- Facilidad de uso sin código

**Casos de uso:**
- Generación de contratos personalizados
- Limpieza profesional de fotos turísticas
- Generación de posts para redes sociales
- Cotizaciones de servicios

**Valor percibido:** Ahorro de 10-15 horas/semana en tareas administrativas

---

### 2. **Pequeñas y Medianas Empresas (PyMEs)** 🏢
**Perfil:**
- Oficinas legales de 5-20 empleados
- Agencias de viajes
- Hoteles pequeños-medianos
- Agencias inmobiliarias
- Establecimientos de salud

**Necesidades:**
- Estandarización de procesos
- Escalabilidad operativa
- Colaboración entre equipos
- Reportes y auditorías

**Casos de uso:**
- Check-in automatizado de huéspedes
- Gestión automatizada de expedientes médicos
- Generación masiva de contratos
- Análisis de documentos de clientes

**Valor percibido:** Reducción de 30-40% en costos operativos administrativos

**Precio:** $49-99/mes (plan profesional)

---

### 3. **Empresas Medianas-Grandes** 🏢🏢
**Perfil:**
- Empresas con múltiples departamentos
- Cadenas hoteleras
- Firmas legales grandes
- Corporativos con procesos complejos
- Integración con sistemas existentes

**Necesidades:**
- Integraciones con sistemas legacy (ERPs, CRMs)
- Personalización avanzada
- APIs para desarrollo interno
- Soporte técnico dedicado
- Compliance y auditorías
- Multi-tenancy
- Administración centralizada

**Casos de uso:**
- Automatización de workflows corporativos
- Integración con sistemas internos
- Generación de reportes ejecutivos
- Análisis de grandes volúmenes de documentos
- Personalización de flujos por departamento

**Valor percibido:** ROI del 200-300% en automatización documental

**Precio:** $199+/mes o anual (plan empresarial)

---

## 🏗️ Arquitectura Actual

### Componentes Actuales

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    React + TypeScript                       │
│                   (Vite + TailwindCSS)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend API                             │
│                      FastAPI                                │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│   │  Auth    │  │ Routes   │  │ Business │                 │
│   │          │  │          │  │  Logic   │                 │
│   └──────────┘  └──────────┘  └──────────┘                 │
└────────────┬────────────────────┬───────────────────────────┘
             │                    │
             ▼                    ▼
┌────────────────────┐  ┌──────────────────────────────────┐
│   PostgreSQL       │  │        Celery Workers            │
│                    │  │  ┌──────────────────────────┐   │
│   - Users          │  │  │  Process Executions      │   │
│   - Workflows      │  │  │  - Document Processing   │   │
│   - Executions     │  │  │  - AI Operations         │   │
│   - Assets         │  │  │  - File Conversion       │   │
│   - Templates      │  │  └──────────────────────────┘   │
└────────────────────┘  └──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services / Libraries                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Ollama/     │  │  Whisper     │  │  Pandoc      │     │
│  │  OpenAI      │  │  (Audio)     │  │ (Convert)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PyMuPDF     │  │  PIL         │  │  Redis       │     │
│  │  (PDFs)      │  │  (Images)    │  │  (Cache)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Características Actuales ✅
- API REST con FastAPI
- Procesamiento asíncrono con Celery
- Base de datos relacional (PostgreSQL)
- Autenticación básica (email/password)
- Procesamiento de archivos (PDF, DOCX, imágenes, audio)
- IA generativa integrada (Ollama/OpenAI)
- Transcripción de audio (Whisper)
- Conversión de documentos (Pandoc)

---

## 🏛️ Arquitectura Ideal

### 1. Arquitectura de Microservicios (Escalable)

```
┌─────────────────────────────────────────────────────────────────┐
│                        CDN / CloudFront                         │
│                   (Static Assets + Cache)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────┐                       ┌──────────────┐
│  Web App     │                       │  Mobile App  │
│  (React SPA) │                       │  (React N.)  │
└──────┬───────┘                       └──────┬───────┘
       │                                       │
       └───────────────────┬───────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    API Gateway                                │
│              (Kong / AWS API Gateway)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Auth    │  │  Rate    │  │  Logging │  │  Routing │     │
│  │  JWT     │  │  Limit   │  │          │  │          │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌──────────────┐
│  API User   │ │  API Work   │ │  API Asset   │
│  Service    │ │  Service    │ │  Service     │
└──────┬──────┘ └──────┬──────┘ └──────┬───────┘
       │               │                │
       ▼               ▼                ▼
┌─────────────┐ ┌─────────────┐ ┌────────────────┐
│  Auth DB    │ │  Work DB    │ │  Storage S3    │
│  (Postgres) │ │  (Postgres) │ │  (MinIO/S3)    │
└─────────────┘ └─────────────┘ └────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│                  Message Queue                               │
│              (RabbitMQ / AWS SQS)                            │
└──────────┬──────────┬──────────┬──────────┬─────────────────┘
           │          │          │          │
           ▼          ▼          ▼          ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  Worker  │ │  Worker  │ │  Worker  │ │  Worker  │
    │  Doc     │ │  Image   │ │  Audio   │ │  Export  │
    │ Process  │ │  Edit    │ │  Trans   │ │  (PDF)   │
    └──────────┘ └──────────┘ └──────────┘ └──────────┘
           │          │          │          │
           └──────────┴──────────┴──────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    AI Services Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  OpenAI  │  │  Ollama  │  │  Whisper │  │  Vision  │     │
│  │  (GPT)   │  │  (Local) │  │  (Trans) │  │  (SDXL)  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### 2. Componentes Principales

#### **API Gateway** 🌐
- **Rol:** Punto de entrada único para todos los clientes
- **Funciones:**
  - Autenticación/Authorization (JWT)
  - Rate limiting por usuario/plan
  - Routing inteligente
  - Logging y monitoreo
  - API versioning

#### **Microservicios Core** 🔧

**1. User Service**
- Gestión de usuarios y autenticación
- Perfiles y preferencias
- Suscripciones y billing
- DB: PostgreSQL (users, subscriptions, payments)

**2. Workflow Service**
- CRUD de workflows
- Plantillas y templates
- Ejemplos de salida
- Variables y placeholders
- DB: PostgreSQL (workflows, templates, examples)

**3. Execution Service**
- Ejecución de workflows
- Gestión de estado (PENDING → IN_PROGRESS → DONE)
- Historial de ejecuciones
- DB: PostgreSQL (executions, logs)

**4. Asset Service**
- Gestión de archivos (upload/download)
- Conversión de formatos
- Storage distribuido (S3-compatible)
- CDN para delivery
- DB: PostgreSQL (assets metadata)
- Storage: MinIO / AWS S3

**5. AI Processing Service**
- Orquestación de tareas de IA
- Cola de procesamiento
- Balanceo de carga entre workers
- Queue: RabbitMQ / AWS SQS

**6. Notification Service**
- Notificaciones en tiempo real (WebSocket)
- Email notifications
- Push notifications (móvil)
- Message broker: Redis Pub/Sub

#### **Workers Especializados** ⚙️

**1. Document Worker**
- Procesamiento de PDFs/DOCX
- Extracción de texto (OCR)
- Análisis con IA

**2. Image Worker**
- Análisis de imágenes (Vision AI)
- Edición con IA (Stable Diffusion)
- Inpainting/Outpainting
- Redimensionamiento

**3. Audio Worker**
- Transcripción (Whisper)
- Análisis de audio
- Extracción de metadatos

**4. Export Worker**
- Conversión de formatos (Pandoc)
- Generación de PDFs
- Compresión de archivos

#### **Servicios de Soporte** 🛠️

**1. Analytics Service**
- Métricas de uso
- Dashboards
- Reportes ejecutivos
- DB: PostgreSQL + ClickHouse (analytics)

**2. Billing Service**
- Facturación automática
- Stripe/PayPal integration
- Gestión de créditos
- DB: PostgreSQL (payments, invoices)

**3. Admin Service**
- Panel administrativo
- Gestión de usuarios
- Configuración del sistema
- DB: PostgreSQL (config, admin_users)

---

## 🎯 Features y Roadmap

### Phase 1: MVP Actual ✅
- ✅ CRUD de workflows
- ✅ Ejecución de workflows
- ✅ Procesamiento de documentos (PDF, DOCX)
- ✅ Procesamiento de imágenes (OCR)
- ✅ Procesamiento de audio (Whisper)
- ✅ Plantillas con variables
- ✅ Generación de documentos
- ✅ Conversión de formatos

### Phase 2: Q1 2024 🚧
**Edición de Imágenes con IA**
- Inpainting/Outpainting
- Eliminación de objetos
- Mejora de calidad
- Filtros automáticos

**Integración con Servicios Externos**
- Google Drive
- Dropbox
- Slack notifications
- Email integration

**Mejoras en Workflows**
- Multi-step workflows
- Conditional logic
- Loop/repeat
- Parallel execution

### Phase 3: Q2 2024 📅
**Marketplace de Workflows**
- Comunidad de plantillas
- Ratings y reviews
- Compartir workflows
- Templates premium

**Analytics Avanzado**
- Dashboards personalizados
- Reportes de uso
- Métricas de productividad
- ROI calculator

**Integraciones Empresariales**
- Zapier integration
- API REST completa
- Webhooks
- SSO (Single Sign-On)

### Phase 4: Q3-Q4 2024 🚀
**Colaboración en Equipo**
- Multi-user workflows
- Permisos y roles
- Comentarios en documentos
- Version control

**Machine Learning Personalizado**
- Fine-tuning de modelos
- Custom AI agents
- Aprendizaje del usuario
- Recomendaciones inteligentes

**Mobile Apps**
- iOS app
- Android app
- Offline mode
- Mobile-first features

---

## 🛠️ Stack Tecnológico

### Recomendación: Mantener FastAPI vs Django

#### **FastAPI (Recomendado)** ✅

**Ventajas:**
- ✅ **Performance superior:** Async/await nativo, 3x más rápido que Django
- ✅ **Type hints:** Validación automática con Pydantic
- ✅ **Documentación automática:** OpenAPI/Swagger incluido
- ✅ **Modo async nativo:** Perfecto para I/O bound operations (DB, AI APIs)
- ✅ **Moderno:** Basado en ASGI (WebSockets nativos)
- ✅ **Ligero:** Ideal para microservicios
- ✅ **Curva de aprendizaje:** Más simple para APIs

**Mejor para:**
- APIs REST/gRPC
- Microservicios
- Alta concurrencia
- Real-time (WebSockets)
- Integración con servicios externos

**Desventajas:**
- ❌ Admin panel no incluido (pero se puede usar FastAPI Admin)
- ❌ ORM menos maduro (SQLAlchemy es excelente)
- ❌ Ecosistema más pequeño que Django

#### **Django** 🤔

**Ventajas:**
- ✅ Admin panel incluido
- ✅ ORM muy maduro
- ✅ Ecosistema enorme
- ✅ Django REST Framework
- ✅ Better for monoliths

**Desventajas:**
- ❌ Más lento que FastAPI
- ❌ Menos efficient para async
- ❌ Más verbose
- ❌ Overkill para APIs puras

### **Recomendación Final: FastAPI** ✅

Para MindDocs, **FastAPI es la mejor opción** porque:
1. Arquitectura de microservicios requiere APIs ligeras y rápidas
2. Procesamiento asíncrono de archivos requiere async nativo
3. Multiple workers requieren eficiencia en recursos
4. Real-time notifications (WebSockets) son críticas
5. Integración con múltiples servicios externos (AI, Storage, etc.)

**Si necesitas admin panel:** Usa FastAPI Admin o un frontend separado.

---

## 🌐 Stack Tecnológico Detallado

### Backend
```yaml
API Framework:
  - FastAPI 0.104+ (async, WebSockets)
  - Uvicorn (ASGI server)
  - Gunicorn (production)

Database:
  - PostgreSQL 15+ (primary)
  - Redis 7+ (cache, queues, pub/sub)
  - ClickHouse (analytics, opcional)

Message Queue:
  - RabbitMQ (managed) o AWS SQS (cloud)
  - Celery (task queue)

Storage:
  - MinIO (self-hosted) o AWS S3 (cloud)
  - CloudFront / CloudFlare (CDN)

Authentication:
  - JWT (FastAPI-JWT)
  - OAuth2 (Google, Microsoft)
  - SSO (SAML, opcional)

Monitoring:
  - Prometheus + Grafana
  - Sentry (error tracking)
  - ELK Stack (logs)
```

### AI/ML
```yaml
LLM Providers:
  - OpenAI GPT-4 (production)
  - Ollama (local, dev/testing)
  - Anthropic Claude (backup)

Vision:
  - Stable Diffusion XL (image generation/editing)
  - Replicate API (managed SD)
  - OpenAI DALL-E 3 (backup)

Audio:
  - Whisper (OpenAI, local)
  - AssemblyAI (managed, backup)

Document Processing:
  - PyMuPDF (PDF)
  - python-docx (DOCX)
  - Pandoc (conversions)
  - Tesseract OCR (fallback)
```

### Frontend
```yaml
Framework:
  - React 18+ (SPA)
  - TypeScript
  - Vite (build tool)
  - TailwindCSS

State Management:
  - Zustand o Redux Toolkit
  - React Query (server state)

UI Libraries:
  - shadcn/ui (components)
  - React Hook Form
  - Zod (validation)

Real-time:
  - Socket.IO Client
  - Redis Pub/Sub (backend)
```

### DevOps & Infrastructure
```yaml
Containerization:
  - Docker
  - Docker Compose (local)

Orchestration:
  - Kubernetes (production)
  - Helm (K8s charts)

CI/CD:
  - GitHub Actions
  - GitLab CI (alternativo)

Infrastructure as Code:
  - Terraform
  - AWS CDK (alternativo)
```

---

## 🚀 Estrategia de Despliegue

### Recomendación: AWS ECS (Containers) > EC2

#### **¿Por qué ECS en lugar de EC2?**

**AWS ECS (Elastic Container Service)** ✅

**Ventajas:**
- ✅ **Escalado automático:** Auto-scaling groups configurables
- ✅ **Gestión simplificada:** Sin necesidad de gestionar servidores
- ✅ **Alto disponibilidad:** Multi-AZ automático
- ✅ **Rolling updates:** Zero-downtime deployments
- ✅ **Logs centralizados:** CloudWatch integrado
- ✅ **Cost-effective:** Solo pagas por recursos usados
- ✅ **Service discovery:** DNS automático entre servicios
- ✅ **Load balancing:** ALB integrado
- ✅ **Secretos:** AWS Secrets Manager
- ✅ **Fargate:** Serverless (sin EC2)

**Desventajas:**
- ❌ Curva de aprendizaje más alta
- ❌ Vendor lock-in AWS
- ❌ Costo ligeramente mayor

**AWS EC2** 🤔

**Ventajas:**
- ✅ Control total
- ✅ Configuración personalizada
- ✅ Más económico para uso constante

**Desventajas:**
- ❌ Gestión manual del escalado
- ❌ Balanceador de carga manual
- ❌ Updates manuales
- ❌ Menos resiliente
- ❌ Más tiempo de operación

### **Arquitectura en AWS ECS** 🏗️

```
┌─────────────────────────────────────────────────────────────┐
│                      CloudFront CDN                         │
│              (Static Assets + Caching)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   AWS API Gateway                           │
│              (Rate Limiting + Auth)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────┐                 ┌──────────────┐
│  ECS Service │                 │  ECS Service │
│  API Gateway │                 │  Workers     │
│  (Fargate)   │                 │  (Fargate)   │
│  3 replicas  │                 │  2-10 tasks  │
└──────┬───────┘                 └──────┬───────┘
       │                                │
       └────────────┬───────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
┌──────────────┐      ┌──────────────┐
│  RDS         │      │  ElastiCache │
│  (Postgres)  │      │  (Redis)     │
│  2 Multi-AZ  │      │  Cluster     │
└──────────────┘      └──────────────┘
         │
         ▼
┌──────────────┐
│  S3 Bucket   │
│  (Files)     │
│  + Glacier   │
└──────────────┘
```

### Configuración ECS Fargate

```yaml
# ecs-cluster.yaml
Cluster: minddocs-cluster
Launch Type: Fargate
Capacity: 3 services

Services:
  - API Gateway:
      Tasks: 3 (multi-AZ)
      CPU: 1024 (1 vCPU)
      Memory: 2048 MB (2 GB)
      Auto Scaling: 3-10 tasks
  
  - Workers:
      Tasks: 2-10 (dynamic)
      CPU: 2048 (2 vCPU)
      Memory: 4096 MB (4 GB)
      Auto Scaling: 2-20 tasks
  
  - AI Processing:
      Tasks: 2-5
      CPU: 4096 (4 vCPU)
      Memory: 8192 MB (8 GB)
      Auto Scaling: 2-10 tasks
```

### Auto-scaling Policy

```yaml
Triggers:
  - CPU > 70%: Scale up +1
  - Memory > 80%: Scale up +1
  - Queue > 100 tasks: Scale up +2
  - CPU < 30%: Scale down -1

Cooldown: 300 seconds
Max Instances: 20
Min Instances: 2
```

### Costo Estimado (AWS ECS + Fargate)

**Desarrollo/Testing:**
- API Gateway: 2 tasks × $0.04/hour × 730 hours = $58/mes
- Workers: 2 tasks × $0.08/hour × 730 hours = $116/mes
- RDS: t3.medium multi-AZ = $150/mes
- S3: ~$20/mes
- Data Transfer: ~$30/mes
**Total: ~$374/mes**

**Producción:**
- API Gateway: 3 tasks × $0.04/hour × 730 hours = $87/mes
- Workers: 5 tasks × $0.08/hour × 730 hours = $292/mes
- AI Workers: 2 tasks × $0.16/hour × 730 hours = $233/mes
- RDS: t3.large multi-AZ = $300/mes
- S3: ~$100/mes
- CloudFront: ~$50/mes
- Data Transfer: ~$100/mes
**Total: ~$1,162/mes**

**Nota:** Costos pueden optimizarse con Reserved Instances (-30%) y Spot Instances (-70%).

---

## 📈 Escalabilidad

### Horizontal Scaling
- **API Services:** Replicar contenedores según demanda
- **Workers:** Escalar según cola de tareas (RabbitMQ)
- **Database:** Read replicas para queries pesadas
- **CDN:** Cache de assets estáticos

### Vertical Scaling
- **AI Processing:** Workers con más CPU/RAM para tareas pesadas
- **Database:** Upgrade a instancias más grandes según necesidad

### Performance Optimizations
- Redis caching de queries frecuentes
- Connection pooling (SQLAlchemy)
- Async processing para I/O bound tasks
- Batch processing para múltiples archivos
- Pagination en listados grandes

---

## 🔒 Seguridad

### Authentication & Authorization
- JWT tokens con expiración corta (15 min)
- Refresh tokens
- OAuth2 con Google/Microsoft
- Role-based access control (RBAC)
- API keys para integraciones

### Data Security
- Encriptación en tránsito (TLS 1.3)
- Encriptación en reposo (S3, RDS)
- Secrets management (AWS Secrets Manager)
- Regular security audits

### Compliance
- GDPR compliance
- SOC 2 Type II (futuro)
- HIPAA compliance (para salud)
- ISO 27001 (futuro)

---

## 💡 Recomendaciones Finales

### Arquitectura
1. ✅ **Mantén FastAPI** - Ideal para microservicios
2. ✅ **Migra a ECS/Fargate** - Mejor escalabilidad que EC2
3. ✅ **Implementa microservicios gradualmente** - Comienza con 2-3 servicios
4. ✅ **API Gateway** - Punto de entrada unificado
5. ✅ **Message Queue** - Desacopla procesamiento asíncrono

### Desarrollo
1. **API Versioning** - `/v1/`, `/v2/`
2. **Documentación** - OpenAPI/Swagger
3. **Testing** - Unit tests + Integration tests
4. **Monitoring** - Prometheus + Grafana
5. **Error tracking** - Sentry

### Negocio
1. **MVP primero** - Luego agregar features
2. **Freemium model** - Plan gratuito con límites
3. **Marketplace** - Comunidad de workflows
4. **Integrations** - Zapier, n8n, Make
5. **White-label** - Para empresas grandes

### Tecnología
1. **Managed services** - RDS, ElastiCache, S3
2. **Container orchestration** - ECS/Kubernetes
3. **CI/CD automatizado** - GitHub Actions
4. **Infrastructure as Code** - Terraform
5. **Monitoring** - CloudWatch, Datadog

---

## 📚 Referencias
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Microservices Patterns](https://microservices.io/patterns/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Documento creado:** 2024-01-XX  
**Versión:** 1.0  
**Autor:** MindDocs Team
