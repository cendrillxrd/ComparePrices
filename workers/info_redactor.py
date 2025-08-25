import pandas as pd

from services.redaction import RedactionService
from DTO.info_dto import InfoDTO


class InfoRedactor:
    def __init__(self):
        self.red = RedactionService()

    def redact_info(self, info: InfoDTO) -> pd.DataFrame:
        wb_prices_stocks = self.red.merge_stocks(info.wb_stocks, info.wb_prices)
        wb_med_prices_stocks = self.red.merge_prices(wb_prices_stocks, info.med_prices)
        return wb_med_prices_stocks
