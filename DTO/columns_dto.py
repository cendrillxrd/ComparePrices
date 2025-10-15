from dataclasses import asdict, dataclass


@dataclass
class ColumnsDTO:
    wb_article: str = 'Артикул WB'
    seller_article: str = 'Артикул продавца'
    ozon_id: str = 'Ozon ID'
    category: str = 'Категория'
    name: str = 'Наименование'
    brand: str = 'Бренд'
    collection: str = 'Коллекция'
    stock_fbw: str = 'Остаток FBW'
    stock_fbs: str = 'Остаток FBS'
    stock_in_way_to_client: str = 'В пути к клиенту'
    stock_in_way_from_client: str = 'В пути от клиента'
    wb_price_without_discount: str = 'РРЦ'
    seller_discount: str = '(WB) Скидка продавца'
    wb_price_with_seller_discount: str = '(WB) Цена со скидкой продавца'
    wb_discount: str = 'Скидка WB'
    wb_price_with_wb_discount: str = '(WB) Цена со скидкой WB\n(черная)'
    wb_price_with_wb_club: str = '(WB) Цена со скидкой WB клуба\n(красная/фиолетовая)'
    med_price_without_discount: str = '(MED) Цена без скидки'
    med_discount: str = '(MED) Скидка продавца'
    med_price_with_discount: str = '(MED) Цена со скидкой продавца'
    price_difference: str = 'Разность цен ●'
    equilibrium_discount: str = 'Скидка для равновесия'
    plan_discount: str = 'Скидка для акции'
    purchase: str = 'Закупка'