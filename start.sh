#!/bin/bash

VENV_DIR="venv"
REDIS_FLAG=false
MODE=""
WORKERS=""
APP_MODULE="main:app"
PORT="${PORT:-8000}"

# --- PARSEO DE ARGUMENTOS ---
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -r|--redis)
            if [[ "$2" == "true" ]]; then
                REDIS_FLAG=true
            fi
            shift 2
            ;;
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# --- PEDIR MODO SI NO SE ESPECIFICA ---
if [[ -z "$MODE" ]]; then
    read -p "¿Modo de ejecución? (dev/prod): " MODE
    MODE="${MODE,,}"  # minusculas
fi

# --- VALIDAR MODO ---
if [[ "$MODE" != "dev" && "$MODE" != "prod" ]]; then
    echo "❌ Modo inválido: $MODE. Debe ser 'dev' o 'prod'."
    exit 1
fi

# --- PEDIR WORKERS SI NO SE ESPECIFICA Y ES PROD ---
if [[ "$MODE" == "prod" && -z "$WORKERS" ]]; then
    read -p "¿Cuántos workers para Gunicorn? (default: 2): " WORKERS
    WORKERS="${WORKERS:-2}"
fi

# --- DETECTAR SISTEMA OPERATIVO ---
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    ACTIVATE_CMD="$VENV_DIR/Scripts/activate"
    IS_WINDOWS=true
else
    ACTIVATE_CMD="$VENV_DIR/bin/activate"
    IS_WINDOWS=false
fi

echo "🔍 Verificando entorno virtual..."
if [ ! -d "$VENV_DIR" ]; then
    echo "📁 No se encontró un entorno virtual. Creando uno nuevo..."
    python3 -m venv $VENV_DIR
    echo "✅ Entorno virtual creado."
else
    echo "✅ Se encontró el entorno virtual existente."
fi

echo "⚙️ Activando el entorno virtual..."
source $ACTIVATE_CMD
echo "✅ Entorno virtual activado."

echo "📦 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt -q
echo "✅ Dependencias instaladas."

# --- SECCIÓN REDIS SOLO SI REDIS_FLAG ES TRUE ---
if [ "$REDIS_FLAG" = true ]; then
    echo "🚀 Verificando estado de Redis (contenedor: redis_server_sentencias)..."
    if [ "$(docker ps -aq -f name=redis_server_sentencias)" ]; then
        if [ "$(docker ps -q -f name=redis_server_sentencias)" ]; then
            echo "✅ Redis ya está corriendo."
        else
            echo "🔄 Redis existe pero está detenido. Iniciando..."
            docker start redis_server_sentencias
        fi
    else
        echo "📦 Redis no existe. Creando contenedor con configuración segura..."
        docker run -d \
            --name redis_server_sentencias \
            -p 6380:6379 \
            redis \
            redis-server --bind 0.0.0.0 --protected-mode no
    fi
else
    echo "ℹ️  Flag de Redis desactivada. No se iniciará/verificará Redis."
fi

export ENVIRONMENT="$MODE"

echo "⚡ Lanzando la aplicación FastAPI..."
if [ "$MODE" = "prod" ]; then
    if [ "$IS_WINDOWS" = true ]; then
        echo "⚠️ Windows detectado: iniciando FastAPI con Uvicorn (Gunicorn no es compatible)..."
        uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT
    else
        echo "🐧 Linux detectado: iniciando FastAPI con Gunicorn + UvicornWorker ($WORKERS workers)..."
        gunicorn $APP_MODULE -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers $WORKERS
    fi
else
    echo "🛠️ Modo desarrollo: iniciando FastAPI con Uvicorn en modo recarga..."
    uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT --reload
fi
