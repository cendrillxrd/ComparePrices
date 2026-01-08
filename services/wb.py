import logging
import time
from typing import Literal, Union

import pandas as pd

from config import TASKS_STATUS
from logging_config import setup_logging
from strategies.convert_strategies import (ConvPricesWBStrategy,
                                           ConvPromoGoodsWBStrategy,
                                           ConvPromoIDWBStrategy,
                                           ConvStocksWBStrategy,
                                           ConvWbCardsPricesStrategy, ConvExcelStrategy, ConvStatusNewPricesWBStrategy)
from strategies.request_strategies import (ReqStocksWBStrategy,
                                           ReqWBAPIPricesStrategy,
                                           ReqWBAPIPromotionsGoodsStrategy,
                                           ReqWBAPIPromotionsStrategy,
                                           ReqWbCardsPricesStrategy, ReqWBNewPricesStrategy, ReqStatusNewPricesWBStrategy)
from workers.client import WildberriesAPIClient, WildberriesHttpClient
from workers.converter import Converter

setup_logging()
logger = logging.getLogger(__name__)


def with_strategies(wb_strategy_cls = None, converter_strategy_cls = None, type: Literal['api', 'http', ''] = None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if wb_strategy_cls is not None:
                if type == 'api':
                    self.wb_api_client.set_strategy(wb_strategy_cls())
                else:
                    self.wb_http_client.set_strategy(wb_strategy_cls())
            if converter_strategy_cls is not None:
                self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class WBService:
    def __init__(self):
        self.wb_api_client = WildberriesAPIClient()
        self.wb_http_client = WildberriesHttpClient()
        self.converter = Converter()

    def get_wb_promotions_plan_discounts(self) -> Union[pd.DataFrame, None]:
        promo_ids = self.get_wb_promo_ids()
        if promo_ids:
            promo_goods = self.get_wb_promo_goods(promo_ids)
            return promo_goods
        else:
            return None

    def create_task_for_change_prices(self, data: list[dict]):
        batch_size = 1000
        all_status_dfs = []

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            print(f"Обработка батча {i // batch_size + 1}/{(len(data) - 1) // batch_size + 1}")

            task_id = self.update_prices(batch)
            time.sleep(30)
            status_data_df = self.check_status_tasks(task_id)
            all_status_dfs.append(status_data_df)

        # Объединяем все результаты
        if all_status_dfs:
            final_status_df = pd.concat(all_status_dfs, ignore_index=True)
            final_status_df.to_csv(f'{TASKS_STATUS}.csv', index=False)
        else:
            print("Нет данных для обработки")

    @with_strategies(wb_strategy_cls=ReqWBNewPricesStrategy, type='api')
    def update_prices(self, data: list[dict]) -> int:
        task_id = self.wb_api_client.get_data(data=data)
        return task_id

    @with_strategies(wb_strategy_cls=ReqStatusNewPricesWBStrategy, converter_strategy_cls=ConvStatusNewPricesWBStrategy, type='api')
    def check_status_tasks(self, upload_id: int):
        status_data = self.wb_api_client.get_data(uploadID=upload_id)
        status_data_df = self.converter.convert(status_data)
        return status_data_df

    @with_strategies(ReqWBAPIPromotionsStrategy, ConvPromoIDWBStrategy, 'api')
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

    @with_strategies(ReqStocksWBStrategy, ConvStocksWBStrategy, 'api')
    def get_wb_stocks(self, stock_type=Literal['wb', 'mp']) -> Union[pd.DataFrame, None]:
        logger.info('Получение данных об остатках')
        stocks_json = self.wb_api_client.get_data(stock_type=stock_type)
        if stocks_json is None:
            return stocks_json
        stocks_df = self.converter.convert(stocks_json, stock_type=stock_type)
        return stocks_df

    @with_strategies(ReqWbCardsPricesStrategy, ConvWbCardsPricesStrategy, 'http')
    def get_wb_cards_prices(self) -> pd.DataFrame:
        logger.info('Получение данных о ценах в карточках товаров')
        wb_cards_prices_json = self.wb_http_client.get_data()
        wb_cards_prices_df = self.converter.convert(wb_cards_prices_json)
        return wb_cards_prices_df
