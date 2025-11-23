import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Union

from DTO.orders_dto import OrdersDTO
from config import (LIMIT_PRICE, LIMIT_STOCKS, TIME_SLEEP_PRICE,
                    TIME_SLEEP_STOCKS, PURCHASE_PASSWORD, PURCHASE_LOGIN, LIMIT_NEW_PRICE_TASK, TIME_SLEEP_REPORT,
                    TIME_SLEEP_STOCKS_FBS)
from DTO.price_dto import PriceDTO
from DTO.promo_dto import PromoDTO
from DTO.promo_goods import PromoGoodsDTO
from DTO.stocks_dto import StocksDTO, asdict
from logging_config import setup_logging
# from utils.request_helper import get_wildberries_cookies

setup_logging()
logger = logging.getLogger(__name__)


class RequestStrategy(ABC):
    @abstractmethod
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        pass

class ReqWBNewPricesStrategy(RequestStrategy):
    endpoint = '/api/v2/upload/task'
    api_type = 'Price_discount_API_KEY'
    url_key = 'discounts-prices'

    def get_info(self, client: 'Client', **kwargs):
        logger.info(f'Редактирование цен')
        payload = {'data': kwargs.get('data')}
        response = client.make_request(method='POST',
                            api_type=self.api_type,
                            url_key=self.url_key,
                            payload=payload,
                            endpoint=self.endpoint)
        return response['data']['id']

class ReqStatusNewPricesStrategy(RequestStrategy):
    endpoint = '/api/v2/history/goods/task'
    api_type = 'Price_discount_API_KEY'
    url_key = 'discounts-prices'

    def get_info(self, client: 'Client', **kwargs):
        logger.info(f'Запрос статусов цен')
        result = []
        count = 0
        params = {'uploadID': kwargs.get('uploadID'),
                  'limit': LIMIT_NEW_PRICE_TASK,
                  'offset': 0,}
        response = client.make_request(method='GET',
                            api_type=self.api_type,
                            url_key=self.url_key,
                            params=params,
                            endpoint=self.endpoint)
        goods = response['data']['historyGoods']
        antifreeze = 10
        while goods and antifreeze:
            antifreeze -= 1
            params['offset'] += LIMIT_NEW_PRICE_TASK
            result.extend(goods)
            time.sleep(TIME_SLEEP_PRICE)
            count += len(goods)
            logger.debug(f'Карточек загружено {count}')

            response = client.make_request(method='GET',
                                           api_type=self.api_type,
                                           url_key=self.url_key,
                                           params=params,
                                           endpoint=self.endpoint)
            goods = response['data']['historyGoods']
        return result

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
    def get_product_list(client: 'Client', page: str) -> list[dict]:
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

    def get_info(self, client, nm_ids=None, **kwargs) -> Union[list[dict], None]:
        stock_type = kwargs['stock_type']

        result = []
        count = 0
        payload = asdict(self.stock_dto)
        payload['stockType'] = stock_type
        if nm_ids is not None:
            payload['nmIDs'] = nm_ids

        response = client.make_request(method='POST',
                                       api_type=self.api_type,
                                       url_key=self.url_key,
                                       payload=payload,
                                       endpoint=self.endpoint)
        if response is None:
            return response
        items = response['data']['items']
        antifreeze = 1000

        while items and antifreeze:
            antifreeze -= 1
            payload['offset'] += LIMIT_STOCKS
            result.extend(items)
            time.sleep(TIME_SLEEP_STOCKS)
            count += len(items)
            logger.debug(f'Карточек загружено {count}')

            response = client.make_request(method='POST',
                                           api_type=self.api_type,
                                           url_key=self.url_key,
                                           payload=payload,
                                           endpoint=self.endpoint)
            if response == None:
                return response
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

class ReqPurchaseMEDStrategy(RequestStrategy):
    url_key = "med_purchase"
    login = PURCHASE_LOGIN
    password = PURCHASE_PASSWORD
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        response = client.make_request(url_key=self.url_key, login=self.login, password=self.password)
        return response

class ReqOrdersInfoOZONReportStrategy(RequestStrategy):
    endpoint = '/v1/report/postings/create'
    url_key = 'ozon'
    orders_dto = OrdersDTO()
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        schema = kwargs['schema']
        payload = asdict(self.orders_dto)
        payload['filter']['delivery_schema'] = [schema]
        logger.info('Запрос заказов')
        response = client.make_request(method='POST',
                                       url_key=self.url_key,
                                       endpoint=self.endpoint,
                                       payload=payload)
        code = response['result']['code']
        return code

class ReqCardsInfoOZONReportStrategy(RequestStrategy):
    endpoint = '/v1/report/products/create'
    url_key = 'ozon'

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info('Запрос карточек')
        response = client.make_request(method='POST',
                                       url_key=self.url_key,
                                       endpoint=self.endpoint)
        code = response['result']['code']
        return code

class ReqGetLinkOZONStrategy(RequestStrategy):
    endpoint = '/v1/report/info'
    url_key = 'ozon'

    def get_info(self, client: 'Client', **kwargs) -> Union[list[dict], bool]:
        logger.info('Получение ссылки')
        payload = {'code': kwargs['code']}
        response = client.make_request(method='POST',
                                       url_key=self.url_key,
                                       payload=payload,
                                       endpoint=self.endpoint)
        status = response['result']['status']
        if status == 'success':
            file_link = response['result']['file']
            return file_link
        elif status in ('waiting', 'processing'):
            time.sleep(TIME_SLEEP_REPORT)
            return self.get_info(client, code=kwargs['code'])
        return False

class ReqGetLinkDataOZONStrategy(RequestStrategy):
    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info('Получение данных из ссылки')
        link = kwargs['link']
        response = client.make_request(url=link)
        return response

class ReqStocksFboOZONStrategy(RequestStrategy):
    endpoint = '/v1/analytics/stocks'
    url_key = 'ozon'

    def get_info(self, client: 'Client', **kwargs) -> list[dict]:
        logger.info('Запрос остатков FBS')
        result = []
        loaded_cards = 0
        sku = kwargs['sku']
        for i in range(0, len(sku), 100):
            time.sleep(TIME_SLEEP_STOCKS_FBS)
            payload = {'skus': sku[i:i+100]}
            response = client.make_request(method='POST',
                                           url_key=self.url_key,
                                           payload=payload,
                                           endpoint=self.endpoint)
            items = response['items']
            loaded_cards += len(items)
            logger.debug(f'Загружено карт: {loaded_cards}')
            result.extend(items)
        return result