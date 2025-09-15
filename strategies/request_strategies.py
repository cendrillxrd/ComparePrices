import logging
import random
import time
from abc import ABC, abstractmethod

from config import (LIMIT_PRICE, LIMIT_STOCKS, TIME_SLEEP_PRICE,
                    TIME_SLEEP_STOCKS)
from DTO.price_dto import PriceDTO
from DTO.promo_dto import PromoDTO
from DTO.promo_goods import PromoGoodsDTO
from DTO.stocks_dto import StocksDTO, asdict
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class RequestStrategy(ABC):
    @abstractmethod
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        pass

class ReqWBAPIPromotionsStrategy(RequestStrategy):
    endpoint = '/api/v1/calendar/promotions'
    api_type = 'Price_discount_API_KEY'
    url_key = 'dp-calendar'
    promo_dto = PromoDTO()

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info(f'Получение данных об акциях')
        params = asdict(self.promo_dto)
        response = client.make_request(method='GET',
                                       api_type=self.api_type,
                                       url_key=self.url_key,
                                       params=params,
                                       endpoint=self.endpoint)
        return response['data']['promotions']

class ReqWBAPIPromotionsGoodsStrategy(RequestStrategy):
    endpoint = "/api/v1/calendar/promotions/nomenclatures"
    api_type = "Price_discount_API_KEY"
    url_key = "dp-calendar"
    promo_goods_dto = PromoGoodsDTO()

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info(f'Получение данных о товарах для акций')
        result = []
        count = 0
        params = asdict(self.promo_goods_dto)
        params['promotionID'] = kwargs['promotion_id']
        response = client.make_request(method='GET',
                                       api_type=self.api_type,
                                       url_key=self.url_key,
                                       params=params,
                                       endpoint=self.endpoint)
        list_goods = response['data']['nomenclatures']
        antifreeze = 1000

        while list_goods and antifreeze:
            antifreeze -= 1
            self.promo_goods_dto.offset += LIMIT_PRICE
            result.extend(list_goods)
            time.sleep(TIME_SLEEP_PRICE)
            count += len(list_goods)
            logger.debug(f'Карточек загружено {count}')

            params = asdict(self.promo_goods_dto)
            params['promotionID'] = kwargs['promotion_id']
            response = client.make_request(method='GET',
                                           api_type=self.api_type,
                                           url_key=self.url_key,
                                           params=params,
                                           endpoint=self.endpoint)
            list_goods = response['data']['nomenclatures']
        return result

class ReqWBAPIPricesStrategy(RequestStrategy):
    endpoint = "/api/v2/list/goods/filter"
    api_type = "Price_discount_API_KEY"
    url_key = "discounts-prices"
    price_dto = PriceDTO()

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
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

class ReqWbCardsPricesStrategy(RequestStrategy):
    @staticmethod
    def get_product_list(client: 'Client', page: str):
        logger.debug(f'Страница {page}')
        content = client.make_request(page)
        product_list = content['products']
        sleep_time = random.uniform(1, 10)
        time.sleep(sleep_time)
        return product_list

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info(f'Получение данных о ценах в карточках WB')
        cards = []
        page = 1
        product_list = self.get_product_list(client, str(page))
        while product_list != []:
            cards.extend(product_list)
            page += 1
            product_list = self.get_product_list(client, str(page))
        return cards

class ReqStocksStrategy(RequestStrategy):
    endpoint = "/api/v2/stocks-report/products/products"
    api_type = "Analytics_Statistics_API_KEY"
    url_key = "seller-analytics"
    stock_dto = StocksDTO()

    def get_info(self, client, nm_ids=None, **kwargs) -> list[dict]:
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

class ReqPricesMEDStrategy(RequestStrategy):
    url_key = "med_prices"
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        response = client.make_request(url_key=self.url_key)
        return response

class ReqCollectionsFirstMEDStrategy(RequestStrategy):
    url_key = "med_collections_1"
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        response = client.make_request(url_key=self.url_key)
        return response

class ReqCollectionsSecondMEDStrategy(RequestStrategy):
    url_key = "med_collections_2"
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        response = client.make_request(url_key=self.url_key)
        return response