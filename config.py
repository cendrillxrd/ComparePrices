import os

from dotenv import load_dotenv

load_dotenv()

API_KEYS = {
    'Price_discount_API_KEY': os.getenv('PRICE_DISCOUNT_API_KEY')
}

BASE_URLS = {
    'discounts-prices': 'https://discounts-prices-api.wildberries.ru',
    'med': 'https://med-online.ru/upload/acrit.exportproplus/file.prices.csv?1755164681'
}

FILE_PATH = 'C:/Users/Admin/Desktop/'
