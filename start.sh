#!/bin/bash

VENV_DIR="venv"
REDIS_FLAG=false

# --- PARSEO DE ARGUMENTOS ---
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -r|--redis)
            if [[ "$2" == "true" ]]; then
                REDIS_FLAG=true
            fi
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# --- DETECTAR SISTEMA OPERATIVO ---
if [[ "$OSTYPE" == "msys" ]]; then
    ACTIVATE_CMD="$VENV_DIR/Scripts/activate"
else
    ACTIVATE_CMD="$VENV_DIR/bin/activate"
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

export ENVIRONMENT=prod

echo "🚀 Iniciando la aplicación FastAPI..."
python main.py
