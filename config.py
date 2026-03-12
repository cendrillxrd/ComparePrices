import os
from pathlib import Path

from dotenv import load_dotenv

from DTO.columns_dto import WBColumnsDTO
from DTO.ozon_columns_dto import OZONColumnsDTO

wb_columns = WBColumnsDTO()
ozon_columns = OZONColumnsDTO()

load_dotenv()

API_KEYS_WB = {
    'Price_discount_API_KEY': os.getenv('PRICE_DISCOUNT_API_KEY'),
    'Analytics_Statistics_API_KEY': os.getenv('ANALYTICS_STATISTICS_API_KEY')
}

PURCHASE_LOGIN = os.getenv('PURCHASE_LOGIN')
PURCHASE_PASSWORD = os.getenv('PURCHASE_PASSWORD')

API_KEY_OZON = os.getenv('OZON_API_KEY')
CLIENT_ID = os.getenv('CLIENT_ID')

YANDEX_API = os.getenv('YANDEX_API')

BASE_URLS = {
    'dp-calendar': 'https://dp-calendar-api.wildberries.ru',
    'discounts-prices': 'https://discounts-prices-api.wildberries.ru',
    'seller-analytics': 'https://seller-analytics-api.wildberries.ru',
    'med_prices': 'https://med-online.ru/upload/acrit.exportproplus/file.prices.csv?1769758965',
    'wb_http': 'https://catalog.wb.ru/sellers/v4/catalog',
    'med_collections_1': 'https://med-online.ru/upload/acrit.exportproplus/file.OZON.xlsx?1740656479',
    'med_collections_2': 'https://med-online.ru/upload/acrit.exportproplus/file.OZONdop.xlsx?1744707024',
    'med_collections_3': 'https://med-online.ru/upload/acrit.exportproplus/file.match-bikk.xlsx?1769676747',
    'med_collections_4': 'https://med-online.ru/upload/acrit.exportproplus/file.Strell-Truss-Redp.xlsx?1772624157',
    'med_purchase': 'https://med-online.ru/upload/1cdata/cost.csv',
    'http': '',
    'ozon': 'https://api-seller.ozon.ru',
}

MAIN_OZON_BRANDS = ['LTB', 'Armani Exchange', 'Bikkembergs']

BASE_COLUMNS_NAME_WB = {'nmID': wb_columns.wb_article,
                     'vendorCode': wb_columns.seller_article,
                     'Артикул': wb_columns.seller_article,
                     'price': wb_columns.wb_price_without_discount,
                     'price_seller': wb_columns.wb_price_with_seller_discount,
                     'Цена без скидки': wb_columns.med_price_without_discount,
                     'Цена со скидкой': wb_columns.med_price_with_discount,
                     'subjectName': wb_columns.category,
                     'name': wb_columns.name,
                     'brandName': wb_columns.name,
                     'stock_fbw': wb_columns.stock_fbw,
                     'stock_fbs': wb_columns.stock_fbs,
                     'discount': wb_columns.seller_discount,
                     'planDiscount': wb_columns.plan_discount,
                     'id': wb_columns.wb_article,
                     'ID': wb_columns.ozon_id,
                     'toClientCount': wb_columns.stock_in_way_to_client,
                     'fromClientCount': wb_columns.stock_in_way_from_client,
                     'OfferId': wb_columns.ozon_id,
                     'Cost': wb_columns.purchase,
                     'status': 'Статус загрузки',
                     'uploadID': 'ID загрузки',
                     'uploadDate': 'Дата',
                     'overAllGoodsNumber': 'Всего товаров',
                     'successGoodsNumber': 'Товаров без ошибок',
                     'techSizeName': 'Размер',
                     'clubDiscount': 'Скидка WB клуба',
                     'errorText': 'Текст ошибки'
                         }

BASE_COLUMNS_NAME_OZON = {'ID': ozon_columns.ozon_id,
                        'offer_id': ozon_columns.ozon_id,
                        'Артикул': ozon_columns.ozon_id,
                        'SKU': ozon_columns.ozon_article,
                        'sku': ozon_columns.ozon_article,
                        'return_from_customer_stock_count': ozon_columns.in_way_from_client,
                        'subjectName': ozon_columns.name,
                        'Barcode': ozon_columns.barcode,
                        'Тип': ozon_columns.category,
                        'Название товара': ozon_columns.name,
                        'Доступно к продаже по схеме FBS, шт.':  ozon_columns.fbs_stocks,
                        'Зарезервировано, шт': ozon_columns.fbs_reserv,
                        'Доступно к продаже по схеме FBO, шт.': ozon_columns.fbo_stocks,
                        'Зарезервировано на моих складах, шт': ozon_columns.fbo_reserv,
                        'Цена до скидки (перечеркнутая цена), ₽': ozon_columns.price_without_discount,
                        'Количество': ozon_columns.in_way_to_client,
                        'price': ozon_columns.price_with_seller_discount
                        }

TASKS_STATUS = 'Tasks_status'

LIMIT_PRICE = 1000  # <= 1000
LIMIT_STOCKS = 1000  # <= 1000
LIMIT_PROMO_GOODS = 1000 # <= 1000
LIMIT_NEW_PRICE_TASK = 1000 # <= 1000

TIME_SLEEP_PRICE = 1  # >= 0.6
TIME_SLEEP_STOCKS = 20  # >= 20
TIME_SLEEP_NEW_PRICE_TASK = 1 # >= 0.6

# BASE_MP_COMMISSION = 0.55
BASE_MP_COMMISSION = 55

DELAY_INTERVAL=10

HEADERS = {
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
     "Referer": "https://www.wildberries.ru/seller/859504?sort=popular&page=",
     "Content-Encoding":"gzip, deflate, br, zstd",
     "Content-Type":"application/json",
     "sec-ch-ua":'"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',

}

USER_AGENTS = [
    # Chrome на Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',

    # Chrome на Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',

    # Firefox на Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',

    # Firefox на Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',

    # Safari
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',

    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',

    # Мобильные устройства
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
]

PARAMS = {
    'ab_testing': 'false',
    'appType': '1',
    'curr': 'rub',
    'dest': '12358062',
    'lang': 'ru',
    'sort': 'popular',
    'spp': '30',
    'supplier': '859504',
}

CLUB_PROCENT = 2

WB_EXCEL_FILE_NAME = 'compare_price_wb'
OZON_EXCEL_FILE_NAME = 'compare_price_ozon'

RETRY_TIMES = 5


ORDER_STATUSES = ['Ожидает в ПВЗ', 'Доставляется', 'Ожидает сборки', 'Ожидает отгрузки']

LIMIT_FUNNEL = 1000
TIME_SLEEP_FUNNEL = 60
TIME_SLEEP_REPORT = 60
TIME_SLEEP_CARDS_LINK = 30
TIME_SLEEP_STOCKS_FBS = 1
TIME_SLEEP_PRICES = 1


YANDEX_FILE_NAME = 'prices.csv'
YANDEX_DIR_NAME = 'Цены OZON'
MAIN_DIR = f'{str(Path(__file__).parent)}'
MAIN_DIR_PRICES = f'{str(Path(__file__).parent.joinpath(YANDEX_FILE_NAME))}'