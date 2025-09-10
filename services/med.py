import pandas as pd
import logging

from workers.client import MedClient
from strategies.convert_strategies import ConvPricesMEDStrategy
from workers.converter import Converter
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def with_strategies(converter_strategy_cls):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class MEDService:
    def __init__(self):
        self.med = MedClient()
        self.converter = Converter()

    @with_strategies(ConvPricesMEDStrategy)
    def get_med_prices(self) -> pd.DataFrame:
        logger.info('Получение данных о ценах на Меде')
        med_prices_csv = self.med.get_data()
        # med_prices_csv = pd.read_csv('file_prices.csv')
        med_prices_df = self.converter.convert(med_prices_csv)
        return med_prices_df
