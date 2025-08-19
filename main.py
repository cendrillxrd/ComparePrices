import logging

from wildberries_api import WildberriesAPIClient
from logging_config import setup_logging
from converters.prices_converter import convert_prices_result_to_df

setup_logging()
logger = logging.getLogger(__name__)


class WildberriesDataCollector:
    def __init__(self):
        self.api = WildberriesAPIClient()

    def get_prices(self):
        """Получение цен на товары."""
        logger.info(f'Получение данных о ценах')
        prices_response = self.api.get_prices()
        prices_df = convert_prices_result_to_df(prices_response)
        return prices_df
