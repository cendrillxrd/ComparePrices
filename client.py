from abc import ABC, abstractmethod
import time
import logging
from typing import Dict, Literal, Optional

import requests

from config import API_KEYS, BASE_URLS
from strategies.request_strategies import RequestStrategy
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").propagate = False


class Client(ABC):
    @abstractmethod
    def make_request(self, **kwargs):
        pass

    @abstractmethod
    def get_data(self):
        pass


class WildberriesAPIClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS
        self.api_key = API_KEYS
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.__strategy = None

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def make_request(self, method: Literal['GET', 'POST'],
                     api_type: Literal['Analytics_Statistics_API_KEY', 'Price_discount_API_KEY'],
                     url_key: Literal['seller-analytics', 'discounts-prices'],
                     endpoint: str,
                     params: Optional[Dict] = None,
                     payload: Optional[Dict] = None,
                     retries: int = 5):
        url = f'{self.base_url[url_key]}{endpoint}'
        logger.info(f'Выполнение запроса по адресу {url}')

        for attempt in range(retries):
            self.session.headers.update({'Authorization': self.api_key[api_type]})
            response = self.session.request(method=method,
                                            url=url,
                                            params=params,
                                            json=payload,
                                            timeout=10)
            logger.info(f'Запрос выполнен успешно')
            try:
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as err:
                logger.info(f'Запрос не удался, ошибка {err.response.status_code}'
                            f'Попытка {attempt + 1}/{retries}')
                if err.response.status_code in (429, 500, 502, 503, 504):
                    wait_time = min(2 ** attempt, 10)
                    logger.debug(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                raise

            except requests.exceptions.RequestException as err:
                logger.info(f'Запрос не удался, ошибка {err.response.status_code}')
                if attempt == retries - 1:
                    raise err
                time.sleep(1)

        return None

    def get_data(self, **kwargs):
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self)


class MedClient(Client):
    def __init__(self):
        self.url = BASE_URLS['med']

    def make_request(self):
        logger.info(f'Выполнение запроса по адресу {self.url}')
        response = requests.get(self.url)
        return response

    def get_data(self):
        prices = self.make_request()
        return prices
