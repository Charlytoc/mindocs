#!/bin/bash

VENV_DIR="venv"

# Detectar sistema operativo
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

export ENVIRONMENT=prod

echo "🚀 Iniciando la aplicación FastAPI..."
python main.py
