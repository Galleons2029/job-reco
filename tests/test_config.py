import logging
from unittest import TestCase


class TestSettings(TestCase):
    def test_config(self):
        from config import Settings
        log = logging.getLogger("wuhu")
        log.info("wuhif")
        self.assertEqual(Settings().MONGO_DATABASE_NAME, 'admin')
