import logging
import random
import re
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Literal, Optional, Union

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.util.retry import Retry

from config import API_KEYS_WB, BASE_URLS, CLUB_PROCENT, DELAY_INTERVAL, HEADERS, PARAMS, RETRY_TIMES, API_KEY_OZON, \
    CLIENT_ID
from logging_config import setup_logging
from strategies.request_strategies import RequestStrategy

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
                                            timeout=60)
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
    """
    Парсер карточек WB через Selenium.
    Запускает N браузеров параллельно (BROWSER_COUNT), каждый обходит свою часть артикулов.
    Аналог OzonPriceParser — браузер выполняет JS, страница полностью рендерится.
    """
    BROWSER_COUNT = 10  # сколько браузеров запускать параллельно
    DELAY_MIN = 2.0  # задержка между карточками внутри одного браузера
    DELAY_MAX = 4.0
    DELAY_ON_BLOCK = 60.0  # пауза если браузер поймал блокировку
    PAGE_LOAD_TIMEOUT = 20  # сколько ждём загрузки карточки (сек)
    CARD_URL = 'https://www.wildberries.ru/catalog/{nm_id}/detail.aspx'

    def __init__(self):
        self.__strategy = None

    # ------------------------------------------------------------------ #
    # Создание браузера
    # ------------------------------------------------------------------ #
    @staticmethod
    def _make_driver() -> webdriver.Chrome:
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        # НЕ headless — ВБ его детектирует и не рендерит React
        return webdriver.Chrome(options=options)

    # ------------------------------------------------------------------ #
    # Прогрев одного браузера (заходим на главную чтобы получить куки)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _warmup(driver: webdriver.Chrome) -> None:
        driver.get('https://www.wildberries.ru')
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'header'))
            )
        except Exception:
            pass
        time.sleep(random.uniform(2, 4))

    # ------------------------------------------------------------------ #
    # Парсинг одной карточки через браузер
    # ------------------------------------------------------------------ #
    def _fetch_card_selenium(self, driver: webdriver.Chrome, nm_id: int) -> dict | None:
        url = self.CARD_URL.format(nm_id=nm_id)
        for attempt in range(3):
            try:
                driver.get(url)

                # Ждём пока React отрендерит карточку.
                # Признак рендера — появление data-testid на корневом div карточки
                # или любого элемента с классом priceBlock.
                # Используем JS-поллинг — надёжнее чем WebDriverWait на классы с суффиксами.
                rendered = False
                for _ in range(self.PAGE_LOAD_TIMEOUT):
                    try:
                        found = driver.execute_script("""
                            return !!(
                                document.querySelector('[data-testid]') &&
                                document.querySelector('[class*="priceBlock"]')
                            )
                        """)
                        if found:
                            rendered = True
                            break
                    except Exception:
                        pass
                    time.sleep(1)

                if not rendered:
                    logger.debug(f'Артикул {nm_id}: страница не отрендерилась, попытка {attempt + 1}/3')
                    if attempt < 2:
                        time.sleep(self.DELAY_ON_BLOCK)
                        continue
                    return None

                html = driver.page_source
                return self._parse_card(nm_id, html)

            except Exception as e:
                logger.warning(f'Артикул {nm_id}: {e}, попытка {attempt + 1}/3')
                time.sleep(5 * (attempt + 1))
        return None

    # ------------------------------------------------------------------ #
    # Воркер — один браузер обходит свой список артикулов
    # ------------------------------------------------------------------ #
    def _worker(self, nm_ids: list[int], worker_id: int) -> list[dict]:
        results = []
        driver = self._make_driver()
        try:
            logger.info(f'Браузер {worker_id}: старт, {len(nm_ids)} артикулов')
            self._warmup(driver)

            for i, nm_id in enumerate(nm_ids):
                result = self._fetch_card_selenium(driver, nm_id)
                if result:
                    results.append(result)

                if (i + 1) % 10 == 0:
                    logger.info(f'Браузер {worker_id}: обработано {i + 1}/{len(nm_ids)}')

                time.sleep(random.uniform(self.DELAY_MIN, self.DELAY_MAX))

        except Exception as e:
            logger.error(f'Браузер {worker_id}: критическая ошибка — {e}')
        finally:
            driver.quit()
            logger.info(f'Браузер {worker_id}: завершён, получено {len(results)} карточек')

        return results

    # ------------------------------------------------------------------ #
    # Публичный интерфейс
    # ------------------------------------------------------------------ #
    def make_request(self, nm_ids: list[int], **kwargs) -> list[dict]:
        total = len(nm_ids)
        logger.info(f'Запуск парсинга {total} артикулов, браузеров: {self.BROWSER_COUNT}')

        # Делим артикулы поровну между браузерами
        chunk_size = -(-total // self.BROWSER_COUNT)  # ceil division
        chunks = [nm_ids[i:i + chunk_size] for i in range(0, total, chunk_size)]

        results = []
        with ThreadPoolExecutor(max_workers=self.BROWSER_COUNT) as executor:
            futures = {
                executor.submit(self._worker, chunk, i + 1): i
                for i, chunk in enumerate(chunks)
            }
            for future in as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception as e:
                    logger.error(f'Воркер завершился с ошибкой: {e}')

        logger.info(f'Итого получено карточек: {len(results)} из {total}')
        return results

    @staticmethod
    def _parse_card(nm_id: int, html: str) -> dict | None:
        soup = BeautifulSoup(html, 'html.parser')
        # --- Цена ---
        # В HTML два места с ценой:
        #   <ins class="... priceBlockFinalPrice--iToZR">20&nbsp;510&nbsp;₽</ins>  (основной блок)
        #   <span class="... priceBlockFinalPrice--aBPT6">20&nbsp;510&nbsp;₽</span> (блок заказа внизу)
        # Паттерн priceBlock.*Price ловит оба варианта
        price_tag = soup.find('ins', class_=re.compile(r'priceBlock.*Price'))
        if not price_tag:
            price_tag = soup.find('span', class_=re.compile(r'priceBlock.*Price'))
        if not price_tag:
            logger.debug(f'Артикул {nm_id}: блок цены не найден')
            return None
        price_text = price_tag.get_text(separator='', strip=True)
        price_clean = re.sub(r'[^\d]', '', price_text)
        if not price_clean:
            return None
        price_kopecks = int(price_clean) * 100  # конвертер делит на 100

        # --- Название ---
        # В HTML: <h2 class="... productTitle--lfc4o">Ботильоны натуральная кожа</h2>
        # Ищем без указания тега — ВБ может поменять h1/h2
        name_tag = soup.find(class_=re.compile(r'productTitle'))
        name = name_tag.get_text(strip=True) if name_tag else ''

        # # --- Бренд ---
        # # Если у товара есть бренд — он в brandBadgeText
        # # Если нет — берём первый sellerAndBrandItemName (продавец/бренд в одном блоке)
        # brand = ''
        # brand_tag = soup.find('span', class_=re.compile(r'brandBadgeText'))
        # if brand_tag:
        #     brand = brand_tag.get_text(strip=True)

        # --- Категория ---
        # Хлебные крошки находятся в блоке с классом breadcrumbs--...
        # Ссылки вида /catalog/<slug> — последняя из них и есть категория.
        # Избегаем ссылок из меню — их в HTML очень много, они идут ДО блока крошек.
        entity = ''
        breadcrumb_block = soup.find(class_=re.compile(r'^breadcrumbs--', re.I))
        if breadcrumb_block:
            links = breadcrumb_block.find_all('a', href=re.compile(r'/catalog/'))
            if links:
                entity = links[-1].get_text(strip=True)

        logger.debug(f'Артикул {nm_id}: цена={price_kopecks // 100}, '
                     f'категория={entity!r}, название={name[:30]!r}')
        return {
            'id': nm_id,
            'entity': entity,
            'name': name,
            'sizes': [{'price': {'product': price_kopecks}}],
        }

    def set_strategy(self, strategy: RequestStrategy):
        self.__strategy = strategy

    def get_data(self, **kwargs) -> list[dict]:
        if self.__strategy is None:
            raise ValueError('Стратегия не выбрана, установите стратегию с помощью set_strategy')
        return self.__strategy.get_info(self, **kwargs)


class MedClient(Client):
    def __init__(self):
        self.base_url = BASE_URLS
        self.__strategy = None

    def make_request(self, url_key: Literal['med_prices', 'med_collections_1', 'med_collections_2', 'med_purchase'],
                     login: str = None,
                     password: str = None, ):
        url = f'{self.base_url[url_key]}'
        logger.info(f'Выполнение запроса по адресу {url}')
        response = requests.get(url, auth=(login, password), timeout=(30, 30))
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