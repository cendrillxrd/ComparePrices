import pandas as pd

from services.redaction import RedactionService
from DTO.dto import InfoDTO


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()

    def redact_info(self, info: InfoDTO) -> pd.DataFrame:
        wb_prices_merged = self.red.merge_wb_prices(info.wb_cards_prices, info.wb_prices)
        wb_med_prices_stocks = self.red.merge_with_med_prices(wb_prices_merged, info.med_prices)
        return wb_med_prices_stocks
