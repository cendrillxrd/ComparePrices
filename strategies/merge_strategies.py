from abc import ABC, abstractmethod

import pandas as pd

from DTO.columns_dto import WBColumnsDTO
from DTO.ozon_columns_dto import OZONColumnsDTO
wb_columns_dto = WBColumnsDTO()
ozon_columns_dto = OZONColumnsDTO()

class MergeStrategies(ABC):
    @abstractmethod
    def merge(self, *args) -> pd.DataFrame:
        pass

class MergeCollectionsStrategy(MergeStrategies):
    def __init__(self, merge_on: str = wb_columns_dto.seller_article):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.concat([df1, df2], ignore_index=True)
        return merged_df

class MergePricesStrategy(MergeStrategies):
    def __init__(self, merge_on: str = wb_columns_dto.seller_article):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergePricesOZONStrategy(MergeStrategies):
    def __init__(self, merge_on: str = ozon_columns_dto.ozon_article):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        df1[self.merge_on] = df1[self.merge_on].astype(str)
        df2[self.merge_on] = df2[self.merge_on].astype(str)
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeSellerPricesStrategy(MergeStrategies):
    def __init__(self, merge_on: str = wb_columns_dto.ozon_id):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergePromoStrategy(MergeStrategies):
    def __init__(self, merge_on: str = wb_columns_dto.wb_article):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergePurchaseStrategy(MergeStrategies):
    def __init__(self, merge_on: str = wb_columns_dto.ozon_id):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        df1[self.merge_on] = df1[self.merge_on].astype(str)
        df2[self.merge_on] = df2[self.merge_on].astype(str)
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeStocksStrategy(MergeStrategies):
    def __init__(self, merge_on: str = wb_columns_dto.seller_article):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeWbPricesStrategy(MergeStrategies):
    def __init__(self, merge_on: str = wb_columns_dto.wb_article):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeWbCollectionsStrategy(MergeStrategies):
    def __init__(self, merge_on: str = wb_columns_dto.seller_article):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        df1[self.merge_on] = df1[self.merge_on].astype(str)
        df2[self.merge_on] = df2[self.merge_on].astype(str)
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeCardsCollections(MergeStrategies):
    def __init__(self, merge_on: str = ozon_columns_dto.ozon_id):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        df1[self.merge_on] = df1[self.merge_on].astype(str)
        df2[self.merge_on] = df2[self.merge_on].astype(str)
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeArticlePrices(MergeStrategies):
    def __init__(self, merge_on: str = 'url'):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeOZONWithCollectionsStrategy(MergeStrategies):
    def __init__(self, merge_on: str = ozon_columns_dto.ozon_id):

        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        df1[self.merge_on] = df1[self.merge_on].astype(str)
        df2[self.merge_on] = df2[self.merge_on].astype(str)
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeFromClientStrategy(MergeStrategies):
    def __init__(self, merge_on: str = ozon_columns_dto.ozon_article):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        df1[ozon_columns_dto.ozon_article] = df1[ozon_columns_dto.ozon_article].astype(str)
        df2[ozon_columns_dto.ozon_article] = df2[ozon_columns_dto.ozon_article].astype(str)
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

class MergeToClientStrategy(MergeStrategies):
    def __init__(self, merge_on: str = ozon_columns_dto.ozon_article):
        self.merge_on = merge_on

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        df1[ozon_columns_dto.ozon_article] = df1[ozon_columns_dto.ozon_article].astype(str)
        df2[ozon_columns_dto.ozon_article] = df2[ozon_columns_dto.ozon_article].astype(str)
        merged_df = pd.merge(df1, df2, on=self.merge_on, how='left')
        return merged_df

