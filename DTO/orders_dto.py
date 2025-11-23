from dataclasses import asdict, dataclass, field

from utils.date_helpers import get_3_week_ago_date_for_orders, get_today_date_for_orders


@dataclass
class OrdersDTO:
    filter: dict = field(default_factory=lambda: {
        "processed_at_from": get_3_week_ago_date_for_orders(),
        "processed_at_to": get_today_date_for_orders(),
        # "is_express": '',
        "sku": [],
        "cancel_reason_id": [],
        "offer_id": "",
        "status_alias": [],
        "statuses": [],
        "title": ""
    })
    # language: str = "DEFAULT",