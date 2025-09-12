from abc import ABC, abstractmethod

import pandas as pd


class CorrectorStrategy(ABC):
    @abstractmethod
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


class CorrPricesStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)

        columns_name = ['(MED) Цена без скидки', '(MED) Цена со скидкой продавца']
        for col in columns_name:
            df[col] = pd.to_numeric(df[col], downcast="integer")


        return df


class CorrStocksStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.drop(['Остаток', 'В пути к клиенту', 'В пути от клиента'], axis=1, inplace=True)
        return df


class CorrWbPricesStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df['Скидка WB'] = 100 - round((df['(WB) Цена со скидкой WB\n(черная)'] / df['(WB) Цена со скидкой продавца']) * 100)

        return df[['Артикул WB',
                   'Артикул продавца',
                   'Категория',
                   'Наименование',
                   'Бренд',
                   '(WB) Цена без скидки\n(зачеркнутая)',
                   'Скидка продавца',
                   '(WB) Цена со скидкой продавца',
                   'Скидка WB',
                   '(WB) Цена со скидкой WB\n(черная)',
                   '(WB) Цена со скидкой WB клуба\n(красная/фиолетовая)',]]


class CorrCollectionsStrategy(CorrectorStrategy):
    def correcting(self, df: pd.DataFrame) -> pd.DataFrame:
        df.fillna(0, inplace=True)
        df['Скидка для равновесия'] = round(100 * (1 - df['(MED) Цена со скидкой продавца'] / df['(WB) Цена со скидкой WB\n(черная)']))
        df['Скидка для равновесия'] = df['Скидка для равновесия'].clip(lower=0)
        df['Разность цен ●'] = df['(MED) Цена со скидкой продавца'] - df['(WB) Цена со скидкой WB\n(черная)']
        return df[['Артикул WB',
                   'Артикул продавца',
                   'Категория',
                   'Наименование',
                   'Бренд',
                   'Коллекция',
                   '(WB) Цена без скидки\n(зачеркнутая)',
                   'Скидка продавца',
                   '(WB) Цена со скидкой продавца',
                   'Скидка WB',
                   '(WB) Цена со скидкой WB\n(черная)',
                   '(WB) Цена со скидкой WB клуба\n(красная/фиолетовая)',
                   '(MED) Цена без скидки',
                   '(MED) Цена со скидкой продавца',
                   'Разность цен ●',
                   'Скидка для равновесия',]]
