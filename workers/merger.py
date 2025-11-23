import pandas as pd

from strategies.merge_strategies import MergeStrategies


class Merger:
    def __init__(self):
        self.__strategy = None

    def set_strategy(self, strategy: MergeStrategies):
        self.__strategy = strategy

    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
        merged_df = self.__strategy.merge(df1, df2, **kwargs)
        return merged_df
