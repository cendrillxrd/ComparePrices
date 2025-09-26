from dataclasses import asdict, dataclass

@dataclass
class DopColumnsDTO:
    solution: str = 'Решение в разрезе остатка'
    new_discount: str = 'Новая скидка'
    purchase: str = 'Закупка'
    mp_commission: str = 'Комиссия МП'
    mu_original: str = 'МU исходный'
    mu_with_our_discount: str = 'MU с учетом нашей скидки'
    mu_with_discount_from_the_price_with_spp: str = 'MU с учетом скидки от цены с СПП (идет в ОК и выручку)'
    mu_taking_into_account_the_wb_commission: str = 'MU с учетом комиссии ВБ (от нашей цены)'
    max_discount_including_commission: str = 'Макс скидка с учетом комиссии'