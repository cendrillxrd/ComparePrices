import asyncio
import logging
from typing import Tuple
import time
import aiohttp
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random
import chromedriver_autoinstaller

from utils.prices_helper import clean_price
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class OzonPriceParser:
    def __init__(self, max_workers=5, delay_range=(1, 3)):
        self.results = []
        self.max_workers = max_workers
        self.delay_range = delay_range
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    @staticmethod
    def extract_class_values(html_content: str) -> Tuple[str, str]:
        """Извлекает значения цен из HTML контента"""
        soup = BeautifulSoup(html_content, 'html.parser')

        tsHeadline600Large = soup.find(class_="tsHeadline600Large")
        pdp_b7f_tsHeadline500Medium = soup.find(class_="pdp_bi2 tsHeadline500Medium")

        value1 = clean_price(tsHeadline600Large.get_text(strip=True)) if tsHeadline600Large else "Не найдено"
        value2 = clean_price(
            pdp_b7f_tsHeadline500Medium.get_text(strip=True)) if pdp_b7f_tsHeadline500Medium else "Не найдено"

        return value1, value2
    @staticmethod
    def get_cookies():

        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)

        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.implicitly_wait(60)
            driver.get("https://www.ozon.ru")
            time.sleep(random.uniform(2, 5))
            driver.find_element(By.CSS_SELECTOR, "#stickyHeader")
            user_agent = driver.execute_script("return navigator.userAgent")
            cookies = driver.get_cookies()

            cookies_dict = {i["name"]: i["value"] for i in cookies}
            return user_agent, cookies_dict
        finally:
            driver.quit()
    # @staticmethod
    # def get_cookies():
    #     chromedriver_autoinstaller.install()
    #     options = uc.ChromeOptions()
    #     options.add_argument('--disable-blink-features=AutomationControlled')
    #     """Получение cookies с рандомизированными задержками"""
    #     with uc.Chrome(options=options, use_subprocess=True, version_main=None) as driver:
    #         driver.implicitly_wait(60)
    #         driver.get("https://www.ozon.ru")
    #         time.sleep(random.uniform(2, 5))  # Случайная задержка
    #         driver.find_element(By.CSS_SELECTOR, "#stickyHeader")
    #         user_agent = driver.execute_script("return navigator.userAgent")
    #         cookies = driver.get_cookies()
    #
    #     cookies_dict = {i["name"]: i["value"] for i in cookies}
    #     return user_agent, cookies_dict

    async def process_batch(self, articles, user_agent, cookies_dict, batch_size=10, delay_between_batches=5):
        """Обработка батчами с задержками"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            results = []
            total_processed = 0  # Счетчик обработанных товаров

            for i, article in enumerate(articles):
                # Добавляем случайную задержку между запросами
                delay = random.uniform(0.5, 2) if i > 0 else 0

                task = self.get_product_data_with_retry(session, article, user_agent, cookies_dict, delay=delay)
                tasks.append(task)

                # Обрабатываем батчами
                if len(tasks) >= batch_size:
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    valid_results = [r for r in batch_results if not isinstance(r, Exception)]
                    results.extend(valid_results)
                    total_processed += len(valid_results)
                    tasks = []

                    logger.info(f'Обработан батч из {len(valid_results)} товаров. Всего обработано: {total_processed}/{len(articles)}')

                    # Задержка между батчами
                    if i < len(articles) - 1:
                        await asyncio.sleep(delay_between_batches)

            # Обрабатываем оставшиеся задачи
            if tasks:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                valid_results = [r for r in batch_results if not isinstance(r, Exception)]
                results.extend(valid_results)
                total_processed += len(valid_results)

            logger.info(f'Обработка завершена. Всего обработано товаров: {total_processed}/{len(articles)}')

            return results
    @staticmethod
    async def get_product_data_with_retry(session, article, user_agent, cookies_dict, max_retries=5, delay=0):
        """Асинхронное получение данных товара с повторными попытками при блокировке"""
        if delay > 0:
            await asyncio.sleep(delay)

        url = f"https://www.ozon.ru/product/{article}/"

        for attempt in range(max_retries):
            try:
                async with session.get(url, cookies=cookies_dict, headers={"user-agent": user_agent}) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        parser = OzonPriceParser()
                        price1, price2 = parser.extract_class_values(response_text)
                        logger.info(f"Обработан {article}: {price1}, {price2}")

                        return [article, price1, price2]

                    elif response.status in [403, 429, 503]:  # Коды, которые могут означать блокировку
                        logger.info(f"Блокировка для {article}: HTTP {response.status} (попытка {attempt + 1}/{max_retries})")

                        if attempt < max_retries - 1:  # Если это не последняя попытка
                            wait_time = 300 * attempt # Ожидание 5 минут
                            logger.info(f"Ожидание {wait_time} секунд перед повторной попыткой...")
                            await asyncio.sleep(wait_time)

                            continue
                        else:
                            logger.info(f"Превышено количество попыток для {article}: HTTP {response.status}")
                            return [article, f"HTTP {response.status}", "Блокировка"]
                    else:
                        logger.info(f"Ошибка для {article}: HTTP {response.status}")
                        return [article, f"HTTP {response.status}", "Ошибка"]

            except Exception as e:
                logger.info(f"Ошибка для {article} (попытка {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 60
                    logger.info( f"Ожидание {wait_time} секунд перед повторной попыткой...")
                    await asyncio.sleep(wait_time)
                else:
                    return [article, "Ошибка", str(e)]

        return [article, "Не удалось получить данные", "Превышено количество попыток"]