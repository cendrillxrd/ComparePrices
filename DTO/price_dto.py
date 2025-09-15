from dataclasses import asdict, dataclass

from config import LIMIT_PRICE


@dataclass
class PriceDTO:
    limit: int = LIMIT_PRICE
    offset: int = 0
