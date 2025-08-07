import os
import redis
from dotenv import load_dotenv
from server.utils.printer import Printer

load_dotenv()

printer = Printer("REDIS_CACHE")


class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD", None),
            decode_responses=True,
            ssl=os.getenv("REDIS_USE_TLS", "false").lower() == "true",
        )

    # ------------ Strings ------------
    def exists(self, key: str) -> bool:
        return self.client.exists(key) == 1

    def get(self, key: str) -> str | None:
        return self.client.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.client.set(key, value, ex=ex)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def flush_all(self):
        self.client.flushall()

    def hset(self, name: str, key: str, value: str) -> None:
        self.client.hset(name, key, value)

    def hget(self, name: str, key: str) -> str | None:
        return self.client.hget(name, key)

    def hdel(self, name: str, key: str) -> None:
        self.client.hdel(name, key)

    def hgetall(self, name: str) -> dict:
        return self.client.hgetall(name)

    def publish(self, channel: str, message: str) -> None:
        printer.green(f"Publishing message to channel: {channel}")
        self.client.publish(channel, message)
        printer.green(f"Message published to channel: {channel}")


redis_client = RedisCache()
