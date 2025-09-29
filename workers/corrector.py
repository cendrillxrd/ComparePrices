import pandas as pd

from strategies.correct_strategies import CorrectorStrategy


class Corrector:
    def __init__(self):
        self.__strategy = None

    def set_strategy(self, strategy: CorrectorStrategy):
        self.__strategy = strategy

    def correct(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.correcting(df, **kwargs)
