import time
import logging
from abc import ABC, abstractmethod

from config import LIMIT_PRICE, TIME_SLEEP_PRICE, LIMIT_STOCKS, TIME_SLEEP_STOCKS
from logging_config import setup_logging
from DTO.info_dto import StocksDTO, PriceDTO, asdict

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
    price_dto = PriceDTO()

    def get_info(self, client, **kwargs) -> list[dict]:
        logger.info(f'Получение данных о ценах на товары')
        result = []
        count = 0
        params = asdict(self.price_dto)
        response = client.make_request(method='GET',
                                       api_type=self.api_type,
                                       url_key=self.url_key,
                                       params=params,
                                       endpoint=self.endpoint)
        list_goods = response['data']['listGoods']
        antifreeze = 1000

        while list_goods and antifreeze:
            antifreeze -= 1
            self.price_dto.offset += LIMIT_PRICE
            result.extend(list_goods)
            time.sleep(TIME_SLEEP_PRICE)
            count += len(list_goods)
            logger.debug(f'Карточек загружено {count}')

            params = asdict(self.price_dto)
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
    stock_dto = StocksDTO()

    def get_info(self, client, nm_ids=None) -> list[dict]:
        result = []
        count = 0
        payload = asdict(self.stock_dto)
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
            self.stock_dto.offset += LIMIT_STOCKS
            result.extend(items)
            time.sleep(TIME_SLEEP_STOCKS)
            count += len(items)
            logger.debug(f'Карточек загружено {count}')

            payload = asdict(self.stock_dto)
            if nm_ids is not None:
                payload['nmIDs'] = nm_ids

            response = client.make_request(method='POST',
                                           api_type=self.api_type,
                                           url_key=self.url_key,
                                           payload=payload,
                                           endpoint=self.endpoint)
            items = response['data']['items']
        return result
