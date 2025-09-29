import pandas as pd

from DTO.columns_dto import ColumnsDTO, asdict
from DTO.info_dto import InfoDTO
from services.redaction import RedactionService


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()
        self.columns = ColumnsDTO()

    def redact_info(self, info: InfoDTO) -> pd.DataFrame:
        wb_prices_merged = self.red.merge_wb_prices(info.wb_cards_prices, info.wb_prices)
        wb_collections_merged = self.red.merge_collections(info.med_collection_1, info.med_collection_2)

        operations = [
            (self.red.merge_with_med_prices, info.med_prices),
            (self.red.merge_with_med_collections, wb_collections_merged),
            (self.red.merge_stocks, info.wb_fbw_stocks),
            (self.red.merge_stocks, info.wb_fbs_stocks),
        ]

        if info.wb_promotions is not None:
            operations.append((self.red.merge_with_promotions, info.wb_promotions))

        result = wb_prices_merged

        for method, arg in operations:
            result = method(result, arg)

        return result[[col for col in asdict(self.columns).values() if col in result.columns]]
