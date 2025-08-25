import pandas as pd
import logging

from workers.merger import Merger
from workers.corrector import Corrector
from logging_config import setup_logging
from strategies.correct_strategies import CorrPricesStrategy, CorrStocksStrategy
from strategies.merge_strategies import MergePricesStrategy, MergeStocksStrategy

setup_logging()
logger = logging.getLogger(__name__)


def with_strategies(merge_strategy_cls, correcter_strategy_cls):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            self.merger.set_strategy(merge_strategy_cls())
            self.corrector.set_strategy(correcter_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class RedactionService:
    def __init__(self):
        self.merger = Merger()
        self.corrector = Corrector()

    @with_strategies(MergePricesStrategy, CorrPricesStrategy)
    def merge_prices(self, wb_df: pd.DataFrame, med_df: pd.DataFrame) -> pd.DataFrame:
        prices_merged = self.merger.merge(wb_df, med_df)
        prices_corrected = self.corrector.correct(prices_merged)
        return prices_corrected

    @with_strategies(MergeStocksStrategy, CorrStocksStrategy)
    def merge_stocks(self, stocks_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
        stocks_merged = self.merger.merge(stocks_df, prices_df)
        stocks_corrected = self.corrector.correct(stocks_merged)
        return stocks_corrected
