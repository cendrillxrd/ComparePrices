import logging

from services.wb import WBService
from services.med import MEDService
from logging_config import setup_logging
from DTO.dto import InfoDTO
setup_logging()
logger = logging.getLogger(__name__)


class InfoCollector:
    def __init__(self):
        self.wb = WBService()
        self.med = MEDService()

    def collect_info(self) -> InfoDTO:
        wb_prices = self.wb.get_wb_prices()
        wb_cards_prices = self.wb.get_wb_cards_prices()
        med_prices = self.med.get_med_prices()
        return InfoDTO(
            wb_cards_prices=wb_cards_prices,
            wb_prices=wb_prices,
            med_prices=med_prices
        )
