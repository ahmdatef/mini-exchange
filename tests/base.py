import os
import sqlite3 as sqlite
from typing import Any
from unittest import TestCase

from common.config.settings import get_settings


class SqliteTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        os.environ["MQTT_TOPIC"] = "topic"
        os.environ["MQTT_HOST"] = "host"
        os.environ["MQTT_PORT"] = "0"

        os.environ["PERSISTENCE_MODULE"] = "eventsourcing.sqlite"
        os.environ["SQLITE_DBNAME"] = "eventsourcing.sqlite"
        os.environ["SQLITE_LOCK_TIMEOUT"] = "10"

        connection = sqlite.connect('eventsourcing.sqlite')
        connection.execute('DROP TABLE IF EXISTS stored_events')
        connection.execute('DROP TABLE IF EXISTS stored_snapshots')
        connection.execute('DROP TABLE IF EXISTS tracking')
        connection.close()

    def tearDown(self) -> None:
        super().tearDown()
        get_settings.cache_clear()
        os.environ.clear()

    def override_setting(self, key: str, value: Any) -> None:
        get_settings.cache_clear()
        os.environ[key.upper()] = str(value)
