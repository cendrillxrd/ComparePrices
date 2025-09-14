import pandas as pd
from strategies.convert_strategies import ConverterStrategy
from typing import Union


class Converter:
    def __init__(self):
        self.__strategy = None

    def set_strategy(self, strategy: ConverterStrategy):
        self.__strategy = strategy

    def convert(self, data) -> Union[pd.DataFrame, list]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.converting(data)
