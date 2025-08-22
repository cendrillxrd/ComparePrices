from io import StringIO
from abc import ABC, abstractmethod

import pandas as pd


class ConverterStrategy(ABC):
    @abstractmethod
    def converting(self, data) -> pd.DataFrame:
        pass


class PricesWBStrategy(ConverterStrategy):
    def converting(self, data):
        """Преобразует данные о ценах на WB в DataFrame для воронки продаж."""
        df = pd.DataFrame(data)

        assigned_df = df.assign(price=df['sizes'].apply(lambda x: int(x[0]['price'])),
                                price_seller=df['sizes'].apply(lambda x: int(x[0]['discountedPrice'])))
        corrected_df = assigned_df[['nmID', 'vendorCode', 'price', 'price_seller']].copy()

        corrected_df.rename({'nmID': 'Артикул WB',
                             'vendorCode': 'Артикул продавца',
                             'price': '(WB) Цена без скидки',
                             'price_seller': '(WB) Цена со скидкой продавца'},
                            inplace=True,
                            axis=1)

        return corrected_df


class PricesMEDStrategy(ConverterStrategy):
    def converting(self, data):
        """Преобразует данные о ценах на меде в DataFrame для воронки продаж."""
        # med_prices_df = pd.read_csv(StringIO(get_prices_result.text), encoding='utf-8')
        med_prices_df = pd.read_csv('file_prices.csv', encoding='utf-8')
        med_prices_df.drop_duplicates(inplace=True)
        med_prices_df.reset_index(inplace=True, drop=True)
        med_prices_df.rename({'Артикул': 'Артикул продавца',
                              'Цена без скидки': '(MED) Цена без скидки',
                              'Цена со скидкой': '(MED) Цена со скидкой продавца'},
                             inplace=True,
                             axis=1)

        return med_prices_df


class StocksStrategy(ConverterStrategy):
    def converting(self, data):
        """Преобразует данные об остатках в DataFrame для воронки продаж."""
        df = pd.DataFrame(data)

        assigned_df = df.assign(stockCount=df['metrics'].apply(lambda x: x['stockCount']),
                                toClientCount=df['metrics'].apply(lambda x: x['toClientCount']),
                                fromClientCount=df['metrics'].apply(lambda x: x['fromClientCount'])
                                )
        corrected_df = assigned_df[['nmID', 'stockCount', 'toClientCount', 'fromClientCount']].copy()
        corrected_df.rename({'nmID': 'Артикул WB',
                             'stockCount': 'Остаток',
                             'toClientCount': 'В пути к клиенту',
                             'fromClientCount': 'В пути от клиента'},
                            inplace=True,
                            axis=1)
        return corrected_df
