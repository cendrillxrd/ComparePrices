import pandas as pd

from services.price_corr import PriceCorrService
from services.redaction import RedactionService
from services.wb import WBService
from strategies.convert_strategies import ConvExcelStrategy
from workers.converter import Converter


class PriceUpdater:
    def __init__(self):
        self.price_corr = PriceCorrService()
        self.wb = WBService()
        self.red = RedactionService()
        self.converter = Converter()

    def update_prices(self, excel_df: pd.DataFrame):
        self.converter.set_strategy(ConvExcelStrategy())
        actual_excel_df = self.converter.convert(excel_df)

        rules_applies_excel_df = self.price_corr.set_rule_on_med(actual_excel_df)
        rules_applies_excel_df = self.price_corr.set_rule_not_on_med(rules_applies_excel_df)
        final_df = self.red.correct_excel_df(rules_applies_excel_df)
        self.wb.create_task_for_change_prices(final_df)