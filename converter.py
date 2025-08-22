from strategies.convert_strategies import ConverterStrategy


class Converter:
    def __init__(self, strategy: ConverterStrategy):
        self.strategy = strategy

    def convert(self, data):
        return self.strategy.converting(data)
