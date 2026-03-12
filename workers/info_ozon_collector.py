import logging

from DTO.info_ozon_dto import InfoOZONDTO
from DTO.ozon_columns_dto import OZONColumnsDTO
from logging_config import setup_logging
from services.med import MEDService
from services.ozon import OzonService
from services.wb import WBService

setup_logging()
logger = logging.getLogger(__name__)

class InfoOZONCollector:
    def __init__(self):
        self.ozon = OzonService()
        self.med = MEDService()
        self.main_columns_dto = OZONColumnsDTO()

    def collect_info(self) -> InfoOZONDTO:
        cards_info = self.ozon.get_cards_info()
        prices = self.ozon.get_prices_info(cards_info)

        seller_prices = self.ozon.get_seller_prices()
        med_prices = self.med.get_med_prices()

        to_client = self.ozon.get_stocks_to_client()

        collections_first = self.med.get_med_collections_first()
        collections_second = self.med.get_med_collections_second()
        collections_third = self.med.get_med_collections_third()
        collections_fourth = self.med.get_med_collections_fourth()

        skus = cards_info[cards_info[self.main_columns_dto.status] == 'Продается'][self.main_columns_dto.ozon_article].to_list()
        from_client_fbo = self.ozon.get_from_client_fbo(sku=skus)

        purchase = self.med.get_med_purchase()

        return InfoOZONDTO(
            cards_info=cards_info,
            collections_first=collections_first,
            collections_second=collections_second,
            collections_third=collections_third,
            collections_fourth=collections_fourth,
            prices=prices,
            to_client=to_client,
            from_client=from_client_fbo,
            purchase=purchase,
            seller_prices=seller_prices,
            med_prices=med_prices,
        )
