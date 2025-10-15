import logging

import pandas as pd

from logging_config import setup_logging
from strategies.convert_strategies import (ConvCollectionsMEDStrategy,
                                           ConvPricesMEDStrategy, ConvPurchaseMEDStrategy)
from strategies.request_strategies import (ReqCollectionsFirstMEDStrategy,
                                           ReqCollectionsSecondMEDStrategy,
                                           ReqPricesMEDStrategy, ReqPurchaseMEDStrategy)
from workers.client import MedClient
from workers.converter import Converter

setup_logging()
logger = logging.getLogger(__name__)


def with_strategies(med_strategy_cls, converter_strategy_cls):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            self.med.set_strategy(med_strategy_cls())
            self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class MEDService:
    def __init__(self):
        self.med = MedClient()
        self.converter = Converter()

    @with_strategies(ReqPricesMEDStrategy, ConvPricesMEDStrategy)
    def get_med_prices(self) -> pd.DataFrame:
        logger.info('Получение данных о ценах на Меде')
        med_prices_csv = self.med.get_data()
        med_prices_df = self.converter.convert(med_prices_csv)
        return med_prices_df

    @with_strategies(ReqCollectionsFirstMEDStrategy, ConvCollectionsMEDStrategy)
    def get_med_collections_first(self) -> pd.DataFrame:
        logger.info('Получение данных о коллекциях первой ссылки')
        med_collections_csv = self.med.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies(ReqCollectionsSecondMEDStrategy, ConvCollectionsMEDStrategy)
    def get_med_collections_second(self) -> pd.DataFrame:
        logger.info('Получение данных о коллекциях второй ссылки')
        med_collections_csv = self.med.get_data()
        med_collections_df = self.converter.convert(med_collections_csv)
        return med_collections_df

    @with_strategies(ReqPurchaseMEDStrategy, ConvPurchaseMEDStrategy)
    def get_med_purchase(self) -> pd.DataFrame:
        logger.info('Получение данных о коллекциях второй ссылки')
        med_purchase_csv = self.med.get_data()
        med_purchase_df = self.converter.convert(med_purchase_csv)
        return med_purchase_df

