import pandas as pd


class Merger:
    def merge(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        wb_med = pd.merge(df1, df2, on='Артикул продавца', how='left')
        return wb_med
