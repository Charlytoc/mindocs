#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
import socket
from pathlib import Path
from time import sleep
from dotenv import load_dotenv

# ───────────────────────────────────────────────
# 🧱 CONFIGURACIÓN
# ───────────────────────────────────────────────
POSTGRES_CONTAINER_NAME = "postgres_demandas"
POSTGRES_IMAGE = "postgres:16.9"  # Fija la versión solicitada

# ───────────────────────────────────────────────
# 📦 CARGAR VARIABLES DE ENTORNO
# ───────────────────────────────────────────────
env_path = Path(".env")
if not env_path.exists():
    print("❌ No se encontró archivo .env")
    sys.exit(1)

load_dotenv(dotenv_path=env_path)

# Variables requeridas
env_vars = {
    "POSTGRES_VOLUME_HOST": os.getenv("POSTGRES_VOLUME_HOST"),
    "POSTGRES_DB": os.getenv("POSTGRES_DB"),
    "POSTGRES_USER": os.getenv("POSTGRES_USER"),
    "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    "POSTGRES_HOST_PORT": os.getenv("POSTGRES_HOST_PORT"),
    "POSTGRES_CONTAINER_PORT": os.getenv("POSTGRES_CONTAINER_PORT"),
    # Nueva variable, con valor por defecto
    "POSTGRES_MAX_CONNECTIONS": os.getenv("POSTGRES_MAX_CONNECTIONS", "250"),
}

missing = [k for k, v in env_vars.items() if not v and k != "POSTGRES_MAX_CONNECTIONS"]
if missing:
    print(f"❌ Faltan variables de entorno requeridas: {', '.join(missing)}")
    sys.exit(1)

# Asignar variables
POSTGRES_VOLUME_HOST = env_vars["POSTGRES_VOLUME_HOST"]
POSTGRES_DB = env_vars["POSTGRES_DB"]
POSTGRES_USER = env_vars["POSTGRES_USER"]
POSTGRES_PASSWORD = env_vars["POSTGRES_PASSWORD"]
POSTGRES_HOST_PORT = env_vars["POSTGRES_HOST_PORT"]
POSTGRES_CONTAINER_PORT = env_vars["POSTGRES_CONTAINER_PORT"]
POSTGRES_MAX_CONNECTIONS = env_vars["POSTGRES_MAX_CONNECTIONS"]

# Validar que POSTGRES_MAX_CONNECTIONS sea un entero positivo
try:
    max_conn = int(POSTGRES_MAX_CONNECTIONS)
    if max_conn < 1:
        raise ValueError
except ValueError:
    print("❌ POSTGRES_MAX_CONNECTIONS debe ser un entero positivo.")
    sys.exit(1)

# ───────────────────────────────────────────────
# ⚙️ VERIFICAR DOCKER
# ───────────────────────────────────────────────
if not shutil.which("docker"):
    print("❌ Docker no está instalado o no está en el PATH")
    sys.exit(1)


# ───────────────────────────────────────────────
# 🛡️ VERIFICAR PUERTO DISPONIBLE
# ───────────────────────────────────────────────
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", int(port))) == 0


if is_port_in_use(POSTGRES_HOST_PORT):
    print(
        f"❌ El puerto {POSTGRES_HOST_PORT} ya está en uso. Elige otro o libera el puerto."
    )
    sys.exit(1)

# ───────────────────────────────────────────────
# 📁 CREAR VOLUMEN LOCAL SI NO EXISTE
# ───────────────────────────────────────────────
print(f"📁 Verificando volumen en {POSTGRES_VOLUME_HOST}")
volume_path = Path(POSTGRES_VOLUME_HOST).resolve()
try:
    volume_path.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"❌ Error creando el volumen: {e}")
    sys.exit(1)

# Git Bash fix (Windows path)
if os.name == "nt":
    volume_path_str = str(volume_path).replace("\\", "/").replace("C:", "/c")
else:
    volume_path_str = str(volume_path)

# ───────────────────────────────────────────────
# 🧨 LIMPIAR CONTENEDOR ANTERIOR
# ───────────────────────────────────────────────
try:
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
except subprocess.CalledProcessError as e:
    print(f"❌ Error al listar contenedores Docker: {e}")
    sys.exit(1)

if POSTGRES_CONTAINER_NAME in result.stdout.splitlines():
    print(f"🧨 Eliminando contenedor previo: {POSTGRES_CONTAINER_NAME}")
    try:
        subprocess.run(["docker", "rm", "-f", POSTGRES_CONTAINER_NAME], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error eliminando el contenedor previo: {e}")
        sys.exit(1)

# ───────────────────────────────────────────────
# 🐘 CREAR NUEVO CONTENEDOR POSTGRESQL
# ───────────────────────────────────────────────
print(
    f"🚀 Iniciando PostgreSQL {POSTGRES_IMAGE} en puerto {POSTGRES_HOST_PORT} (max_connections={POSTGRES_MAX_CONNECTIONS})"
)
try:
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            POSTGRES_CONTAINER_NAME,
            "-e",
            f"POSTGRES_DB={POSTGRES_DB}",
            "-e",
            f"POSTGRES_USER={POSTGRES_USER}",
            "-e",
            f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}",
            "-e",
            "POSTGRES_INITDB_ARGS=--auth-host=md5",
            "-e",
            f"POSTGRES_MAX_CONNECTIONS={POSTGRES_MAX_CONNECTIONS}",
            "-p",
            f"{POSTGRES_HOST_PORT}:{POSTGRES_CONTAINER_PORT}",
            "-v",
            f"{volume_path_str}:/var/lib/postgresql/data",
            POSTGRES_IMAGE,
        ],
        check=True,
    )
except subprocess.CalledProcessError as e:
    print(f"❌ Error al crear el contenedor de PostgreSQL: {e}")
    sys.exit(1)

print("⏳ Esperando a que PostgreSQL inicie…")
sleep(5)


# ───────────────────────────────────────────────
# ✅ CONEXIÓN FINAL
# ───────────────────────────────────────────────
def set_database_urls_in_env():
    sync_url = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@127.0.0.1:{POSTGRES_HOST_PORT}/{POSTGRES_DB}"
    )
    async_url = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@127.0.0.1:{POSTGRES_HOST_PORT}/{POSTGRES_DB}"
    )

    env_lines = []
    found_sync = False
    found_async = False

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("DATABASE_URL="):
                env_lines.append(f"DATABASE_URL={sync_url}\n")
                found_sync = True
            elif line.strip().startswith("ASYNC_DATABASE_URL="):
                env_lines.append(f"ASYNC_DATABASE_URL={async_url}\n")
                found_async = True
            else:
                env_lines.append(line)

    if not found_sync:
        env_lines.append(f"\nDATABASE_URL={sync_url}\n")
    if not found_async:
        env_lines.append(f"ASYNC_DATABASE_URL={async_url}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(env_lines)

    print("✅ DATABASE_URL y ASYNC_DATABASE_URL actualizados/agregados en .env")

set_database_urls_in_env()
