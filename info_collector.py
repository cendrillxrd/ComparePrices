import logging
from io import StringIO

import pandas as pd

from med_client import MedClient
from wildberries_api import WildberriesAPIClient
from logging_config import setup_logging
from converters.prices_converter import convert_wb_prices_result_to_df, convert_med_prices_result_to_df
from merge.wb_med_merger import wb_and_med_merge

setup_logging()
logger = logging.getLogger(__name__)


class InfoCollector:
    def __init__(self):
        self.api = WildberriesAPIClient()
        self.med = MedClient()

    def save_info(self):
        ...

    def get_wb_prices(self) -> pd.DataFrame:
        logger.info(f'Получение данных о ценах')
        prices_response = self.api.get_prices()
        prices_df = convert_wb_prices_result_to_df(prices_response)
        prices_df.to_csv('temp1.csv', index=False, encoding='cp1251')
        return prices_df

    def get_med_prices(self) -> pd.DataFrame:
        # med_prices_csv = self.med.get_prices()
        # med_prices_df = convert_med_prices_result_to_df(med_prices_csv)
        med_prices_df = convert_med_prices_result_to_df(1)
        return med_prices_df

    def get_info(self):
        wb_df = self.get_wb_prices()
        med_df = self.get_med_prices()
        wb_med_df = wb_and_med_merge(wb_df, med_df)
        return wb_med_df
