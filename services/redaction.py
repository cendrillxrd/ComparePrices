import logging
from typing import Literal

import pandas as pd

from logging_config import setup_logging
from strategies.correct_strategies import (CorrCollectionsStrategy,
                                           CorrPricesStrategy,
                                           CorrPromoStrategy,
                                           CorrStocksStrategy,
                                           CorrWbPricesStrategy)
from strategies.merge_strategies import (MergeCollectionsStrategy,
                                         MergePricesStrategy,
                                         MergePromoStrategy,
                                         MergeStocksStrategy,
                                         MergeWbCollectionsStrategy,
                                         MergeWbPricesStrategy, MergePurchaseStrategy)
from workers.corrector import Corrector
from workers.merger import Merger

setup_logging()
logger = logging.getLogger(__name__)


def with_strategies(merge_strategy_cls: 'MergeStrategies',
                    correcter_strategy_cls: 'CorrectorStrategy' = None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
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

    @with_strategies(MergePromoStrategy, CorrPromoStrategy)
    def merge_with_promotions(self, wb_df: pd.DataFrame, promo_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по акциям WB')
        prices_merged = self.merger.merge(wb_df, promo_df)
        prices_corrected = self.corrector.correct(prices_merged)
        return prices_corrected

    @with_strategies(MergePricesStrategy, CorrPricesStrategy)
    def merge_with_med_prices(self, wb_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по ценам WB и MED')
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

    @with_strategies(MergeCollectionsStrategy)
    def merge_collections(self, wb_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по коллекциям')
        collections_merged = self.merger.merge(wb_df, med_df)
        return collections_merged

    @with_strategies(MergePurchaseStrategy)
    def merge_with_purchase(self, collections_df: pd.DataFrame, purchase_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка закупки')
        purchase_merged = self.merger.merge(collections_df, purchase_df)
        # purchase_corrected = self.corrector.correct(purchase_merged)
        return purchase_merged


