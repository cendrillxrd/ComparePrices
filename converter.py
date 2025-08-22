from strategies.convert_strategies import ConverterStrategy


class Converter:
    def __init__(self, strategy: ConverterStrategy):
        self.__strategy = strategy

    def set_strategy(self, strategy: ConverterStrategy):
        self.__strategy = strategy

    def convert(self, data):
        return self.__strategy.converting(data)
