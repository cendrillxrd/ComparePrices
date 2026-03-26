import logging
import random
from abc import ABC, abstractmethod
from typing import Dict, Literal, Optional, Union

import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


from config import API_KEYS_WB, BASE_URLS, DELAY_INTERVAL, HEADERS, PARAMS, RETRY_TIMES, API_KEY_OZON, CLIENT_ID
from logging_config import setup_logging
from strategies.request_strategies import RequestStrategy

import time
import requests
from typing import Dict, Optional, Literal
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

setup_logging()
logger = logging.getLogger(__name__)
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger("urllib3").propagate = False


class Client(ABC):
    @abstractmethod
    def make_request(self, **kwargs):
        pass

    @abstractmethod
    def get_data(self):
        pass


class WildberriesAPIClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS
        self.api_key = API_KEYS_WB
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.__strategy = None

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def make_request(self, method: Literal['GET', 'POST'],
                     api_type: Literal['Analytics_Statistics_API_KEY', 'Price_discount_API_KEY'],
                     url_key: Literal['seller-analytics', 'discounts-prices', 'dp-calendar'],
                     endpoint: str,
                     params: Optional[Dict] = None,
                     payload: Optional[Dict] = None,
                     retries: int = RETRY_TIMES):
        url = f'{self.base_url[url_key]}{endpoint}'
        logger.info(f'Выполнение запроса по адресу {url}')
        
        for attempt in range(retries):
            self.session.headers.update({'Authorization': self.api_key[api_type]})
            response = self.session.request(method=method,
                                            url=url,
                                            params=params,
                                            json=payload,
                                            timeout=30)
            logger.info(f'Запрос выполнен успешно')
            try:
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as err:
                logger.info(f'Запрос не удался, ошибка {err.response.status_code}'
                            f'Попытка {attempt + 1}/{retries}')
                if err.response.status_code in (429, 500, 502, 503, 504):
                    wait_time = min(2 ** attempt, 10)
                    logger.debug(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    if attempt == RETRY_TIMES:
                        return None
                    continue
                raise

            except requests.exceptions.RequestException as err:
                logger.info(f'Запрос не удался, ошибка {err.response.status_code}')
                if attempt == retries - 1:
                    raise err
                time.sleep(1)

        return None

    def get_data(self, **kwargs) -> Union[list[dict], int]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)

class WildberriesHttpClient(Client):
    def __init__(self):
        self.__strategy = None

    def make_request(self, page: str, **kwargs):

        driver = self.setup_driver()

        url = f'https://www.wildberries.ru/__internal/u-catalog/sellers/v4/catalog?ab_testing=false&ab_testing=false&appType=1&curr=rub&dest=12358062&hide_dtype=11&inheritFilters=false&lang=ru&page={page}&sort=popular&spp=30&supplier=859504'
        driver.get(url)
        time.sleep(5)
        full_text = driver.find_element(By.TAG_NAME, "body").text
        data = json.loads(full_text)
        driver.quit()
        return data

    @staticmethod
    def setup_driver():
        options = Options()

        # Основные настройки для обхода детектирования
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--headless=new')

        # User-Agent
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(options=options)

        # Скрываем WebDriver свойства
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self)

class MedClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS
        self.__strategy = None

    def make_request(self, url_key: Literal['med_prices', 'med_collections_1', 'med_collections_2', 'med_purchase'], login: str = None,
                     password: str = None,):
        url = f'{self.base_url[url_key]}'
        logger.info(f'Выполнение запроса по адресу {url}')
        response = requests.get(url, auth=(login, password))
        return response

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self)

class HttpClient(Client):
    def __init__(self):
        self.__strategy = None

    def make_request(self, url):
        logger.info(f'Выполнение запроса по адресу {url}')
        response = requests.get(url)
        return response

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)

class OzonAPIClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS
        self.api_key = API_KEY_OZON
        self.client_id = CLIENT_ID
        self.session = requests.Session()
        self.__strategy = None
        self._setup_session()

    def _setup_session(self):
        """Настройка сессии с повторными попытками на уровне соединения"""
        retry_strategy = Retry(
            total=3,  # дополнительные попытки на уровне соединения
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
            # Обрабатываем ошибки соединения
            raise_on_status=False
        )

        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Базовые заголовки
        self.session.headers.update({
            'Client-Id': self.client_id,
            'Api-Key': self.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def make_request(self, method: Literal['GET', 'POST'],
                     url_key: Literal['seller-analytics', 'discounts-prices', 'dp-calendar'],
                     endpoint: str,
                     params: Optional[Dict] = None,
                     payload: Optional[Dict] = None,
                     zip_needs: bool = False,
                     retries: int = 5,
                     timeout: int = (10,60),):
        url = f'{self.base_url[url_key]}{endpoint}'

        # Устанавливаем Content-Type
        if zip_needs:
            content_type = 'application/zip'
        else:
            content_type = 'application/json'

        headers = self.session.headers.copy()
        headers['Content-Type'] = content_type

        for attempt in range(retries):
            try:
                logger.info(f'Попытка {attempt + 1}/{retries} для {url}')

                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=payload,
                    headers=headers,
                    timeout=(30, 60)  # (connect_timeout, read_timeout)
                )

                # Явная проверка на 500 до raise_for_status
                if response.status_code == 500:
                    logger.warning(f'Получена 500 ошибка (попытка {attempt + 1}/{retries})')

                    if attempt < retries - 1:
                        wait_time = min(5 * (attempt + 1), 30)  # 5, 10, 15, 20, 25 сек
                        logger.info(f'Ждем {wait_time} секунд перед повторной попыткой...')
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error('Все попытки исчерпаны, поднимаем ошибку')
                        response.raise_for_status()  # Выбросит исключение

                response.raise_for_status()
                logger.info('Запрос выполнен успешно')

                if content_type == 'application/zip':
                    return response
                return response.json()

            except requests.exceptions.HTTPError as err:
                error_status = err.response.status_code if err.response else 'unknown'
                logger.error(f'HTTP ошибка {error_status}: {err}')

                # Для ошибок сервера делаем повторные попытки
                if err.response and err.response.status_code in (429, 500, 502, 503, 504):
                    wait_time = min(2 ** attempt + random.uniform(0.1, 0.5), 30)
                    logger.info(f"Повтор через {wait_time:.1f} секунд...")
                    time.sleep(wait_time)
                    continue

                # Для клиентских ошибок не повторяем
                raise

            except requests.exceptions.ConnectionError as err:
                logger.info(f'Ошибка соединения (попытка {attempt + 1}/{retries}): {err}')

                if attempt < retries - 1:
                    wait_time = min(2 ** attempt + random.uniform(0.5, 1.5), 30)
                    logger.info(f"Повтор через {wait_time:.1f} секунд...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error('Все попытки соединения провалились')
                    raise

            except requests.exceptions.Timeout as err:
                logger.error(f'Таймаут (попытка {attempt + 1}/{retries}): {err}')

                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    logger.info(f"Повтор через {wait_time} секунд...")
                    time.sleep(wait_time)
                    continue
                raise

            except requests.exceptions.RequestException as err:
                logger.error( f'Ошибка запроса (попытка {attempt + 1}/{retries}): {err}')

                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    logger.info(f"Повтор через {wait_time} секунд...")
                    time.sleep(wait_time)
                    continue
                raise

        return None

    def get_data(self, **kwargs):
        """Основной метод для получения данных через стратегию"""
        if not self.__strategy:
            raise ValueError("Strategy not set")
        return self.__strategy.get_info(self, **kwargs)