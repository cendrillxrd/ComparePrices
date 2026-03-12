import asyncio
import logging
import time
import uuid
from typing import Literal, Optional, List, Union

import pandas as pd

from DTO.ozon_columns_dto import OZONColumnsDTO
from config import TIME_SLEEP_CARDS_LINK, YANDEX_FILE_NAME, MAIN_DIR_PRICES, MAIN_OZON_BRANDS
from services.redaction import RedactionService
from services.yandex_disk import YandexDiskManager

from strategies.convert_strategies import ConvCardsInfoOZONStrategy, ConvOrdersInfoOZONStrategy, \
    ConvStocksFboOZONStrategy, ConvPricesOZONStrategy
from strategies.request_strategies import ReqOrdersInfoOZONReportStrategy, ReqCardsInfoOZONReportStrategy, \
    ReqGetLinkOZONStrategy, ReqGetLinkDataOZONStrategy, ReqStocksFboOZONStrategy, ReqPricesOZONStrategy
from utils.prices_helper import transform_dataframe
from utils.save_helper import save_results
from workers.client import OzonAPIClient, HttpClient
from workers.converter import Converter
from workers.ozon_parser import OzonPriceParser
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)



def with_strategies(type: Literal['api', 'http', 'ozon_http']=None, ozon_strategy_cls=None, converter_strategy_cls=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if ozon_strategy_cls is not None:
                if type == 'api':
                    self.ozon_api_client.set_strategy(ozon_strategy_cls())
                elif type == 'http':
                    self.http_client.set_strategy(ozon_strategy_cls())
                else:
                    self.ozon_http_client.set_strategy(ozon_strategy_cls())
            if converter_strategy_cls is not None:
                self.converter.set_strategy(converter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class OzonService:
    def __init__(self):
        self.ozon_api_client = OzonAPIClient()
        self.converter = Converter()
        self.http_client = HttpClient()
        self.red = RedactionService()
        self.ozon_columns = OZONColumnsDTO()
        self.yadisk = YandexDiskManager()

    @with_strategies(converter_strategy_cls=ConvCardsInfoOZONStrategy)
    def get_cards_info(self) -> pd.DataFrame:
        code = self.create_info_report_cards()
        time.sleep(TIME_SLEEP_CARDS_LINK)
        file_link = self.get_info_link(code)
        if file_link:
            cards = self.get_cards_info_report(file_link)
            cards_df = self.converter.convert(cards)
        else:
            cards_df = None
        return cards_df

    @with_strategies(converter_strategy_cls=ConvOrdersInfoOZONStrategy)
    def get_stocks_to_client(self) -> Union[pd.DataFrame, None]:
        orders_fbs_code = self.create_info_report_orders(schema='fbs')
        orders_fbo_code = self.create_info_report_orders(schema='fbo')
        result = []
        for code in (orders_fbs_code, orders_fbo_code):
            time.sleep(TIME_SLEEP_CARDS_LINK)
            file_link = self.get_info_link(code)
            if file_link:
                orders = self.get_cards_info_report(file_link)
                orders_df = self.converter.convert(orders)
                result.append(orders_df)
            else:
                return None
        combined = pd.concat(result)
        result_df = combined.groupby(self.ozon_columns.ozon_article, as_index=False).sum()
        result_df.drop_duplicates(inplace=True)
        return result_df


    @with_strategies('api', ReqOrdersInfoOZONReportStrategy)
    def create_info_report_orders(self, schema: Literal['fbs', 'fbo']) -> str:
        code = self.ozon_api_client.get_data(schema=schema)
        return code

    @with_strategies('api', ReqCardsInfoOZONReportStrategy)
    def create_info_report_cards(self) -> str:
        code = self.ozon_api_client.get_data()
        return code

    @with_strategies('api', ReqGetLinkOZONStrategy)
    def get_info_link(self, code: str) -> str:
        file_link = self.ozon_api_client.get_data(code=code)
        return file_link

    @with_strategies('http', ReqGetLinkDataOZONStrategy)
    def get_cards_info_report(self, link: str) -> list[dict]:
        cards_info = self.http_client.get_data(link=link)
        return cards_info

    def get_prices_info(self, cards_df: pd.DataFrame) -> pd.DataFrame:
        if self.yadisk.is_file_older_than_12_hours():
            cards_df_for_sale = cards_df[(cards_df[self.ozon_columns.status] == 'Продается') & (cards_df[self.ozon_columns.brand].isin(MAIN_OZON_BRANDS))].copy()

            # collections_merged = self.red.merge_collections(collections_1_df, collections_2_df)

            # collections_merged_for_sale = collections_merged[[self.ozon_columns.ozon_id, self.ozon_columns.seller_article]].copy()

            col_name = 'url'
            # articles_for_prices_df = self.red.merge_cards_with_collections(cards_df_for_sale,
            #                                                                collections_merged_for_sale, col_name)
            df_without_unnecessary_columns = cards_df_for_sale[[
                                                 self.ozon_columns.ozon_article,
                                                 self.ozon_columns.name]]
            # grouped_df = df_without_unnecessary_columns.groupby(self.ozon_columns.seller_article).aggregate(
            #     {self.ozon_columns.ozon_article: 'first', self.ozon_columns.name: 'first'}).reset_index()
            # transformed_df = transform_dataframe(grouped_df, kwargs['col_name'])
            transformed_df = transform_dataframe(df_without_unnecessary_columns, col_name)
            articles = transformed_df[col_name].to_list()
            logger.info(f"Загружено {len(articles)} товаров для обработки")


            # Парсинг данных
            prices = asyncio.run(self.main_func(articles))
            prices_info = self.red.merge_articles_with_prices(df_without_unnecessary_columns, prices)
            prices_info.to_csv(MAIN_DIR_PRICES, index=False, encoding='utf-8')
            self.yadisk.save_file_to_folder()
        else:
            self.yadisk.get_file_from_folder()
            prices_info = pd.read_csv(MAIN_DIR_PRICES, encoding='utf-8')

        return prices_info


    @staticmethod
    async def main_func(articles):
        logger.info(f'ПАРСИНГ ДАННЫХ')
        ozon_parser = OzonPriceParser()

        # получение куки
        logger.info(f'Получение куки')
        user_agent, cookies_dict = ozon_parser.get_cookies()

        results = await ozon_parser.process_batch(
            articles,
            user_agent,
            cookies_dict,
            batch_size=100,  # Размер батча
            delay_between_batches=60  # Задержка между батчами
        )
        prices = save_results(results, col_name='url')
        return prices

    @with_strategies('api' , ReqStocksFboOZONStrategy, ConvStocksFboOZONStrategy)
    def get_from_client_fbo(self, sku: list[str]) -> pd.DataFrame:
        stocks = self.ozon_api_client.get_data(sku=sku)
        stocks_df = self.converter.convert(stocks)
        return stocks_df

    @with_strategies('api' , ReqPricesOZONStrategy, ConvPricesOZONStrategy)
    def get_seller_prices(self) -> pd.DataFrame:
        prices = self.ozon_api_client.get_data()
        prices_df = self.converter.convert(prices)
        return prices_df

