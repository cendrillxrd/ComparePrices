from io import StringIO

import pandas as pd


def convert_wb_prices_result_to_df(get_prices_result: list[dict]) -> pd.DataFrame:
    """Преобразует данные о ценах на WB в DataFrame для воронки продаж."""
    df = pd.DataFrame(get_prices_result)

    assigned_df = df.assign(price=df['sizes'].apply(lambda x: int(x[0]['price'])),
                            price_seller=df['sizes'].apply(lambda x: int(x[0]['discountedPrice'])))
    corrected_df = assigned_df[['nmID', 'vendorCode', 'price', 'price_seller']].copy()

    corrected_df.rename({'nmID': 'Артикул WB',
                         'vendorCode': 'Артикул продавца',
                         'price': '(WB) Цена без скидки',
                         'price_seller': '(WB) Цена со скидкой продавца'},
                        inplace=True,
                        axis=1)

    return corrected_df


def convert_med_prices_result_to_df(get_prices_result) -> pd.DataFrame:
    """Преобразует данные о ценах на меде в DataFrame для воронки продаж."""
    # med_prices_df = pd.read_csv(StringIO(get_prices_result.text), encoding='utf-8')
    med_prices_df = pd.read_csv('file_prices.csv', encoding='utf-8')

    med_prices_df.rename({'Артикул': 'Артикул продавца',
                          'Цена без скидки': '(MED) Цена без скидки',
                          'Цена со скидкой': '(MED) Цена со скидкой продавца'},
                         inplace=True,
                         axis=1)

    return med_prices_df
