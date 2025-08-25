from abc import ABC, abstractmethod

import pandas as pd


class CorrectorStrategy(ABC):
    @abstractmethod
    def correcting(self, data) -> pd.DataFrame:
        pass


class CorrPricesStrategy(CorrectorStrategy):
    def correcting(self, df):
        df.fillna(0, inplace=True)
        df['(MED) Цена без скидки'] = pd.to_numeric(df['(MED) Цена без скидки'],
                                                    downcast="integer")
        df['(MED) Цена со скидкой продавца'] = pd.to_numeric(df['(MED) Цена со скидкой продавца'],
                                                             downcast="integer")

        return df


class CorrStocksStrategy(CorrectorStrategy):
    def correcting(self, df):
        df.drop(['Остаток', 'В пути к клиенту', 'В пути от клиента'], axis=1, inplace=True)
        return df
