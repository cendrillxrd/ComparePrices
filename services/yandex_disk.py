import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from yadisk import YaDisk
from yadisk.exceptions import PathNotFoundError, ParentNotFoundError

from config import YANDEX_FILE_NAME, YANDEX_DIR_NAME, YANDEX_API, MAIN_DIR_PRICES, MAIN_DIR


class YandexDiskManager:
    def __init__(self, folder_name: str = YANDEX_DIR_NAME):
        """
        Инициализация менеджера Яндекс.Диска

        Args:
            token (str): OAuth-токен Яндекс.Диска
            folder_name (str): название папки для работы (по умолчанию "my_app_folder")
        """
        self.disk = YaDisk(token=YANDEX_API)
        self.folder_name = f"/{folder_name}"
        self._create_folder_if_not_exists()

    def _create_folder_if_not_exists(self):
        """Создает папку на Яндекс.Диске, если она не существует"""
        try:
            if not self.disk.exists(self.folder_name):
                self.disk.mkdir(self.folder_name)
                print(f"Папка {self.folder_name} создана на Яндекс.Диске")
            else:
                print(f"Папка {self.folder_name} уже существует")
        except Exception as e:
            print(f"Ошибка при создании папки: {e}")

    def get_file_from_folder(self, filename: str = YANDEX_FILE_NAME, local_path: str = MAIN_DIR_PRICES):
        """
        Загружает файл из папки на Яндекс.Диске

        Args:
            filename (str): имя файла в папке на Яндекс.Диске
            local_path (str): локальный путь для сохранения (по умолчанию текущая директория)

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            remote_path = f"{self.folder_name}/{filename}"

            if not self.disk.exists(remote_path):
                print(f"Файл {filename} не найден в папке {self.folder_name}")
                return False

            if local_path is None:
                local_path = filename

            self.disk.download(remote_path, local_path)
            print(f"Файл {filename} успешно загружен в {local_path}")
            return True

        except Exception as e:
            print(f"Ошибка при загрузке файла {filename}: {e}")
            return False

    def save_file_to_folder(self, local_path: str = MAIN_DIR_PRICES, filename: str = YANDEX_FILE_NAME):
        """
        Сохраняет файл в папку на Яндекс.Диске

        Args:
            local_path (str): локальный путь к файлу
            filename (str): имя файла на Яндекс.Диске (по умолчанию берется из local_path)

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            if not os.path.exists(local_path):
                print(f"Локальный файл {local_path} не существует")
                return False

            if filename is None:
                filename = os.path.basename(local_path)

            remote_path = f"{self.folder_name}/{filename}"

            self.disk.upload(local_path, remote_path, overwrite=True)
            print(f"Файл {local_path} успешно сохранен в {remote_path}")
            return True

        except Exception as e:
            print(f"Ошибка при сохранении файла {local_path}: {e}")
            return False

    def is_file_older_than_12_hours(self, filename: str = YANDEX_FILE_NAME) -> bool:
        """
        Проверяет, является ли файл старше 12 часов

        Args:
            filename (str): имя файла в папке на Яндекс.Диске

        Returns:
            bool: True если файл старше 12 часов или не существует, False если младше
        """
        try:
            remote_path = f"{self.folder_name}/{filename}"

            if not self.disk.exists(remote_path):
                print(f"Файл {filename} не найден")
                return True

            # Получаем информацию о файле
            file_info = self.disk.get_meta(remote_path)
            modified_time = file_info.modified

            # Преобразуем время модификации в datetime
            if isinstance(modified_time, str):
                modified_time = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))

            # Конвертируем в московское время
            moscow_tz = ZoneInfo("Europe/Moscow")
            modified_time_moscow = modified_time.astimezone(moscow_tz)

            # Получаем текущее время в московском часовом поясе
            current_time_moscow = datetime.now(moscow_tz)
            # Вычисляем разницу во времени
            time_difference = current_time_moscow - modified_time_moscow
            twelve_hours = timedelta(hours=12)

            is_older = time_difference > twelve_hours

            if is_older:
                print(
                    f"Файл {filename} старше 12 часов (последнее изменение: {modified_time_moscow.strftime('%d.%m.%Y %H:%M:%S %Z')})")
                return True
            else:
                print(
                    f"Файл {filename} младше 12 часов (последнее изменение: {modified_time_moscow.strftime('%d.%m.%Y %H:%M:%S %Z')})")
                return False

        except Exception as e:
            print(f"Ошибка при проверке возраста файла {filename}: {e}")
            return True

# Создание экземпляра менеджера

# disk_manager = YandexDiskManager()
# Сохранение файла на Яндекс.Диск
# disk_manager.save_file_to_folder()
#
# # Проверка возраста файла
# disk_manager.is_file_older_than_12_hours()
#
# # Загрузка файла с Яндекс.Диска
# disk_manager.get_file_from_folder()
