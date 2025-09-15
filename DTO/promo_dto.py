from dataclasses import asdict, dataclass

import pandas as pd

from utils.date_helpers import get_current_date_iso


@dataclass
class PromoDTO:
    startDateTime: str = get_current_date_iso('start')
    endDateTime: str = get_current_date_iso('end')
    allPromo: bool = False