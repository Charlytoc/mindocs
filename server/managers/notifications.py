import os
import json
from server.managers.socket_server import sio
from server.utils.printer import Printer
import redis.asyncio as redis

printer = Printer("NOTIFICATIONS")

async def redis_to_socketio_bridge():
    r = redis.Redis.from_url(
        f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/{os.getenv('REDIS_DB')}"
    )

    printer.green("Redis connected")

    pubsub = r.pubsub()
    await pubsub.subscribe("case_updates")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                # printer.green("Message received")
                data = json.loads(message["data"])
                # printer.green("Message parsed")

                case_id = data["case_id"]
                # printer.green(f"Case ID: {case_id}")

                await sio.emit("case_update", data, room=f"case_{case_id}")
    finally:
        await pubsub.unsubscribe("case_updates")
        await pubsub.close()
        await r.close()
