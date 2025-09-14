import pandas as pd
import logging

from workers.merger import Merger
from workers.corrector import Corrector
from logging_config import setup_logging
from strategies.correct_strategies import (CorrPricesStrategy, CorrStocksStrategy, CorrWbPricesStrategy,
                                           CorrCollectionsStrategy, CorrPromoStrategy)
from strategies.merge_strategies import (MergePricesStrategy, MergeStocksStrategy, MergeWbPricesStrategy,
                                         MergeWbCollectionsStrategy, MergeCollectionsStrategy, MergePromoStrategy)

setup_logging()
logger = logging.getLogger(__name__)


def with_strategies(merge_strategy_cls: 'CorrectorStrategy',
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
        prices_merged = self.merger.merge(wb_df, med_df)
        prices_corrected = self.corrector.correct(prices_merged)
        return prices_corrected

    @with_strategies(MergeCollectionsStrategy)
    def merge_collections(self, wb_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        logger.info('Обработка данных по коллекциям')
        prices_merged = self.merger.merge(wb_df, med_df)
        return prices_merged


