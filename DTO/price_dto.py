from dataclasses import dataclass, asdict
from config import LIMIT_PRICE


@dataclass
class PriceDTO:
    limit: int = LIMIT_PRICE
    offset: int = 0
