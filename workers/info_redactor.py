import pandas as pd

from DTO.info_dto import InfoDTO
from services.redaction import RedactionService


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()

    def redact_info(self, info: InfoDTO) -> pd.DataFrame:
        wb_prices_merged = self.red.merge_wb_prices(info.wb_cards_prices, info.wb_prices)
        wb_med_prices = self.red.merge_with_med_prices(wb_prices_merged, info.med_prices)
        wb_collections_merged = self.red.merge_collections(info.med_collection_1, info.med_collection_2)
        wb_med_collections_prices = self.red.merge_with_med_collections(wb_med_prices, wb_collections_merged)
        wb_med_collections_prices_promo = self.red.merge_with_promotions(wb_med_collections_prices, info.wb_promotions)
        return wb_med_collections_prices_promo
