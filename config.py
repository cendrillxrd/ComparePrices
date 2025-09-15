import os

from dotenv import load_dotenv

from DTO.columns_dto import ColumnsDTO

columns = ColumnsDTO()

load_dotenv()

API_KEYS = {
    'Price_discount_API_KEY': os.getenv('PRICE_DISCOUNT_API_KEY'),
    'Analytics_Statistics_API_KEY': os.getenv('ANALYTICS_STATISTICS_API_KEY')
}

BASE_URLS = {
    'dp-calendar': 'https://dp-calendar-api.wildberries.ru',
    'discounts-prices': 'https://discounts-prices-api.wildberries.ru',
    'seller-analytics': 'https://seller-analytics-api.wildberries.ru',
    'med_prices': 'https://med-online.ru/upload/acrit.exportproplus/file.prices.csv?1755164681',
    'wb_http': 'https://catalog.wb.ru/sellers/v4/catalog',
    'med_collections_1': 'https://med-online.ru/upload/acrit.exportproplus/file.OZON.xlsx?1740656479',
    'med_collections_2': 'https://med-online.ru/upload/acrit.exportproplus/file.OZONdop.xlsx?1744707024'
}

BASE_COLUMNS_NAME = {'nmID': columns.wb_article,
                     'vendorCode': columns.seller_article,
                     'Артикул': columns.seller_article,
                     'price': columns.wb_price_without_discount,
                     'price_seller': columns.wb_price_with_seller_discount,
                     'Цена без скидки': columns.med_price_without_discount,
                     'Цена со скидкой': columns.med_price_with_discount,
                     'subjectName': columns.category,
                     'name': columns.name,
                     'brandName': columns.name,
                     'stockCount': columns.stock_count,
                     'toClientCount': columns.to_client_count,
                     'fromClientCount': columns.to_client_count,
                     'discount': columns.seller_discount,
                     'planDiscount': columns.plan_discount,
                     'id': columns.wb_article,
                     }

FILE_PATH = 'C:/Users/Admin/Desktop/'

LIMIT_PRICE = 1000  # <= 1000
LIMIT_STOCKS = 1000  # <= 1000
LIMIT_PROMO_GOODS = 1000 # <= 1000

TIME_SLEEP_PRICE = 1  # >= 0.6
TIME_SLEEP_STOCKS = 20  # >= 20

COLUMNS_FOR_EXCEL_FORMATTER = {
    "discount_wb": columns.wb_discount,
    "price_diff": columns.price_difference,
    "med_price": columns.med_price_with_discount,
    "wb_price": columns.wb_price_with_wb_discount,
    'seller_discount': columns.seller_discount,
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