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


import time
import json
from json import JSONDecodeError
from selenium.common.exceptions import TimeoutException, WebDriverException


class WildberriesHttpClient(Client):
    def __init__(self):
        self.__strategy = None
        self.max_retries = 3  # Максимальное количество попыток
        self.retry_delay = 5  # Начальная задержка в секундах

    def make_request(self, page: str, **kwargs):
        """Метод с автоматическими повторными попытками при ошибках"""

        for attempt in range(self.max_retries):
            driver = None
            try:
                print(f"Попытка {attempt + 1} из {self.max_retries} для страницы {page}")

                driver = self.setup_driver()

                url = f'https://www.wildberries.ru/__internal/u-catalog/sellers/v4/catalog?ab_testing=false&ab_testing=false&appType=1&curr=rub&dest=12358062&hide_dtype=11&inheritFilters=false&lang=ru&page={page}&sort=popular&spp=30&supplier=859504'

                driver.get(url)
                time.sleep(5)  # Ожидание загрузки страницы

                full_text = driver.find_element(By.TAG_NAME, "body").text

                # Проверка на пустой ответ
                if not full_text or full_text.strip() == '':
                    raise ValueError(f"Пустой ответ от сервера для страницы {page}")

                # Проверка, не вернулась ли HTML страница с ошибкой
                if full_text.strip().startswith('<!DOCTYPE') or '<html' in full_text.lower():
                    raise ValueError(
                        f"Получен HTML вместо JSON. Возможно, страница {page} не существует или требуется капча")

                # Попытка парсинга JSON
                data = json.loads(full_text)

                # Если успешно - выходим из функции
                print(f"Успешно получены данные для страницы {page}")
                return data

            except JSONDecodeError as e:
                print(f"Ошибка парсинга JSON на попытке {attempt + 1}: {e}")
                print(f"Первые 500 символов ответа: {full_text[:500] if 'full_text' in locals() else 'Нет данных'}")

                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)  # Увеличиваем задержку с каждой попыткой
                    print(f"Повторная попытка через {wait_time} секунд...")
                    time.sleep(wait_time)
                else:
                    print(f"Не удалось получить JSON после {self.max_retries} попыток")
                    raise

            except (ValueError, TimeoutException, WebDriverException) as e:
                print(f"Ошибка на попытке {attempt + 1}: {e}")

                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    print(f"Повторная попытка через {wait_time} секунд...")
                    time.sleep(wait_time)
                else:
                    print(f"Критическая ошибка после {self.max_retries} попыток")
                    raise

            except Exception as e:
                print(f"Неожиданная ошибка на попытке {attempt + 1}: {e}")

                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    print(f"Повторная попытка через {wait_time} секунд...")
                    time.sleep(wait_time)
                else:
                    raise

            finally:
                # Всегда закрываем драйвер, даже при ошибке
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

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
        response = requests.get(url, auth=(login, password), timeout=(30,30))
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


import time
import random
import logging
from typing import Optional, Dict, Literal
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

logger = logging.getLogger(__name__)


class OzonAPIClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS
        self.api_key = API_KEY_OZON
        self.client_id = CLIENT_ID
        self.session = requests.Session()
        self.__strategy = None
        self._setup_session()

    def _setup_session(self):
        """Настройка сессии - убираем Retry, оставляем только ручное управление"""
        # Отключаем автоматические retry, чтобы не конфликтовали с ручными
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
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
                     retries: int = 10,
                     timeout: int = (10, 60)):

        url = f'{self.base_url[url_key]}{endpoint}'

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
                    timeout=timeout
                )

                # Специальная обработка 429 (Too Many Requests)
                if response.status_code == 429:
                    wait_time = self._get_retry_after(response) or (2 ** attempt + random.uniform(1, 3))
                    logger.warning(f'Получена 429 ошибка (попытка {attempt + 1}/{retries}). Ждем {wait_time:.1f} сек')

                    if attempt < retries - 1:
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f'Все {retries} попыток исчерпаны для 429 ошибки')
                        # Возвращаем None или пустой результат вместо падения
                        return None if not zip_needs else None

                # Обработка 500 ошибок
                if response.status_code >= 500:
                    logger.warning(f'Получена {response.status_code} ошибка (попытка {attempt + 1}/{retries})')

                    if attempt < retries - 1:
                        wait_time = min(5 * (attempt + 1), 30)
                        logger.info(f'Ждем {wait_time} секунд перед повторной попыткой...')
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error('Все попытки исчерпаны для серверной ошибки')
                        if zip_needs:
                            return None
                        return None

                response.raise_for_status()
                logger.info('Запрос выполнен успешно')

                if content_type == 'application/zip':
                    return response
                return response.json()

            except requests.exceptions.HTTPError as err:
                error_status = err.response.status_code if err.response else 'unknown'

                # 429 снова проверяем (на случай если raise_for_status выбросил)
                if err.response and err.response.status_code == 429:
                    wait_time = self._get_retry_after(err.response) or (2 ** attempt + random.uniform(1, 3))

                    if attempt < retries - 1:
                        logger.info(f"429 ошибка, повтор через {wait_time:.1f} секунд...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"429 ошибка после {retries} попыток, возвращаем None")
                        return None

                # Обработка других HTTP ошибок
                logger.error(f'HTTP ошибка {error_status}: {err}')
                if attempt < retries - 1 and err.response and err.response.status_code >= 500:
                    wait_time = min(2 ** attempt + random.uniform(0.1, 0.5), 30)
                    time.sleep(wait_time)
                    continue

                # Для 400, 401, 403, 404 и т.д. не повторяем, но и не падаем
                if err.response and 400 <= err.response.status_code < 500:
                    logger.error(f'Клиентская ошибка {error_status}, возвращаем None')
                    return None

                raise  # Неожиданная ошибка - поднимаем дальше

            except requests.exceptions.ConnectionError as err:
                logger.warning(f'Ошибка соединения (попытка {attempt + 1}/{retries}): {err}')

                if attempt < retries - 1:
                    wait_time = min(2 ** attempt + random.uniform(0.5, 1.5), 30)
                    logger.info(f"Повтор через {wait_time:.1f} секунд...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error('Все попытки соединения провалились')
                    return None

            except requests.exceptions.Timeout as err:
                logger.warning(f'Таймаут (попытка {attempt + 1}/{retries}): {err}')

                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    logger.info(f"Повтор через {wait_time} секунд...")
                    time.sleep(wait_time)
                    continue

                logger.error('Таймаут после всех попыток')
                return None

            except Exception as err:
                logger.error(f'Неожиданная ошибка: {err}')
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None

        return None

    def _get_retry_after(self, response) -> Optional[float]:
        """Извлекаем время ожидания из заголовка Retry-After"""
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                # Может быть число секунд или HTTP-дата
                return float(retry_after)
            except ValueError:
                # Если это дата, игнорируем, используем стандартную логику
                pass
        return None

    def get_data(self, **kwargs):
        """Основной метод для получения данных через стратегию"""
        if not self.__strategy:
            raise ValueError("Strategy not set")
        return self.__strategy.get_info(self, **kwargs)