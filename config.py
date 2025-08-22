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
    'med': 'https://med-online.ru/upload/acrit.exportproplus/file.prices.csv?1755164681'
}

FILE_PATH = 'C:/Users/Admin/Desktop/'

LIMIT_PRICE = 1000  # <= 1000
LIMIT_STOCKS = 1000  # <= 1000

TIME_SLEEP_PRICE = 1  # >= 0.6
TIME_SLEEP_STOCKS = 20  # >= 20

