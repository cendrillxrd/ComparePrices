import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Literal, Optional

import requests

from config import API_KEYS, BASE_URLS, DELAY_INTERVAL, HEADERS, PARAMS
from logging_config import setup_logging
from strategies.request_strategies import RequestStrategy
from utils.request_helper import get_random_user_agent

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
                     url_key: Literal['seller-analytics', 'discounts-prices', 'dp-calendar'],
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

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)


class WildberriesHttpClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS['wb_http']
        self.headers = HEADERS
        self.params = PARAMS
        self.__strategy = None

    def make_request(self, page: str):
        self.headers['User-Agent'] = get_random_user_agent()
        self.params['page'] = page
        self.headers['Referer'] = ''.join([self.headers['Referer'], page])
        response = requests.get(self.base_url, headers=self.headers, params=self.params)
        content = None
        if response.status_code == 429:
            print('Rate limit reached. Sleeping...')
            time.sleep(DELAY_INTERVAL)
            return self.make_request(page)
        elif response.status_code != 200:
            print(f'Error: {response.status_code}. Try a different proxy or user-agent')
            response.raise_for_status()
        else:
            content = response.json()
        return content

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self)

class MedClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS
        self.__strategy = None

    def make_request(self, url_key: Literal['med_prices', 'med_collections_1', 'med_collections_2']):
        url = f'{self.base_url[url_key]}'
        logger.info(f'Выполнение запроса по адресу {url}')
        response = requests.get(url)
        return response

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self)