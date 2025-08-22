import logging

from services.wb import WBService
from services.med import MEDService
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class InfoCollector:
    def __init__(self):
        self.wb = WBService()
        self.med = MEDService()

    def save_info(self):
        pass

    def collect_info(self):
        wb_prices = self.wb.get_wb_prices()
        wb_stocks = self.wb.get_wb_stocks()
        med_prices = self.med.get_med_prices()
        pass
