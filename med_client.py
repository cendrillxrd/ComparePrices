import logging

import pandas as pd
import requests

from logging_config import setup_logging
from config import BASE_URLS

setup_logging()
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").propagate = False


class MedClient:
    def __init__(self):
        self.url = BASE_URLS['med']

    def _make_request(self, url):
        logger.info(f'Выполнение запроса по адресу {self.url}')
        response = requests.get(url)
        return response

    def get_prices(self):
        url = self.url
        prices = self._make_request(url)
        return prices
