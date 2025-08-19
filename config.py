import os

from dotenv import load_dotenv

load_dotenv()

API_KEYS = {
    'Price_discount_API_KEY': os.getenv('PRICE_DISCOUNT_API_KEY')
}

BASE_URLS = {
    'discounts-prices': 'https://discounts-prices-api.wildberries.ru'
}

FILE_PATH = 'C:/Users/Admin/Desktop/'
