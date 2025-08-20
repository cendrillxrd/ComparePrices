import pandas as pd


def wb_and_med_merge(wb: pd.DataFrame, med: pd.DataFrame) -> pd.DataFrame:
    wb_med = pd.merge(wb, med, on='Артикул продавца', how='left')
    return wb_med
