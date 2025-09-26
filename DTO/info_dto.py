from dataclasses import asdict, dataclass

import pandas as pd


@dataclass
class InfoDTO:
    wb_prices: pd.DataFrame
    med_prices: pd.DataFrame
    wb_cards_prices: pd.DataFrame
    med_collection_1: pd.DataFrame
    med_collection_2: pd.DataFrame
    wb_promotions: pd.DataFrame
    # wb_fbs_stocks: pd.DataFrame
    # wb_fbw_stocks: pd.DataFrame
