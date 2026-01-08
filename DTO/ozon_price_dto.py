from dataclasses import asdict, dataclass, field

from config import LIMIT_PRICE


@dataclass
class OZONPriceDTO:
    limit: int = LIMIT_PRICE
    filter: dict = field(default_factory=lambda: {
        "visibility": "ALL"
    })