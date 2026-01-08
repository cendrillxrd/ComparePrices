
from dataclasses import asdict, dataclass
from typing import Optional

import pandas as pd


@dataclass
class InfoOZONDTO:
    funnel: Optional[pd.DataFrame] = None
    stocks: Optional[pd.DataFrame] = None
    to_client: Optional[pd.DataFrame] = None
    from_client: Optional[pd.DataFrame] = None
    med_prices: Optional[pd.DataFrame] = None
    prices: Optional[pd.DataFrame] = None
    cards_info: Optional[pd.DataFrame] = None
    collections_first: Optional[pd.DataFrame] = None
    collections_second: Optional[pd.DataFrame] = None
    purchase: Optional[pd.DataFrame] = None
    seller_prices: Optional[pd.DataFrame] = None