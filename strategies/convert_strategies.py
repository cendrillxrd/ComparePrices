from io import StringIO
from abc import ABC, abstractmethod

import pandas as pd
from config import BASE_COLUMNS_NAME


class ConverterStrategy(ABC):
    @abstractmethod
    def converting(self, data) -> pd.DataFrame:
        pass


class ConvPricesWBStrategy(ConverterStrategy):
    def converting(self, data: dict) -> pd.DataFrame:
        """Преобразует данные о ценах на WB в DataFrame"""
        df = pd.DataFrame(data)

        assigned_df = df.assign(price=df['sizes'].apply(lambda x: int(x[0]['price'])),
                                price_seller=df['sizes'].apply(lambda x: int(x[0]['discountedPrice'])))
        columns_name = ['nmID', 'vendorCode', 'price', 'price_seller']
        corrected_df = assigned_df[columns_name].copy()

        columns_rename = {k: BASE_COLUMNS_NAME.get(k) for k in columns_name}

        corrected_df.rename(columns_rename,
                            inplace=True,
                            axis=1)

        return corrected_df


class ConvPricesMEDStrategy(ConverterStrategy):
    def converting(self, data) -> pd.DataFrame:
        """Преобразует данные о ценах на меде в DataFrame"""
        # med_prices_df = pd.read_csv(StringIO(data.text), encoding='utf-8')
        med_prices_df = pd.read_csv('file_prices.csv', encoding='utf-8')
        med_prices_df.drop_duplicates(inplace=True)
        med_unique_prices_df = med_prices_df.sort_values('Цена со скидкой').drop_duplicates(['Артикул',
                                                                                             'Цена без скидки'])
        med_unique_prices_df.reset_index(inplace=True, drop=True)

        columns_name = ['Артикул', 'Цена без скидки', 'Цена со скидкой']

        columns_rename = {k: BASE_COLUMNS_NAME.get(k) for k in columns_name}

        med_unique_prices_df.rename(columns_rename,
                                    inplace=True,
                                    axis=1)
        return med_unique_prices_df


class ConvStocksStrategy(ConverterStrategy):
    def converting(self, data: dict) -> pd.DataFrame:
        """Преобразует данные об остатках в DataFrame"""
        df = pd.DataFrame(data)

        assigned_df = df.assign(stockCount=df['metrics'].apply(lambda x: x['stockCount']),
                                toClientCount=df['metrics'].apply(lambda x: x['toClientCount']),
                                fromClientCount=df['metrics'].apply(lambda x: x['fromClientCount'])
                                )

        columns_name = ['nmID', 'stockCount', 'subjectName', 'name', 'brandName', 'toClientCount', 'fromClientCount']
        corrected_df = assigned_df[columns_name].copy()
        corrected_no_zeros_df = corrected_df.loc[~(corrected_df == 0).all(axis=1)]

        columns_rename = {k: BASE_COLUMNS_NAME.get(k) for k in columns_name}

        corrected_no_zeros_df.rename(columns_rename,
                                     inplace=True,
                                     axis=1)
        return corrected_no_zeros_df
