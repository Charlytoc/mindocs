from celery import Celery
import os
import platform
import ssl

# Config Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")  # Debe ser 6379 para ElastiCache Valkey
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_USE_TLS = os.getenv("REDIS_USE_TLS", "false").lower() == "true"
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

if REDIS_PASSWORD:
    URL_PREFIX = "rediss" if REDIS_USE_TLS else "redis"
    REDIS_URL = f"{URL_PREFIX}://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    URL_PREFIX = "rediss" if REDIS_USE_TLS else "redis"
    REDIS_URL = f"{URL_PREFIX}://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

celery = Celery(
    "worker_demandas",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# SSL options si usas TLS
if REDIS_USE_TLS:
    ssl_options = {
        "ssl_cert_reqs": ssl.CERT_NONE,  # Para no validar certificados (útil para ElastiCache)
        # Si quieres validar el certificado, usa ssl.CERT_REQUIRED y proporciona "ssl_ca_certs"
    }
    celery.conf.broker_use_ssl = ssl_options
    celery.conf.redis_backend_use_ssl = ssl_options

# Ajuste dinámico del pool según el sistema operativo
if platform.system() == "Windows":
    celery.conf.worker_pool = "threads"
    celery.conf.worker_concurrency = int(os.getenv("CELERY_CONCURRENCY", "4"))
else:
    celery.conf.worker_pool = os.getenv("CELERY_POOL", "prefork")
    celery.conf.worker_concurrency = int(os.getenv("CELERY_CONCURRENCY", "8"))
