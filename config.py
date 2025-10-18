import os

from dotenv import load_dotenv

from DTO.columns_dto import ColumnsDTO

columns = ColumnsDTO()

load_dotenv()

API_KEYS = {
    'Price_discount_API_KEY': os.getenv('PRICE_DISCOUNT_API_KEY'),
    'Analytics_Statistics_API_KEY': os.getenv('ANALYTICS_STATISTICS_API_KEY')
}

PURCHASE_LOGIN = os.getenv('PURCHASE_LOGIN')
PURCHASE_PASSWORD = os.getenv('PURCHASE_PASSWORD')

BASE_URLS = {
    'dp-calendar': 'https://dp-calendar-api.wildberries.ru',
    'discounts-prices': 'https://discounts-prices-api.wildberries.ru',
    'seller-analytics': 'https://seller-analytics-api.wildberries.ru',
    'med_prices': 'https://med-online.ru/upload/acrit.exportproplus/file.prices.csv?1755164681',
    'wb_http': 'https://catalog.wb.ru/sellers/v4/catalog',
    'med_collections_1': 'https://med-online.ru/upload/acrit.exportproplus/file.OZON.xlsx?1740656479',
    'med_collections_2': 'https://med-online.ru/upload/acrit.exportproplus/file.OZONdop.xlsx?1744707024',
    'med_purchase': 'https://med-online.ru/upload/1cdata/cost.csv'
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
                     'stock_fbw': columns.stock_fbw,
                     'stock_fbs': columns.stock_fbs,
                     'discount': columns.seller_discount,
                     'planDiscount': columns.plan_discount,
                     'id': columns.wb_article,
                     'ID': columns.ozon_id,
                     'toClientCount': columns.stock_in_way_to_client,
                     'fromClientCount': columns.stock_in_way_from_client,
                     'OfferId': columns.ozon_id,
                     'Cost': columns.purchase,
                     'status': 'Статус загрузки',
                     'uploadID': 'ID загрузки',
                     'uploadDate': 'Дата',
                     'overAllGoodsNumber': 'Всего товаров',
                     'successGoodsNumber': 'Товаров без ошибок',
                     'techSizeName': 'Размер',
                     'clubDiscount': 'Скидка WB клуба',
                     'errorText': 'Текст ошибки'
                     }

FILE_PATH = 'C:/Users/Admin/Desktop/'

LIMIT_PRICE = 1000  # <= 1000
LIMIT_STOCKS = 1000  # <= 1000
LIMIT_PROMO_GOODS = 1000 # <= 1000
LIMIT_NEW_PRICE_TASK = 1000 # <= 1000

TIME_SLEEP_PRICE = 1  # >= 0.6
TIME_SLEEP_STOCKS = 20  # >= 20
TIME_SLEEP_NEW_PRICE_TASK = 1 # >= 0.6

BASE_MP_COMMISSION = 0.5

DELAY_INTERVAL=20

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

EXCEL_FILE_NAME = 'compare_price'