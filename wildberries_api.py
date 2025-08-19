import logging
import time
from typing import Dict, Literal, Optional

import pandas as pd
import requests

from config import API_KEYS, BASE_URLS
from logging_config import setup_logging

LIMIT_CARDS = 100  # <= 100
LIMIT_PRICE = 1000  # <= 1000
TIME_SLEEP_CARDS = 0.7  # >= 0.6
TIME_SLEEP_PRICE = 1  # >= 0.6

setup_logging()
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").propagate = False


class WildberriesAPIClient:
    def __init__(self):
        self.base_url = BASE_URLS
        self.api_key = API_KEYS
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _make_request(
            self,
            api_type: Literal['Analytics_Statistics_API_KEY', 'Content_Marketplace_API_KEY',
                              'Price_discount_API_KEY'],
            url_key: Literal['suppliers', 'content', 'seller-analytics', 'statistics',
                             'marketplace', 'dp-calendar', 'discounts-prices'],
            method: Literal['GET', 'POST'],
            endpoint: str,
            params: Optional[Dict] = None,
            payload: Optional[Dict] = None,
            retries: int = 5):
        """
            Делает запрос по API.

            Args:
                api_type (str): Тип апи ключа.
                url_key (str): Тип URL адреса запроса.
                method (str): Метод API запроса.
                endpoint (str): Эндпоинт запроса
                params (Optional[Dict]): Параметры запроса, по умолчанию None
                payload (Optional[Dict]): Данные, передаваемые в POST запрос, по умолчанию None
                retries (int): Количество попыток для повторения запроса, по умолчанию 5

            Returns:
                Возвращает либо словарь с данными или ZIP файл
            """
        url = f'{self.base_url[url_key]}{endpoint}'
        logger.info(f'Выполнение запроса по адресу {url}')

        for attempt in range(retries):
            self.session.headers.update({'Authorization': self.api_key[api_type]})
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=payload,
                timeout=10
            )
            try:
                response.raise_for_status()
                logger.info(f'Запрос выполнен успешно')
                if self.session.headers['Content-Type'] == 'application/zip':
                    return response
                return response.json()

            except requests.exceptions.HTTPError as err:
                logger.info(f'Запрос не удался, ошибка {err.response.status_code}'
                            f'Попытка {attempt + 1}/{retries}')
                if err.response.status_code in (429, 500, 502, 503, 504):
                    wait_time = min(2 ** attempt, 10)
                    logger.debug(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                raise err

            except requests.exceptions.RequestException as err:
                logger.info(f'Запрос не удался, ошибка {err.response.status_code}')
                if attempt == retries - 1:
                    raise err
                time.sleep(1)

        return None

    def get_prices(self) -> list[dict]:
        """
           Запрос данных о ценах на товары.

           Запрашивает данные о товарах по их артикулам: цены, валюту, общие скидки и скидки для WB Клуба.
           Например:
            {
            --------"nmID": 98486,
            --------"vendorCode": "07326060",
            --------"sizes": [
            --------------------{
            ------------------------"sizeID": 3123515574,
            ------------------------"price": 500,
            ------------------------"discountedPrice": 350,
            ------------------------"clubDiscountedPrice": 332.5,
            ------------------------"techSizeName": "42"
            --------------------}
            --------],
            --------"currencyIsoCode4217": "RUB",
            --------"discount": 30,
            --------"clubDiscount": 5,
            --------"editableSizePrice": true
            ----}
           Returns:
               list[dict]: Список словарей в которых хранится информация о товарах.
           """
        logger.info(f'Получение данных о ценах на товары')
        endpoint = '/api/v2/list/goods/filter'
        offset = 0
        result = []
        count = 0

        params = {
            'limit': LIMIT_PRICE,
            'offset': offset
        }
        response = self._make_request(method='GET',
                                      api_type='Price_discount_API_KEY',
                                      url_key='discounts-prices',
                                      params=params,
                                      endpoint=endpoint)
        list_goods = response['data']['listGoods']
        antifreeze = 1000

        while list_goods and antifreeze:
            antifreeze -= 1
            offset += LIMIT_PRICE
            result.extend(list_goods)
            time.sleep(TIME_SLEEP_PRICE)
            count += len(list_goods)
            logger.debug(f'Карточек загружено {count}')

            params = {
                'limit': LIMIT_PRICE,
                'offset': offset
            }
            response = self._make_request(method='GET',
                                          api_type='Price_discount_API_KEY',
                                          url_key='discounts-prices',
                                          params=params,
                                          endpoint=endpoint)
            list_goods = response['data']['listGoods']
        return result
