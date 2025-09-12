import os

from dotenv import load_dotenv

load_dotenv()

API_KEYS = {
    'Price_discount_API_KEY': os.getenv('PRICE_DISCOUNT_API_KEY'),
    'Analytics_Statistics_API_KEY': os.getenv('ANALYTICS_STATISTICS_API_KEY')
}

BASE_URLS = {
    'discounts-prices': 'https://discounts-prices-api.wildberries.ru',
    'seller-analytics': 'https://seller-analytics-api.wildberries.ru',
    'med_prices': 'https://med-online.ru/upload/acrit.exportproplus/file.prices.csv?1755164681',
    'wb_http': 'https://catalog.wb.ru/sellers/v4/catalog',
    'med_collections_1': 'https://med-online.ru/upload/acrit.exportproplus/file.OZON.xlsx?1740656479',
    'med_collections_2': 'https://med-online.ru/upload/acrit.exportproplus/file.OZONdop.xlsx?1744707024'
}

BASE_COLUMNS_NAME = {'nmID': 'Артикул WB',
                     'vendorCode': 'Артикул продавца',
                     'Артикул': 'Артикул продавца',
                     'price': '(WB) Цена без скидки',
                     'price_seller': '(WB) Цена со скидкой продавца',
                     'Цена без скидки': '(MED) Цена без скидки',
                     'Цена со скидкой': '(MED) Цена со скидкой продавца',
                     'subjectName': 'Категория',
                     'name': 'Наименование',
                     'brandName': 'Бренд',
                     'stockCount': 'Остаток',
                     'toClientCount': 'В пути к клиенту',
                     'fromClientCount': 'В пути от клиента'
                     }

FILE_PATH = 'C:/Users/Admin/Desktop/'

LIMIT_PRICE = 1000  # <= 1000
LIMIT_STOCKS = 1000  # <= 1000

TIME_SLEEP_PRICE = 1  # >= 0.6
TIME_SLEEP_STOCKS = 20  # >= 20

COLUMNS_FOR_EXCEL_FORMATTER = {
    "discount_wb": "Скидка WB",
    "price_diff": "Разность цен ●",
    "med_price": "(MED) Цена со скидкой продавца",
    "wb_price": "(WB) Цена со скидкой WB",
}

DELAY_INTERVAL=10

HEADERS = {
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
     "Access-Control-Allow-Credentials": "true",
     "Access-Control-Allow-Headers":"Authorization, x-pow, x-captcha-id, x-userdata",
     "Access-Control-Allow-Methods":"HEAD,GET,OPTIONS",
     "Referer": "https://www.wildberries.ru/seller/859504?sort=popular&page=",
     "Access-control-Allow-Origin":"https://www.wildberries.ru",
     "Content-Encoding":"gzip",
     "Content-Type":"application/json"
 }

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