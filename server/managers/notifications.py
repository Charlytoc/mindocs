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
    await pubsub.subscribe("workflow_updates")

    try:
        async for message in pubsub.listen():
            # printer.green("Message received: ", message)
            if message["type"] == "message":
                printer.green("Message received in workflow_updates channel")
                data = json.loads(message["data"])
                # printer.green("Message parsed")

                workflow_id = data["workflow_execution_id"]
                # printer.green(f"Case ID: {case_id}")

                await sio.emit("workflow_update", data, room=f"workflow_{workflow_id}")
                printer.green(
                    f"Message sent to socketio to room: workflow_{workflow_id}"
                )
    finally:
        await pubsub.unsubscribe("workflow_updates")
        await pubsub.close()
        await r.close()


async def redis_to_socketio_bridge_notifications():
    r = redis.Redis.from_url(
        f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/{os.getenv('REDIS_DB')}"
    )
    printer.green("Redis connected")
    pubsub = r.pubsub()
    await pubsub.subscribe("notifications")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                not_id = data.get("not_id")
                if not_id:
                    await sio.emit(f"notification_{not_id}", data)
    finally:
        await pubsub.unsubscribe("notifications")
        await pubsub.close()
        await r.close()
