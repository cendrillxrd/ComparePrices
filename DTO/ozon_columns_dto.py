from dataclasses import asdict, dataclass


@dataclass
class OZONColumnsDTO:
    ozon_id: str = 'OZON ID'
    ozon_article: str = 'Артикул OZON'
    seller_article: str = 'Артикул продавца'
    barcode: str = 'Баркод'
    # date: str = 'Дата'
    # year: str = 'Год'
    # month: str = 'Месяц'
    # week: str = 'Неделя'
    brand: str = 'Бренд'
    category: str = 'Тип'
    collection: str = 'Коллекция'
    name: str = 'Название предмета'
    fbs_stocks: str = 'Остатки FBS'
    fbs_reserv: str = 'Зарезервировано FBS'
    fbo_stocks: str = 'Остатки FBO'
    fbo_reserv: str = 'Зарезервировано FBO'
    in_way_to_client: str = 'В пути к клиенту'
    in_way_from_client: str = 'В пути от клиента'
    price_with_ozon_club: str = 'Цена с озон картой (Зеленая)'
    price_with_ozon_discount: str = 'Цена со скидкой озон (Черная)'
    price_without_discount: str = 'Цена без скидки (Зачеркнутая)'
    status: str = 'Статус товара'
    purchase: str = 'Закупка'