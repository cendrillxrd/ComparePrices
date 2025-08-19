import pandas as pd


def convert_prices_result_to_df(get_prices_result: list[dict]) -> pd.DataFrame:
    """Преобразует данные о ценах в DataFrame для воронки продаж."""
    df = pd.DataFrame(get_prices_result)

    assigned_df = df.assign(price=df['sizes'].apply(lambda x: int(x[0]['price'])),
                            price_seller=df['sizes'].apply(lambda x: int(x[0]['discountedPrice'])))
    corrected_df = assigned_df[['nmID', 'price', 'price_seller']].copy()

    corrected_df.rename({'nmID': 'Артикул WB',
                         'price': 'Цена',
                         'price_seller': 'Цена со скидкой продавца'},
                        inplace=True,
                        axis=1)

    return corrected_df
