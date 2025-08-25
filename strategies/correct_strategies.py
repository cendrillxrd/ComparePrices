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
