from dataclasses import dataclass, field, asdict
import pandas as pd
from utils.date_helpers import get_today_date
from config import LIMIT_STOCKS, LIMIT_PRICE


@dataclass
class InfoDTO:
    wb_prices: pd.DataFrame
    med_prices: pd.DataFrame
    wb_stocks: pd.DataFrame


@dataclass
class StocksDTO:
    currentPeriod: dict = field(default=None)
    orderBy: dict = field(default=None)
    availabilityFilters: list = field(default=None)
    limit: int = LIMIT_STOCKS
    offset: int = 0
    stockType: str = ''
    skipDeletedNm: bool = True

    def __post_init__(self):
        if self.currentPeriod is None:
            self.currentPeriod = {
                'start': get_today_date(),
                'end': get_today_date()
            }
            self.orderBy = {
                'field': 'stockCount',
                'mode': 'desc'
            }
            self.availabilityFilters = [
                'deficient',
                'balanced',
                'actual',
                'nonActual',
                'nonLiquid',
                'invalidData'
            ]


@dataclass
class PriceDTO:
    limit: int = LIMIT_PRICE
    offset: int = 0
