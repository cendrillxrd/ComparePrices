from dataclasses import asdict, dataclass, field

from config import LIMIT_PROMO_GOODS


@dataclass
class PromoGoodsDTO:
    inAction: bool = False
    limit: int = LIMIT_PROMO_GOODS
    offset: int = 0
