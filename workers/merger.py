import pandas as pd
from abc import ABC, abstractmethod

from utils.merger_rules import apply_rules


class Merger(ABC):
    @abstractmethod
    def merge(self, *args) -> pd.DataFrame:
        pass


class WBMedMerger(Merger):
    def __init__(self, merge_on: str = 'Артикул продавца'):
        self.merge_on = merge_on

    def merge(self, wb_prices_df: pd.DataFrame, med_prices_df: pd.DataFrame, wb_stock_df: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(wb_prices_df, med_prices_df, on=self.merge_on, how='left')
        merged_df = apply_rules(merged_df, wb_stock_df)
        return merged_df
