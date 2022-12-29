import logging

from worker.consumers.VernemqConsumer import VernemqConsumer
from common.config.logging import get_logging_config
from common.config.settings import get_settings
from common.domain.manager import Manager

get_logging_config()

logger = logging.getLogger(__name__)

manager = Manager()


def handler(message: dict) -> None:
    logger.info("received message", message)
    manager.stock_update(stock_id=message["stock_id"],
                         name=message["name"],
                         price=message["price"],
                         availability=message["availability"])


if __name__ == "__main__":
    settings = get_settings()
    consumer = VernemqConsumer(topic=settings.mqtt_topic,
                               handler=handler,
                               host=settings.mqtt_host,
                               port=settings.mqtt_port,
                               keep_alive=settings.mqtt_keep_alive)
    consumer.connect()
