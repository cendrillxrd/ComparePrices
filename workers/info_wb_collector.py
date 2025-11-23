import logging

from DTO.info_wb_dto import InfoWBDTO
from logging_config import setup_logging
from services.med import MEDService
from services.wb import WBService

setup_logging()
logger = logging.getLogger(__name__)


class InfoWBCollector:
    def __init__(self):
        self.wb = WBService()
        self.med = MEDService()

    def collect_info(self) -> InfoWBDTO:
        wb_cards_prices = self.wb.get_wb_cards_prices()
        wb_prices = self.wb.get_wb_prices()
        med_prices = self.med.get_med_prices()
        med_collection_1 = self.med.get_med_collections_first(type='wb')
        med_collection_2 = self.med.get_med_collections_second(type='wb')
        wb_promotions = self.wb.get_wb_promotions_plan_discounts()
        wb_fbs_stocks = self.wb.get_wb_stocks('mp')
        wb_fbw_stocks = self.wb.get_wb_stocks('wb')
        purchase = self.med.get_med_purchase()

        return InfoWBDTO(
            wb_cards_prices=wb_cards_prices,
            wb_prices=wb_prices,
            med_prices=med_prices,
            med_collection_1=med_collection_1,
            med_collection_2=med_collection_2,
            wb_promotions=wb_promotions,
            wb_fbs_stocks=wb_fbs_stocks,
            wb_fbw_stocks=wb_fbw_stocks,
            purchase=purchase
        )
