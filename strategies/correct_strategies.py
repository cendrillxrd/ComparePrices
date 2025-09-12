from abc import ABC, abstractmethod

import pandas as pd


class CorrectorStrategy(ABC):
    @abstractmethod
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


class CorrPricesStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)

        columns_name = ['(MED) Цена без скидки', '(MED) Цена со скидкой продавца']
        for col in columns_name:
            df[col] = pd.to_numeric(df[col], downcast="integer")


        return df


class CorrStocksStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.drop(['Остаток', 'В пути к клиенту', 'В пути от клиента'], axis=1, inplace=True)
        return df


class CorrWbPricesStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df['Скидка WB'] = 100 - round((df['(WB) Цена со скидкой WB'] / df['(WB) Цена со скидкой продавца']) * 100)
        return df[['Артикул WB',
                   'Артикул продавца',
                   'Категория',
                   'Наименование',
                   'Бренд',
                   '(WB) Цена без скидки',
                   '(WB) Цена со скидкой продавца',
                   'Скидка WB',
                   '(WB) Цена со скидкой WB',
                   '(WB) Цена со скидкой WB клуба']]


class CorrCollectionsStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)
        return df[['Артикул WB',
                   'Артикул продавца',
                   'Категория',
                   'Наименование',
                   'Бренд',
                   'Коллекция',
                   '(WB) Цена без скидки',
                   '(WB) Цена со скидкой продавца',
                   'Скидка WB',
                   '(WB) Цена со скидкой WB',
                   '(WB) Цена со скидкой WB клуба',
                   '(MED) Цена без скидки',
                   '(MED) Цена со скидкой продавца']]
