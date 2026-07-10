from abc import ABC, abstractmethod
from io import BytesIO, StringIO

import numpy as np
import pandas as pd

from DTO.wb_dop_columns import WBDopColumnsDTO
from config import BASE_COLUMNS_NAME_WB, CLUB_PROCENT, ORDER_STATUSES, BASE_COLUMNS_NAME_OZON
from DTO.columns_dto import WBColumnsDTO, asdict
from DTO.ozon_columns_dto import OZONColumnsDTO


class ConverterStrategy(ABC):
    def __init__(self):
        self.wb_columns = WBColumnsDTO()
        self.ozon_columns = OZONColumnsDTO()
        self.dop_columns = WBDopColumnsDTO()


    @abstractmethod
    def converting(self, data, **kwargs) -> pd.DataFrame:
        pass

class ConvPromoGoodsWBStrategy(ConverterStrategy):
    def converting(self, data: dict, **kwargs) -> pd.DataFrame:
        """Преобразует данные о ценах на WB в DataFrame"""
        df = pd.DataFrame(data)

        columns_name = [column for column in df.columns if column in BASE_COLUMNS_NAME_WB]
        columns_rename = {k: BASE_COLUMNS_NAME_WB.get(k) for k in columns_name}
        df.rename(columns_rename,
                                          inplace=True,
                                          axis=1)

        min_discount_promotions_df = df.sort_values(self.wb_columns.wb_article).drop_duplicates(
            [self.wb_columns.wb_article,
             self.wb_columns.plan_discount])
        min_discount_promotions_df.reset_index(inplace=True, drop=True)

        min_discount_promotions_df = min_discount_promotions_df[[self.wb_columns.wb_article, self.wb_columns.plan_discount]].copy()

        return min_discount_promotions_df

class ConvPromoIDWBStrategy(ConverterStrategy):
    def converting(self, data: dict, **kwargs) -> list:
        promotions = pd.DataFrame(data)
        filtered_promotions = promotions[promotions['type'] == 'regular']
        ids = filtered_promotions['id'].tolist()
        int_ids = list(map(int, ids))
        return int_ids

class ConvPricesWBStrategy(ConverterStrategy):
    def converting(self, data: dict, **kwargs) -> pd.DataFrame:
        """Преобразует данные о ценах на WB в DataFrame"""
        df = pd.DataFrame(data)

        assigned_df = df.assign(price=df['sizes'].apply(lambda x: int(x[0]['price'])),
                                price_seller=df['sizes'].apply(lambda x: int(x[0]['discountedPrice'])))

        columns_name = [column for column in assigned_df.columns if column in BASE_COLUMNS_NAME_WB]
        corrected_df = assigned_df[columns_name].copy()

        columns_rename = {k: BASE_COLUMNS_NAME_WB.get(k) for k in columns_name}

        corrected_df.rename(columns_rename,
                            inplace=True,
                            axis=1)

        return corrected_df

class ConvPricesMEDStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        """Преобразует данные о ценах на меде в DataFrame"""
        med_prices_df = pd.read_csv(StringIO(data.text), encoding='utf-8')
        med_prices_df.columns = [col.encode('latin1').decode('utf-8') for col in med_prices_df.columns]
        med_prices_df.drop_duplicates(inplace=True)

        columns_name = [column for column in med_prices_df.columns if column in BASE_COLUMNS_NAME_WB]

        columns_rename = {k: BASE_COLUMNS_NAME_WB.get(k) for k in columns_name}

        med_prices_df.rename(columns_rename,
                            inplace=True,
                            axis=1)

        med_unique_prices_df = med_prices_df.sort_values(self.wb_columns.med_price_with_discount).drop_duplicates([self.wb_columns.seller_article,
                                                                                                                   self.wb_columns.med_price_without_discount])
        med_unique_prices_df.reset_index(inplace=True, drop=True)

        return med_unique_prices_df

class ConvCollectionsMEDStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        """Преобразует данные о ценах на меде в DataFrame"""
        med_collections_df = pd.read_excel(BytesIO(data.content))

        columns_name = [column for column in med_collections_df.columns if column in BASE_COLUMNS_NAME_WB]

        columns_rename = {k: BASE_COLUMNS_NAME_WB.get(k) for k in columns_name}
        med_collections_df.rename(columns_rename,
                                  inplace=True,
                                  axis=1)

        if kwargs['type'] == 'wb':
            med_collections_df.drop_duplicates(subset=self.wb_columns.seller_article, inplace=True)
            med_collections_df.reset_index(inplace=True, drop=True)
        med_without_unnecessary_columns = med_collections_df[[self.wb_columns.ozon_id, self.wb_columns.seller_article, self.wb_columns.collection]]
        return med_without_unnecessary_columns

class ConvPurchaseMEDStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        """Преобразует данные о закупке на меде в DataFrame"""
        med_purchase_df = pd.read_csv(StringIO(data.text))

        columns_name = [column for column in med_purchase_df.columns if column in BASE_COLUMNS_NAME_WB]

        columns_rename = {k: BASE_COLUMNS_NAME_WB.get(k) for k in columns_name}
        med_purchase_df.rename(columns_rename,
                                  inplace=True,
                                  axis=1)

        return med_purchase_df

class ConvExcelStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        df = data[~(data[self.wb_columns.seller_discount] == data[self.wb_columns.equilibrium_discount])]
        # df.loc[df[self.dop_columns.max_discount_including_commission] == 100, self.dop_columns.max_discount_including_commission] = 60
        return df

class ConvStatusNewPricesWBStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        df = pd.DataFrame(data)
        columns_name = [column for column in df.columns if column in BASE_COLUMNS_NAME_WB]

        columns_rename = {k: BASE_COLUMNS_NAME_WB.get(k) for k in columns_name}
        df.rename(columns_rename,
                   inplace=True,
                   axis=1)
        needs_columns = [self.wb_columns.wb_article, self.wb_columns.seller_article,
                         self.wb_columns.wb_price_without_discount, self.wb_columns.seller_discount, 'Статус загрузки',
                         'Текст ошибки']
        return df[[col for col in needs_columns if col in df.columns]]

class ConvStocksWBStrategy(ConverterStrategy):
    def converting(self, data: dict, **kwargs) -> pd.DataFrame:
        """Преобразует данные об остатках в DataFrame"""
        stock_type = kwargs['stock_type']
        df = pd.DataFrame(data)

        assigned_df = df.assign(stockCount=df['metrics'].apply(lambda x: x['stockCount']),
                                toClientCount=df['metrics'].apply(lambda x: x['toClientCount']),
                                fromClientCount=df['metrics'].apply(lambda x: x['fromClientCount'])
                                )

        if stock_type == 'wb':
            assigned_df.rename({'stockCount': 'stock_fbw'}, inplace=True, axis=1)
        if stock_type == 'mp':
            assigned_df.rename({'stockCount': 'stock_fbs'}, inplace=True, axis=1)

        columns_name = [column for column in assigned_df.columns if column in BASE_COLUMNS_NAME_WB]

        columns_rename = {k: BASE_COLUMNS_NAME_WB.get(k) for k in columns_name}

        assigned_df.rename(columns_rename,
                                     inplace=True,
                                     axis=1)
        if stock_type == 'wb':
            df_without_unnecessary_columns = assigned_df[[self.wb_columns.seller_article, self.wb_columns.stock_fbw,
                                                          self.wb_columns.stock_in_way_to_client, self.wb_columns.stock_in_way_from_client]].copy()
        else:
            df_without_unnecessary_columns = assigned_df[[self.wb_columns.seller_article, self.wb_columns.stock_fbs]].copy()

        return df_without_unnecessary_columns

class ConvWbCardsPricesStrategy(ConverterStrategy):
    def converting(self, data: dict, **kwargs) -> pd.DataFrame:
        """Преобразует данные о ценах на WB в DataFrame"""
        prices = []
        prices_df = pd.DataFrame()
        for card in data:
            articul = card['id']
            # brand = card['brand']
            category = card['entity']
            name = card['name']
            price = card["sizes"][0]["price"]["product"] // 100
            price_with_wb_club = round(price * (1 - CLUB_PROCENT / 100))
            prices.append({self.wb_columns.wb_article: articul,
                           self.wb_columns.wb_price_with_wb_discount: price,
                           self.wb_columns.wb_price_with_wb_club: price_with_wb_club,
                           # self.wb_columns.brand: brand,
                           self.wb_columns.category: category,
                           self.wb_columns.name: name, })
            prices_df = pd.DataFrame(prices)
        return prices_df

class ConvCardsInfoOZONStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        df = pd.read_csv(BytesIO(data.content), encoding='utf-8', sep=';')

        columns_name = [column for column in df.columns if column in BASE_COLUMNS_NAME_OZON]

        columns_rename = {k: BASE_COLUMNS_NAME_OZON.get(k) for k in columns_name}
        df.rename(columns_rename,
                                  inplace=True,
                                  axis=1)
        # df[self.ozon_columns.ozon_id] = df[self.ozon_columns.ozon_id].str.lstrip("'")
        return df

class ConvOrdersInfoOZONStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        df = pd.read_csv(BytesIO(data.content), encoding='utf-8', sep=';')

        columns_name = [column for column in df.columns if column in BASE_COLUMNS_NAME_OZON]

        columns_rename = {k: BASE_COLUMNS_NAME_OZON.get(k) for k in columns_name}
        df.rename(columns_rename,
                                  inplace=True,
                                  axis=1)
        df_active_orders = df[df['Статус'].isin(ORDER_STATUSES)]
        grouped_df = df_active_orders.groupby(self.ozon_columns.ozon_article).aggregate(
            {self.ozon_columns.in_way_to_client: lambda x: np.sum(x)}).reset_index()

        return grouped_df

class ConvStocksFboOZONStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        df = pd.DataFrame(data)

        columns_name = [column for column in df.columns if column in BASE_COLUMNS_NAME_OZON]

        columns_rename = {k: BASE_COLUMNS_NAME_OZON.get(k) for k in columns_name}
        df.rename(columns_rename,
                                  inplace=True,
                                  axis=1)

        from_client = df[[self.ozon_columns.ozon_article, self.ozon_columns.in_way_from_client]].copy()
        grouped_df = from_client.groupby(self.ozon_columns.ozon_article).aggregate(
            {self.ozon_columns.in_way_from_client: lambda x: np.sum(x)}).reset_index()
        return grouped_df

class ConvPricesOZONStrategy(ConverterStrategy):
    def converting(self, data, **kwargs) -> pd.DataFrame:
        df = pd.DataFrame(data)

        assigned_df = df.assign(price=df['price'].apply(lambda x: x['price']))

        columns_name = [column for column in assigned_df.columns if column in BASE_COLUMNS_NAME_OZON]
        corrected_df = assigned_df[columns_name].copy()

        columns_rename = {k: BASE_COLUMNS_NAME_OZON.get(k) for k in columns_name}

        corrected_df.rename(columns_rename,
                            inplace=True,
                            axis=1)
        corrected_df = corrected_df[[self.ozon_columns.ozon_id, self.ozon_columns.price_with_seller_discount]]
        return corrected_df
