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
        to_client = self.ozon.get_stocks_to_client()

        collections_first = self.med.get_med_collections_first()
        collections_second = self.med.get_med_collections_second()

        cards_info = self.ozon.get_cards_info()

        skus = cards_info[cards_info[self.main_columns_dto.status] == 'Продается'][self.main_columns_dto.ozon_article].to_list()
        from_client_fbo = self.ozon.get_from_client_fbo(sku=skus)

        prices = self.ozon.get_prices_info(cards_info, collections_first, collections_second)

        purchase = self.med.get_med_purchase()

        return InfoOZONDTO(
            cards_info=cards_info,
            collections_first=collections_first,
            collections_second=collections_second,
            prices=prices,
            to_client=to_client,
            from_client=from_client_fbo,
            purchase=purchase
        )
