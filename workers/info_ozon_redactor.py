import pandas as pd

# from config import STOCKS_FILE_NAME, FUNNEL_FILE_NAME
# from dto.info_update_dto import InfoUpdateDTO
from DTO.ozon_columns_dto import OZONColumnsDTO, asdict
from DTO.info_ozon_dto import InfoOZONDTO
from config import MAIN_OZON_BRANDS
# from dto.stocks_by_size_columns_dto import StocksColumnsDTO
from services.redaction import RedactionService


class InfoOZONRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.main_columns = OZONColumnsDTO()

    def redact_info(self, info: InfoOZONDTO) -> dict:
        ozon_collections_merged = self.red.merge_collections(info.collections_first, info.collections_second)
        ozon_collections_merged_2 = self.red.merge_collections(ozon_collections_merged, info.collections_third)
        ozon_collections_merged_3 = self.red.merge_collections(ozon_collections_merged_2, info.collections_fourth)

        operations = [
            (self.red.merge_with_to_client, info.to_client),
            # (self.red.merge_with_from_client, info.from_client),
            (self.red.merge_with_med_collections_ozon, ozon_collections_merged_3),
            (self.red.merge_with_med_prices_ozon, info.med_prices),
            (self.red.merge_with_seller_prices, info.seller_prices),
            (self.red.merge_with_prices, info.prices),
            (self.red.merge_with_ozon_purchase, info.purchase),
        ]

        result = info.cards_info

        for method, arg in operations:
            result = method(result, arg)
        main_table = result[[col for col in asdict(self.main_columns).values() if col in result.columns]].copy()

        #Убрал бренды с селекта
        main_table = main_table[main_table[self.main_columns.brand].isin(MAIN_OZON_BRANDS)]

        return main_table