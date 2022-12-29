from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    mqtt_host: str
    mqtt_port: int
    mqtt_keep_alive: int = 60
    mqtt_topic: str

    order_expiry: int = 60

    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
