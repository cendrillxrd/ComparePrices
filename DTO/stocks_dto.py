from dataclasses import asdict, dataclass, field

from config import LIMIT_STOCKS
from utils.date_helpers import get_today_date


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