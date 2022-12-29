import logging
import time
from typing import Callable

from paho.mqtt import client as mqtt

import ast

from common.consumers.Consumer import Consumer

logger = logging.getLogger(__name__)


class VernemqConsumer(Consumer):
    def __init__(self, topic: str, handler: Callable[[dict], None], host: str, port: int, keep_alive: int):
        self._client = mqtt.Client()

        def on_connect(client, *_):
            logger.info('connected successfully', client)
            client.subscribe(topic)

        self._client.on_connect = on_connect
        self._client.on_message = lambda _, __, msg: handler(ast.literal_eval(msg.payload.decode('utf-8')))

        self._host = host
        self._port = port
        self._keep_alive = keep_alive

        self._connection_retries = 5

    def connect(self) -> None:
        try:
            logger.info("trying to connect")
            self._client.connect(self._host, self._port, self._keep_alive)
            self._client.loop_forever()
        except ConnectionRefusedError as e:
            if self._connection_retries > 0:
                logger.warning("retrying to reconnect in 3 seconds")
                self._connection_retries -= 1
                time.sleep(3)
                self.connect()
            else:
                logger.exception("failed to connect to vernemq after 5 retries")
                raise e

    def disconnect(self, **kwargs) -> None:
        self._client.disconnect()
