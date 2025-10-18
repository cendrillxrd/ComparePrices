import pandas as pd

from strategies.rules_strategies import RulesStrategy


class RulesApplier:
    def __init__(self):
        self.__strategy = None

    def set_strategy(self, strategy: RulesStrategy):
        self.__strategy = strategy

    def apply_rule(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.apply_rule(df, **kwargs)