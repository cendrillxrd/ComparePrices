import pandas as pd
from DTO.columns_dto import WBColumnsDTO
columns_dto = WBColumnsDTO()

def get_seller_discount_df(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df[[columns_dto.wb_article, columns_dto.seller_discount]].copy()
    new_df.rename({columns_dto.seller_discount: 'Старая скидка продавца'}, axis=1, inplace=True)
    return new_df