from abc import ABC, abstractmethod

import pandas as pd
from DTO.columns_dto import ColumnsDTO


class CorrectorStrategy(ABC):
    def __init__(self):
        self.columns = ColumnsDTO()
    @abstractmethod
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


class CorrPricesStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)

        columns_name = [self.columns.med_price_without_discount,
                        self.columns.med_price_without_discount]
        for col in columns_name:
            df[col] = pd.to_numeric(df[col], downcast="integer")


        return df

class CorrPromoStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)
        return df


class CorrStocksStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.drop([self.columns.stock_count, self.columns.to_client_count, self.columns.from_client_count], axis=1, inplace=True)
        return df


class CorrWbPricesStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.columns.wb_discount] = 100 - round((df[self.columns.wb_price_with_wb_discount] / df[self.columns.wb_price_with_seller_discount]) * 100)

        return df[[self.columns.wb_article,
                   self.columns.seller_article,
                   self.columns.category,
                   self.columns.name,
                   self.columns.brand,
                   self.columns.wb_price_without_discount,
                   self.columns.seller_discount,
                   self.columns.wb_price_with_seller_discount,
                   self.columns.wb_discount,
                   self.columns.wb_price_with_wb_discount,
                   self.columns.wb_price_with_wb_club,]]


class CorrCollectionsStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)
        df[self.columns.equilibrium_discount] = round(100 * (1 - df[self.columns.med_price_with_discount] / (df[self.columns.wb_price_without_discount] * (1 - df[self.columns.wb_discount] / 100))))
        df[self.columns.equilibrium_discount] = df[self.columns.equilibrium_discount].clip(lower=0)
        df[self.columns.price_difference] = df[self.columns.med_price_with_discount] - df[self.columns.wb_price_with_wb_discount]
        return df[[self.columns.wb_article,
                   self.columns.seller_article,
                   self.columns.category,
                   self.columns.name,
                   self.columns.brand,
                   self.columns.collection,
                   self.columns.wb_price_without_discount,
                   self.columns.seller_discount,
                   self.columns.wb_price_with_seller_discount,
                   self.columns.wb_discount,
                   self.columns.wb_price_with_wb_discount,
                   self.columns.wb_price_with_wb_club,
                   self.columns.med_price_without_discount,
                   self.columns.med_price_with_discount,
                   self.columns.price_difference,
                   self.columns.equilibrium_discount,]]
