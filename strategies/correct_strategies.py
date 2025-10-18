from abc import ABC, abstractmethod

import pandas as pd

from DTO.columns_dto import ColumnsDTO
from DTO.dop_columns import DopColumnsDTO


class CorrectorStrategy(ABC):
    def __init__(self):
        self.columns = ColumnsDTO()
        self.dop_columns = DopColumnsDTO()
    @abstractmethod
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

class CorrExcelStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> list[dict]:
        columns_to_int = [self.columns.wb_article, self.columns.med_price_without_discount,self.dop_columns.new_discount]
        for column in columns_to_int:
            df[column] = df[column].astype(int)

        df.rename({self.columns.wb_article: 'nmID',
                   self.columns.med_price_without_discount: 'price',
                   self.dop_columns.new_discount: 'discount'}, inplace=True, axis=1)
        final_df = df[['nmID', 'price', 'discount']].to_dict('records')
        return final_df

class CorrPricesStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)

        columns_name = [self.columns.med_price_without_discount,
                        self.columns.med_price_with_discount]

        for col in columns_name:
            df[col] = pd.to_numeric(df[col], downcast="integer")

        df[self.columns.med_discount] = 100 - round((df[self.columns.med_price_with_discount] / df[self.columns.med_price_without_discount]) * 100)

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
        df[self.columns.wb_discount] = 100 - round((df[self.columns.wb_price_with_wb_discount] / df[self.columns.wb_price_with_seller_discount]) * 100)
        return df

class CorrPurchaseStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        # df.drop(columns=[self.columns.ozon_id], axis=1, inplace=True)
        # df.loc[df[self.columns.purchase].isna() | (df[self.columns.purchase] == 0), self.columns.purchase] = -1
        pass
        return df


class CorrCollectionsStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)  # заменяем пустоту на нули
        df.loc[df[self.columns.purchase] == 0, self.columns.purchase] = -1  # устанавливаем закупку -1, если она 0
        df[self.columns.equilibrium_discount] = round(100 * (1 - df[self.columns.med_price_with_discount] /
                                                             (df[self.columns.wb_price_without_discount] *
                                                              (1 - df[self.columns.wb_discount] / 100))))  # высчитываем скидку для равновесия
        df[self.columns.equilibrium_discount] = df[self.columns.equilibrium_discount].clip(lower=0)  # если скидка отрицательная, то меняем на 0 (невозможно уравнять)
        df.loc[df[self.columns.equilibrium_discount] == 100, self.columns.equilibrium_discount] = -1  # если скидка 100 %, то меняем на -1 (товара нет на меде)
        df[self.columns.price_difference] = df[self.columns.med_price_with_discount] - df[self.columns.wb_price_with_wb_discount]   # подсчет разности цен
        return df
