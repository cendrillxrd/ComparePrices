from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from DTO.columns_dto import WBColumnsDTO
from DTO.wb_dop_columns import WBDopColumnsDTO
from DTO.ozon_columns_dto import OZONColumnsDTO
from config import MAIN_OZON_BRANDS, OZON_DISCOUNT_SELECT
from utils.prices_helper import transform_dataframe


class CorrectorStrategy(ABC):
    def __init__(self):
        self.wb_columns = WBColumnsDTO()
        self.dop_columns = WBDopColumnsDTO()
        self.ozon_columns = OZONColumnsDTO()

    @abstractmethod
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

class CorrExcelStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> list[dict]:
        df = df[~df[self.dop_columns.new_discount].isna()]
        columns_to_int = [self.wb_columns.wb_article, self.wb_columns.wb_price_without_discount, self.dop_columns.new_discount]
        for column in columns_to_int:
            df[column] = df[column].astype(int)

        df.rename({self.wb_columns.wb_article: 'nmID',
                   self.wb_columns.med_price_without_discount: 'price',
                   self.dop_columns.new_discount: 'discount'}, inplace=True, axis=1)
        final_dict = df[['nmID', 'price', 'discount']].to_dict('records')
        return final_dict

class CorrPricesStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)

        columns_name = [self.wb_columns.med_price_without_discount,
                        self.wb_columns.med_price_with_discount]

        for col in columns_name:
            df[col] = pd.to_numeric(df[col], downcast="integer")

        df[self.wb_columns.med_discount] = 100 - round((df[self.wb_columns.med_price_with_discount] / df[self.wb_columns.med_price_without_discount]) * 100)

        return df

class CorrPricesOZONStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)

        columns_name = [self.ozon_columns.med_price_without_discount,
                        self.ozon_columns.med_price_with_discount]

        for col in columns_name:
            df[col] = pd.to_numeric(df[col], downcast="integer")

        df[self.ozon_columns.med_discount] = 100 - round((df[self.ozon_columns.med_price_with_discount] / df[self.ozon_columns.med_price_without_discount]) * 100)

        return df

class CorrPromoStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)
        return df


class CorrStocksStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)
        return df


class CorrWbPricesStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.wb_columns.wb_discount] = 100 - round((df[self.wb_columns.wb_price_with_wb_discount] / df[self.wb_columns.wb_price_with_seller_discount]) * 100)
        return df

class CorrPurchaseOZONStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.ozon_columns.purchase].fillna(0, inplace=True)
        df[self.ozon_columns.purchase] = pd.to_numeric(df[self.ozon_columns.purchase], downcast="integer")
        df.loc[df[self.ozon_columns.purchase] == 0, self.ozon_columns.purchase] = -1

        df[self.ozon_columns.equilibrium_discount] = round(100 * (1 - df[self.ozon_columns.med_price_with_discount] /
                                                                (df[self.ozon_columns.price_without_discount] *
                                                                 (1 - df[self.ozon_columns.ozon_discount] / 100))))  # высчитываем скидку для равновесия
        # df[self.ozon_columns.equilibrium_discount] = df[self.wb_columns.equilibrium_discount].clip(lower=0)  # если скидка отрицательная, то меняем на 0 (невозможно уравнять)
        df.loc[df[self.ozon_columns.equilibrium_discount] == 100, self.ozon_columns.equilibrium_discount] = -1  # если скидка 100 %, то меняем на -1 (товара нет на меде)
        df[self.ozon_columns.price_difference] = df[self.ozon_columns.med_price_with_discount] - df[self.ozon_columns.price_with_ozon_discount]   # подсчет разности цен

        df[self.ozon_columns.equilibrium_price] = round(df[self.ozon_columns.price_without_discount] * (1 - df[self.ozon_columns.equilibrium_discount] / 100)) # высчитываем цену для равновесия
        # df.loc[(df[self.ozon_columns.equilibrium_price] > df[self.ozon_columns.price_without_discount]), self.ozon_columns.equilibrium_price] = -1 # (товара нет на меде)
        df.loc[df[self.ozon_columns.equilibrium_discount] == -1, self.ozon_columns.equilibrium_price] = -1
        return df


class CorrCollectionsStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)  # заменяем пустоту на нули
        df.loc[df[self.wb_columns.purchase] == 0, self.wb_columns.purchase] = -1  # устанавливаем закупку -1, если она 0
        df[self.wb_columns.equilibrium_discount] = round(100 * (1 - df[self.wb_columns.med_price_with_discount] /
                                                                (df[self.wb_columns.wb_price_without_discount] *
                                                                 (1 - df[self.wb_columns.wb_discount] / 100))))  # высчитываем скидку для равновесия

        df[self.wb_columns.equilibrium_discount_100] = round(100 * (1 - (df[self.wb_columns.med_price_with_discount] + 100) /
                                                                    (df[self.wb_columns.wb_price_without_discount] *
                                                                 (1 - df[
                                                                     self.wb_columns.wb_discount] / 100))))  # высчитываем скидку для равновесия

        df[self.wb_columns.equilibrium_discount] = df[self.wb_columns.equilibrium_discount].clip(lower=0)  # если скидка отрицательная, то меняем на 0 (невозможно уравнять)
        df.loc[df[self.wb_columns.equilibrium_discount] == 100, self.wb_columns.equilibrium_discount] = -1  # если скидка 100 %, то меняем на -1 (товара нет на меде)
        df[self.wb_columns.price_difference] = df[self.wb_columns.med_price_with_discount] - df[self.wb_columns.wb_price_with_wb_discount]   # подсчет разности цен


        #Для +300
        df[self.wb_columns.equilibrium_discount_100] = df[self.wb_columns.equilibrium_discount_100].clip(
            lower=0)  # если скидка отрицательная, то меняем на 0 (невозможно уравнять)
        df.loc[df[
                   self.wb_columns.equilibrium_discount_100] == 100, self.wb_columns.equilibrium_discount_100] = -1  # если скидка 100 %, то меняем на -1 (товара нет на меде)
        return df

class CorrectCardsCollections(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df_without_unnecessary_columns = df[[self.ozon_columns.ozon_id,
                                             self.ozon_columns.ozon_article,
                                             self.ozon_columns.seller_article,
                                             self.ozon_columns.name]].dropna().reset_index(drop=True)
        # grouped_df = df_without_unnecessary_columns.groupby(self.ozon_columns.seller_article).aggregate(
        #     {self.ozon_columns.ozon_article: 'first', self.ozon_columns.name: 'first'}).reset_index()
        # transformed_df = transform_dataframe(grouped_df, kwargs['col_name'])
        transformed_df = transform_dataframe(df_without_unnecessary_columns, kwargs['col_name'])
        return transformed_df

class CorrectArticlePrices(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        corrected_df = df[[self.ozon_columns.ozon_article, self.ozon_columns.price_with_ozon_discount,
                           self.ozon_columns.price_with_ozon_club]]
        corrected_df[self.ozon_columns.price_with_ozon_discount] = pd.to_numeric(
            df[self.ozon_columns.price_with_ozon_discount].str.replace('₽', '', regex=False),
            errors='coerce'
        ).fillna(0).astype(int)

        corrected_df[self.ozon_columns.price_with_ozon_club] = pd.to_numeric(
            df[self.ozon_columns.price_with_ozon_club].str.replace('₽', '', regex=False),
            errors='coerce'
        ).fillna(0).astype(int)
        return corrected_df

class CorrectToClientStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df[self.ozon_columns.in_way_to_client].fillna(0, inplace=True)
        return df

class CorrectFromClientStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df[self.ozon_columns.in_way_from_client].fillna(0, inplace=True)
        return df

class CorrectPricesOZONStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df.loc[~(df[self.ozon_columns.brand].isin(MAIN_OZON_BRANDS)),self.ozon_columns.price_with_ozon_discount] = round(df[self.ozon_columns.price_with_seller_discount] * (1 - OZON_DISCOUNT_SELECT / 100))
        df[self.ozon_columns.ozon_discount] = 100 - round(
            (df[self.ozon_columns.price_with_ozon_discount] / df[self.ozon_columns.price_with_seller_discount]) * 100)
        columns_to_update = [self.ozon_columns.price_with_ozon_club, self.ozon_columns.price_with_ozon_discount, self.ozon_columns.ozon_discount]
        for col in columns_to_update:
            df[col].fillna(0, inplace=True)
            df[col] = pd.to_numeric(df[col], downcast="integer")
        df = df[~(df[self.ozon_columns.price_with_ozon_discount] == 0)]
        return df

class CorrectSellerPricesOZONStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df[self.ozon_columns.seller_discount] = 100 - round((df[self.ozon_columns.price_with_seller_discount] / df[self.ozon_columns.price_without_discount]) * 100)
        df[self.ozon_columns.seller_discount] = pd.to_numeric(df[self.ozon_columns.seller_discount], downcast="integer")
        return df

class CorrectOZONinfo(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:

        df[self.ozon_columns.in_way_to_client] = (
                pd.to_numeric(df[self.ozon_columns.in_way_to_client], errors='coerce').fillna(0) +
                pd.to_numeric(df[self.ozon_columns.fbo_reserv], errors='coerce').fillna(0) +
                pd.to_numeric(df[self.ozon_columns.fbs_reserv], errors='coerce').fillna(0)
        ).astype(int)
        df.drop([self.ozon_columns.fbo_reserv, self.ozon_columns.fbs_reserv], axis=1, inplace=True)

        # Обрабатываем остальные числовые столбцы
        columns_to_update = [self.ozon_columns.fbs_stocks, self.ozon_columns.fbo_stocks,
                             self.ozon_columns.price_without_discount, self.ozon_columns.in_way_from_client]

        df = df[df[self.ozon_columns.status]=='Продается'].reset_index(drop=True)
        df.drop([self.ozon_columns.status], axis=1, inplace=True)

        for col in columns_to_update:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], downcast="integer")
        return df
