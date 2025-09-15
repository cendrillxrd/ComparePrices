import logging
from typing import Literal

import pandas as pd

from logging_config import setup_logging
from strategies.convert_strategies import (ConvPricesWBStrategy,
                                           ConvPromoGoodsWBStrategy,
                                           ConvPromoIDStrategy,
                                           ConvStocksStrategy,
                                           ConvWbCardsPricesStrategy)
from strategies.request_strategies import (ReqStocksStrategy,
                                           ReqWBAPIPricesStrategy,
                                           ReqWBAPIPromotionsGoodsStrategy,
                                           ReqWBAPIPromotionsStrategy,
                                           ReqWbCardsPricesStrategy)
from workers.client import WildberriesAPIClient, WildberriesHttpClient
from workers.converter import Converter

setup_logging()
logger = logging.getLogger(__name__)


def with_strategies(wb_strategy_cls, converter_strategy_cls, type: Literal['api', 'http']):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if type == 'api':
                self.wb_api_client.set_strategy(wb_strategy_cls())
            else:
                self.wb_http_client.set_strategy(wb_strategy_cls())
            self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class WBService:
    def __init__(self):
        self.wb_api_client = WildberriesAPIClient()
        self.wb_http_client = WildberriesHttpClient()
        self.converter = Converter()

    def get_wb_promotions_plan_discounts(self):
        promo_ids = self.get_wb_promo_ids()
        promo_goods = self.get_wb_promo_goods(promo_ids)
        return promo_goods

    @with_strategies(ReqWBAPIPromotionsStrategy, ConvPromoIDStrategy, 'api')
    def get_wb_promo_ids(self) -> list:
        logger.info('Получение данных об акциях')
        promotions = self.wb_api_client.get_data()
        promotions_ids = self.converter.convert(promotions)
        return promotions_ids

    @with_strategies(ReqWBAPIPromotionsGoodsStrategy, ConvPromoGoodsWBStrategy, 'api')
    def get_wb_promo_goods(self, promotion_ids: list) -> pd.DataFrame:
        logger.info('Получение данных о товарах для акции')
        promotions_goods = []
        for promo_id in promotion_ids:
            promotions_goods.extend(self.wb_api_client.get_data(promotion_id=promo_id))
        promotions_goods_df = self.converter.convert(promotions_goods)
        return promotions_goods_df

    @with_strategies(ReqWBAPIPricesStrategy, ConvPricesWBStrategy, 'api')
    def get_wb_prices(self) -> pd.DataFrame:
        logger.info('Получение данных о ценах')
        prices_json = self.wb_api_client.get_data()
        prices_df = self.converter.convert(prices_json)
        return prices_df

    @with_strategies(ReqStocksStrategy, ConvStocksStrategy, 'api')
    def get_wb_stocks(self) -> pd.DataFrame:
        logger.info('Получение данных об остатках')
        stocks_json = self.wb_api_client.get_data()
        stocks_df = self.converter.convert(stocks_json)
        return stocks_df

    @with_strategies(ReqWbCardsPricesStrategy, ConvWbCardsPricesStrategy, 'http')
    def get_wb_cards_prices(self) -> pd.DataFrame:
        logger.info('Получение данных о ценах в карточках товаров')
        wb_cards_prices_json = self.wb_http_client.get_data()
        wb_cards_prices_df = self.converter.convert(wb_cards_prices_json)
        return wb_cards_prices_df
