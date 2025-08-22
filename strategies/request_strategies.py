import time
import logging
from abc import ABC, abstractmethod

# from client import Client
from config import LIMIT_PRICE, TIME_SLEEP_PRICE, LIMIT_STOCKS, TIME_SLEEP_STOCKS
from logging_config import setup_logging
from utils.date_helpers import get_today_date

setup_logging()
logger = logging.getLogger(__name__)


class RequestStrategy(ABC):
    @abstractmethod
    def get_info(self, client: 'WildberriesAPIClient', **kwargs) -> list[dict]:
        pass


class ReqPricesStrategy(RequestStrategy):
    endpoint = "/api/v2/list/goods/filter"
    api_type = "Price_discount_API_KEY"
    url_key = "discounts-prices"

    def get_info(self, client, **kwargs) -> list[dict]:
        logger.info(f'Получение данных о ценах на товары')
        result = []
        offset = 0
        count = 0
        params = {
            'limit': LIMIT_PRICE,
            'offset': offset
        }
        response = client.make_request(method='GET',
                                       api_type=self.api_type,
                                       url_key=self.url_key,
                                       params=params,
                                       endpoint=self.endpoint)
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
            response = client.make_request(method='GET',
                                           api_type=self.api_type,
                                           url_key=self.url_key,
                                           params=params,
                                           endpoint=self.endpoint)
            list_goods = response['data']['listGoods']
        return result


class ReqStocksStrategy(RequestStrategy):
    endpoint = "/api/v2/stocks-report/products/products"
    api_type = "Analytics_Statistics_API_KEY"
    url_key = "seller-analytics"
    stock_type = ''
    start_date = get_today_date()
    end_date = get_today_date()

    def get_info(self, client, nm_ids=None) -> list[dict]:
        result = []
        offset = 0
        count = 0
        stock_type = ''
        payload = {
            'currentPeriod': {
                'start': self.start_date,
                'end': self.end_date
            },
            'stockType': self.stock_type,
            'skipDeletedNm': True,
            'orderBy': {
                'field': 'stockCount',
                'mode': 'desc'
            },
            'availabilityFilters': [
                'deficient',
                'balanced',
                'actual',
                'nonActual',
                'nonLiquid',
                'invalidData'
            ],
            'limit': LIMIT_STOCKS,
            'offset': offset
        }
        if nm_ids is not None:
            payload['nmIDs'] = nm_ids

        response = client.make_request(method='POST',
                                       api_type=self.api_type,
                                       url_key=self.url_key,
                                       payload=payload,
                                       endpoint=self.endpoint)
        items = response['data']['items']
        antifreeze = 1000

        while items and antifreeze:
            antifreeze -= 1
            offset += LIMIT_STOCKS
            result.extend(items)
            time.sleep(TIME_SLEEP_STOCKS)
            count += len(items)
            logger.debug(f'Карточек загружено {count}')

            payload = {
                'currentPeriod': {
                    'start': self.start_date,
                    'end': self.end_date
                },
                'stockType': self.stock_type,
                'skipDeletedNm': True,
                'orderBy': {
                    'field': 'stockCount',
                    'mode': 'desc'
                },
                'availabilityFilters': [
                    'deficient',
                    'balanced',
                    'actual',
                    'nonActual',
                    'nonLiquid',
                    'invalidData'
                ],
                'limit': LIMIT_STOCKS,
                'offset': offset
            }
            if nm_ids is not None:
                payload['nmIDs'] = nm_ids

            response = client.make_request(method='POST',
                                           api_type=self.api_type,
                                           url_key=self.url_key,
                                           payload=payload,
                                           endpoint=self.endpoint)
            items = response['data']['items']
        return result
