import logging
from typing import Literal

import pandas as pd

from logging_config import setup_logging
from strategies.correct_strategies import (CorrCollectionsStrategy,
                                           CorrPricesStrategy,
                                           CorrPromoStrategy,
                                           CorrStocksStrategy,
                                           CorrWbPricesStrategy, CorrPurchaseOZONStrategy, CorrExcelStrategy,
                                           CorrectCardsCollections, CorrectArticlePrices, CorrectOZONinfo,
                                           CorrectToClientStrategy, CorrectFromClientStrategy,
                                           CorrectPricesOZONStrategy, CorrectSellerPricesOZONStrategy,
                                           CorrPricesOZONStrategy)
from strategies.merge_strategies import (MergeCollectionsStrategy,
                                         MergePricesStrategy,
                                         MergePromoStrategy,
                                         MergeStocksStrategy,
                                         MergeWbCollectionsStrategy,
                                         MergeWbPricesStrategy, MergePurchaseStrategy, MergeCardsCollections,
                                         MergeArticlePrices, MergeOZONWithCollectionsStrategy, MergeToClientStrategy,
                                         MergeFromClientStrategy, MergeSellerPricesStrategy, MergePricesOZONStrategy)
from workers.corrector import Corrector
from workers.merger import Merger

setup_logging()
logger = logging.getLogger(__name__)


def with_strategies(merge_strategy_cls: 'MergeStrategies' = None,
                    correcter_strategy_cls: 'CorrectorStrategy' = None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if merge_strategy_cls is not None:
                self.merger.set_strategy(merge_strategy_cls())
            if correcter_strategy_cls is not None:
                self.corrector.set_strategy(correcter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class RedactionService:
    def __init__(self):
        self.merger = Merger()
        self.corrector = Corrector()

    @with_strategies(correcter_strategy_cls=CorrExcelStrategy)
    def correct_excel_df(self, excel_df: pd.DataFrame) -> list[dict]:
        excel_df_corrected = self.corrector.correct(excel_df)
        return excel_df_corrected

    @with_strategies(MergePromoStrategy, CorrPromoStrategy)
    def merge_with_promotions(self, wb_df: pd.DataFrame, promo_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по акциям WB')
        prices_merged = self.merger.merge(wb_df, promo_df)
        prices_corrected = self.corrector.correct(prices_merged)
        return prices_corrected

    @with_strategies(MergePricesStrategy, CorrPricesStrategy)
    def merge_with_med_prices(self, wb_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по ценам MED')
        prices_merged = self.merger.merge(wb_df, med_df)
        prices_corrected = self.corrector.correct(prices_merged)
        return prices_corrected

    @with_strategies(MergePricesStrategy, CorrPricesOZONStrategy)
    def merge_with_med_prices_ozon(self, wb_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по ценам MED')
        prices_merged = self.merger.merge(wb_df, med_df)
        prices_corrected = self.corrector.correct(prices_merged)
        return prices_corrected

    @with_strategies(MergeStocksStrategy, CorrStocksStrategy)
    def merge_stocks(self, stocks_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по остаткам')
        stocks_merged = self.merger.merge(stocks_df, prices_df)
        stocks_corrected = self.corrector.correct(stocks_merged)
        return stocks_corrected

    @with_strategies(MergeWbPricesStrategy, CorrWbPricesStrategy)
    def merge_wb_prices(self, wb_cards_prices: pd.DataFrame, wb_prices: pd.DataFrame):
        logger.info('Обработка данных по ценам WB')
        wb_prices_merged = self.merger.merge(wb_cards_prices, wb_prices)
        wb_prices_corrected = self.corrector.correct(wb_prices_merged)
        return wb_prices_corrected

    @with_strategies(MergeWbCollectionsStrategy, CorrCollectionsStrategy)
    def merge_with_med_collections(self, wb_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по ценам WB и MED')
        collections_merged = self.merger.merge(wb_df, med_df)
        collections_corrected = self.corrector.correct(collections_merged)
        return collections_corrected

    @with_strategies(merge_strategy_cls=MergeCardsCollections, correcter_strategy_cls=CorrectCardsCollections)
    def merge_cards_with_collections(self, cards_df: pd.DataFrame, collections_df: pd.DataFrame, col_name) -> pd.DataFrame:
        merged_df = self.merger.merge(cards_df, collections_df)
        corrected_df = self.corrector.correct(merged_df, col_name=col_name)
        return corrected_df

    @with_strategies(merge_strategy_cls=MergeArticlePrices, correcter_strategy_cls=CorrectArticlePrices)
    def merge_articles_with_prices(self, articles_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
        merged_df = self.merger.merge(articles_df, prices_df)
        corrected_df = self.corrector.correct(merged_df)
        return corrected_df

    @with_strategies(merge_strategy_cls=MergeOZONWithCollectionsStrategy, correcter_strategy_cls=CorrectOZONinfo)
    def merge_with_med_collections_ozon(self, main_df: pd.DataFrame, collections_df: pd.DataFrame) -> pd.DataFrame:
        med_collections_merged = self.merger.merge(main_df, collections_df)
        med_collections_corrected = self.corrector.correct(med_collections_merged)
        return med_collections_corrected

    @with_strategies(merge_strategy_cls=MergeToClientStrategy, correcter_strategy_cls=CorrectToClientStrategy)
    def merge_with_to_client(self, main_df: pd.DataFrame, to_client_df: pd.DataFrame) -> pd.DataFrame:
        to_client_merged = self.merger.merge(main_df, to_client_df)
        corrected_df = self.corrector.correct(to_client_merged)
        return corrected_df

    @with_strategies(merge_strategy_cls=MergeFromClientStrategy, correcter_strategy_cls=CorrectFromClientStrategy)
    def merge_with_from_client(self, main_df: pd.DataFrame, from_client_df: pd.DataFrame) -> pd.DataFrame:
        from_client_merged = self.merger.merge(main_df, from_client_df)
        corrected_df = self.corrector.correct(from_client_merged)
        return corrected_df

    @with_strategies(merge_strategy_cls=MergePricesOZONStrategy, correcter_strategy_cls=CorrectPricesOZONStrategy)
    def merge_with_prices(self, main_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
        merged_df = self.merger.merge(main_df, prices_df)
        corrected_df = self.corrector.correct(merged_df)
        return corrected_df

    @with_strategies(merge_strategy_cls=MergeSellerPricesStrategy, correcter_strategy_cls=CorrectSellerPricesOZONStrategy)
    def merge_with_seller_prices(self, main_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
        merged_df = self.merger.merge(main_df, prices_df)
        corrected_df = self.corrector.correct(merged_df)
        return corrected_df

    @with_strategies(MergeCollectionsStrategy)
    def merge_collections(self, wb_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по коллекциям')
        collections_merged = self.merger.merge(wb_df, med_df)
        return collections_merged

    @with_strategies(merge_strategy_cls=MergePurchaseStrategy)
    def merge_with_purchase(self, collections_df: pd.DataFrame, purchase_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка закупки')
        purchase_merged = self.merger.merge(collections_df, purchase_df)
        return purchase_merged

    @with_strategies(merge_strategy_cls=MergePurchaseStrategy, correcter_strategy_cls=CorrPurchaseOZONStrategy)
    def merge_with_ozon_purchase(self, collections_df: pd.DataFrame, purchase_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка закупки')
        purchase_merged = self.merger.merge(collections_df, purchase_df)
        corrected_df = self.corrector.correct(purchase_merged)
        return corrected_df


