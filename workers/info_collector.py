import logging

from services.wb import WBService
from services.med import MEDService
from logging_config import setup_logging
from DTO.info_dto import InfoDTO
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
        med_collection_1 = self.med.get_med_collections_first()
        med_collection_2 = self.med.get_med_collections_second()
        wb_promotions = self.wb.get_wb_promotions_plan_discounts()
        return InfoDTO(
            wb_cards_prices=wb_cards_prices,
            wb_prices=wb_prices,
            med_prices=med_prices,
            med_collection_1=med_collection_1,
            med_collection_2=med_collection_2,
            wb_promotions=wb_promotions
        )
