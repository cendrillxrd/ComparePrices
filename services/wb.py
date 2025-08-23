import pandas as pd
import logging

from workers.client import WildberriesAPIClient
from strategies.request_strategies import ReqStocksStrategy, ReqPricesStrategy
from strategies.convert_strategies import PricesWBStrategy, StocksStrategy
from logging_config import setup_logging
from workers.converter import Converter

setup_logging()
logger = logging.getLogger(__name__)


def with_strategies(wb_strategy_cls, converter_strategy_cls):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            self.wb.set_strategy(wb_strategy_cls())
            self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class WBService:
    def __init__(self):
        self.wb = WildberriesAPIClient()
        self.converter = Converter()

    @with_strategies(ReqPricesStrategy, PricesWBStrategy)
    def get_wb_prices(self) -> pd.DataFrame:
        logger.info('Получение данных о ценах')
        prices_json = self.wb.get_data()
        prices_df = self.converter.convert(prices_json)
        return prices_df

    @with_strategies(ReqStocksStrategy, StocksStrategy)
    def get_wb_stocks(self) -> pd.DataFrame:
        logger.info('Получение данных об остатках')
        stocks_json = self.wb.get_data()
        stocks_df = self.converter.convert(stocks_json)
        return stocks_df
