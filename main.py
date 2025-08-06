import os
from datetime import datetime
import socketio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from starlette.exceptions import HTTPException as StarletteHTTPException


from server.utils.printer import Printer
from server.routes import router
from server.managers.socket_server import sio
from server.managers.notifications import (
    redis_to_socketio_bridge,
    redis_to_socketio_bridge_notifications,
)

printer = Printer("MAIN")
ENVIRONMENT = os.getenv("ENVIRONMENT", "prod").lower().strip()

printer.green("🚀 Iniciando aplicación en modo: ", ENVIRONMENT)
# Crear carpetas necesarias
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/documents", exist_ok=True)
os.makedirs("uploads/documents/read", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    printer.green("Iniciando aplicación, hora: ", datetime.now())
    task = asyncio.create_task(redis_to_socketio_bridge())
    task_notifications = asyncio.create_task(redis_to_socketio_bridge_notifications())
    yield
    task.cancel()
    task_notifications.cancel()

    try:
        await task
        await task_notifications
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

# Configuración de ORIGINS
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if raw_origins != "*":
    ALLOWED_ORIGINS = [
        o if o.startswith("http") else f"http://{o}"
        for o in map(str.strip, raw_origins.split(","))
    ]
else:
    printer.red(
        "PELIGRO: ALLOWED_ORIGINS es *, cualquier origen puede acceder a la API."
    )
    if ENVIRONMENT == "prod":
        raise Exception("ALLOWED_ORIGINS es * en producción")
    ALLOWED_ORIGINS = "*"


raw_ips = os.getenv("ALLOWED_IPS", "")
if raw_ips != "":
    ALLOWED_IPS = [ip.strip() for ip in raw_ips.split(",")]
else:
    ALLOWED_IPS = []

printer.green("ALLOWED_ORIGINS: ", ALLOWED_ORIGINS)
printer.green("ALLOWED_IPS: ", ALLOWED_IPS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != "*" else ["*"],
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)


@app.middleware("http")
async def auth_and_cors(request: Request, call_next):
    # printer.green("Receiving a request. Headers: ", request.headers)
    origin = request.headers.get("origin")
    if origin:
        if ALLOWED_ORIGINS != "*" and origin not in ALLOWED_ORIGINS:
            printer.yellow(f"Origin '{origin}' no permitido.")
            return JSONResponse(
                status_code=403, content={"detail": f"Origin '{origin}' no permitido."}
            )
    else:
        client_ip = request.client.host
        if len(ALLOWED_IPS) > 0 and client_ip not in ALLOWED_IPS:
            printer.yellow(f"IP '{client_ip}' no permitida.")
            return JSONResponse(
                status_code=403, content={"detail": f"IP '{client_ip}' no permitida."}
            )

    # CHECK_AUTH = ENVIRONMENT == "prod"
    # CHECK_AUTH = False
    # if CHECK_AUTH:
    #     auth: str = request.headers.get("Authorization", "")
    #     if not auth.startswith("Bearer "):
    #         printer.yellow("No se encontró el token en el header")
    #         return JSONResponse(
    #             status_code=401,
    #             content={"detail": "Missing or malformed Authorization header."},
    #         )
    #     token = auth.split(" ", 1)[1]

    #     validate_url = os.getenv(
    #         "TOKEN_VALIDATION_URL",
    #         "https://declaraciones.pjedomex.gob.mx/declaraciones/gestion",
    #     )

    #     payload = {"access_token": token}
    #     printer.yellow(f"Validando token en {validate_url}...", payload)
    #     async with httpx.AsyncClient(timeout=5) as client:
    #         headers = {"Content-Type": "application/x-www-form-urlencoded"}
    #         body = urlencode(payload)
    #         resp = await client.post(validate_url, data=body, headers=headers)
    #         printer.yellow("Respuesta del servidor:", resp.text)
    #     if resp.status_code != 200:
    #         printer.error(f"Token inválido o expirado: {resp.text}")
    #         return JSONResponse(
    #             status_code=401, content={"detail": "Invalid or expired token."}
    #         )
    # else:
    #     printer.yellow("No se validó el token")
    printer.green("Una solicitud fue permitida con éxito a las ", datetime.now())
    return await call_next(request)


app.include_router(router)

app.mount("/socket.io", sio_asgi_app)
app.mount(
    "/assets", StaticFiles(directory="client/dist/assets", html=True), name="client"
)


@app.get("/{full_path:path}")
async def spa_catch_all(full_path: str):
    printer.red("spa_catch_all: ", full_path)
    # Puedes agregar filtros si quieres omitir /api, /uploads, etc.
    if full_path.startswith(("api/", "socket.io", "uploads/")):
        raise StarletteHTTPException(status_code=404, detail="Not Found")
    return FileResponse("client/dist/index.html")


PORT = int(os.getenv("PORT", 8006))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
