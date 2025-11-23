import pandas as pd
import re
import logging

from DTO.ozon_columns_dto import OZONColumnsDTO
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
columns = OZONColumnsDTO()

def transform_dataframe(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Преобразует датафрейм, создавая колонку с отформатированными названиями"""

    def format_name(row):
        name = str(row[columns.name]).lower()
        article = str(row[columns.ozon_article])

        cyrillic_to_latin = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
            'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya', ' ': '-'
        }

        latin_name = ''
        for char in name:
            if char in cyrillic_to_latin:
                latin_name += cyrillic_to_latin[char]
            elif char.isalnum():
                latin_name += char
            else:
                latin_name += '-'

        latin_name = re.sub(r'-+', '-', latin_name)
        latin_name = latin_name.strip('-')
        return f"{latin_name}-{article}"

    df[col_name] = df.apply(format_name, axis=1)
    logger.info(f'Сгенерировано {len(df)} url')
    return df


def clean_price(price_text: str) -> str:
    """Очищает цену от тонких пробелов и других ненужных символов"""
    if not price_text or price_text == "Не найдено":
        return price_text
    cleaned_price = price_text.replace(' ', '').replace(' ', '')
    return cleaned_price