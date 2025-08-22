import pandas as pd


def apply_rules(merged_df: pd.DataFrame, stocks_df: pd.DataFrame) -> pd.DataFrame:
    result_df = merged_df[merged_df['Артикул WB'].isin(stocks_df['Артикул WB'])].copy()
    result_df.fillna(0, inplace=True)
    result_df['(MED) Цена без скидки'] = pd.to_numeric(result_df['(MED) Цена без скидки'],
                                                       downcast="integer")
    result_df['(MED) Цена со скидкой продавца'] = pd.to_numeric(result_df['(MED) Цена со скидкой продавца'],
                                                                downcast="integer")
    return result_df
