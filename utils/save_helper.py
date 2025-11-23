import pandas as pd
from DTO.ozon_columns_dto import OZONColumnsDTO
columns_dto = OZONColumnsDTO()

def save_results(results, col_name):
    """Сохранение результатов в CSV"""
    df = pd.DataFrame(results, columns=[col_name, columns_dto.price_with_ozon_club,
                                        columns_dto.price_with_ozon_discount])
    return df