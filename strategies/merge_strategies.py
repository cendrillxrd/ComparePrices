import pandas as pd
from abc import ABC, abstractmethod


class MergeStrategies(ABC):
    @abstractmethod
    def merge(self, *args) -> pd.DataFrame:
        pass

class MergeCollectionsStrategy(MergeStrategies):
    def __init__(self, merge_on: str = 'Артикул продавца'):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.concat([df1, df2], ignore_index=True)
        return merged_df

class MergePricesStrategy(MergeStrategies):
    def __init__(self, merge_on: str = 'Артикул продавца'):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df


class MergeStocksStrategy(MergeStrategies):
    def __init__(self, merge_on: str = 'Артикул WB'):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeWbPricesStrategy(MergeStrategies):
    def __init__(self, merge_on: str = 'Артикул WB'):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeWbCollectionsStrategy(MergeStrategies):
    def __init__(self, merge_on: str = 'Артикул продавца'):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df
