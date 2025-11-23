from dataclasses import asdict, dataclass
from typing import Optional

import pandas as pd


@dataclass
class InfoWBDTO:
    wb_prices: Optional[pd.DataFrame] = None
    med_prices: Optional[pd.DataFrame] = None
    wb_cards_prices: Optional[pd.DataFrame] = None
    med_collection_1: Optional[pd.DataFrame] = None
    med_collection_2: Optional[pd.DataFrame] = None
    wb_promotions: Optional[pd.DataFrame] = None
    wb_fbs_stocks: Optional[pd.DataFrame] = None
    wb_fbw_stocks: Optional[pd.DataFrame] = None
    purchase: Optional[pd.DataFrame] = None