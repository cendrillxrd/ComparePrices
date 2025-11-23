import pandas as pd

from DTO.columns_dto import WBColumnsDTO, asdict
from DTO.info_wb_dto import InfoWBDTO
from services.redaction import RedactionService


class InfoWBRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.columns = WBColumnsDTO()

    def redact_info(self, info: InfoWBDTO) -> pd.DataFrame:
        wb_prices_merged = self.red.merge_wb_prices(info.wb_cards_prices, info.wb_prices)
        wb_collections_merged = self.red.merge_collections(info.med_collection_1, info.med_collection_2)
        purchase_merged = self.red.merge_with_purchase(wb_collections_merged, info.purchase)
        operations = [
            (self.red.merge_with_med_prices, info.med_prices),
            (self.red.merge_with_med_collections_ozon, purchase_merged),
        ]

        if info.wb_promotions is not None:
            operations.append((self.red.merge_with_promotions, info.wb_promotions))
        if info.wb_fbs_stocks is not None:
            operations.append((self.red.merge_stocks, info.wb_fbs_stocks))
        if info.wb_fbw_stocks is not None:
            operations.append((self.red.merge_stocks, info.wb_fbw_stocks))

        result = wb_prices_merged

        for method, arg in operations:
            result = method(result, arg)

        return result[[col for col in asdict(self.columns).values() if col in result.wb_columns]]
