from dataclasses import dataclass, asdict

@dataclass
class ColumnsDTO:
    wb_article: str = 'Артикул WB'
    seller_article: str = 'Артикул продавца'
    category: str = 'Категория'
    name: str = 'Наименование'
    brand: str = 'Бренд'
    collection: str = 'Коллекция'
    wb_price_without_discount: str = '(WB) Цена без скидки\n(зачеркнутая)'
    seller_discount: str = 'Скидка продавца'
    wb_price_with_seller_discount: str = '(WB) Цена со скидкой продавца'
    wb_discount: str = 'Скидка WB'
    wb_price_with_wb_discount: str = '(WB) Цена со скидкой WB\n(черная)'
    wb_price_with_wb_club: str = '(WB) Цена со скидкой WB клуба\n(красная/фиолетовая)'
    med_price_without_discount: str = '(MED) Цена без скидки'
    med_price_with_discount: str = '(MED) Цена со скидкой продавца'
    price_difference: str = 'Разность цен ●'
    equilibrium_discount: str = 'Скидка для равновесия'
    stock_count: str = 'Остаток',
    to_client_count: str = 'В пути к клиенту',
    from_client_count: str = 'В пути от клиента'