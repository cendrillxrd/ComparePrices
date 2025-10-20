import os
import tempfile

import requests
import logging
from typing import List, Dict
from telegram_notifier.database import Database
from telegram_notifier.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token or config.BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.db = Database()

        # Проверяем валидность токена
        self._check_bot_token()

    def _check_bot_token(self):
        """Проверка валидности токена бота"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            data = response.json()

            if data.get("ok"):
                bot_info = data["result"]
                logger.info(f"🤖 Бот инициализирован: {bot_info['first_name']} (@{bot_info['username']})")
                return True
            else:
                logger.error("❌ Неверный токен бота")
                return False

        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Telegram API: {e}")
            return False

    def get_user_display_name(self, chat_id: int) -> str:
        """Получение отображаемого имени пользователя"""
        return self.db.get_user_display_name(chat_id)

    def _send_csv_file(self, chat_id: int, csv_data: str, filename: str, caption: str = None) -> bool:
        """Отправка CSV файла"""
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(csv_data)
                temp_file_path = temp_file.name

            # Отправка файла через Telegram API
            with open(temp_file_path, 'rb') as file:
                url = f"{self.base_url}/sendDocument"
                files = {'document': (filename, file)}
                data = {'chat_id': chat_id,
                        'parse_mode': 'HTML'}
                if caption:
                    data['caption'] = caption

                response = requests.post(url, files=files, data=data, timeout=30)
                success = response.json().get("ok", False)

            # Удаляем временный файл
            os.unlink(temp_file_path)

            if success:
                logger.info(f"✅ CSV файл отправлен пользователю {self.db.get_user_display_name(chat_id)}")
            else:
                logger.warning(f"⚠️ Не удалось отправить CSV пользователю {self.db.get_user_display_name(chat_id)}")

            return success

        except Exception as e:
            logger.error(f"❌ Ошибка отправки CSV: {e}")
            # Убедимся, что временный файл удален даже при ошибке
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return False

    def register_user(self, chat_id: int, username: str = None,
                      first_name: str = None, last_name: str = None) -> bool:
        """Регистрация нового пользователя"""
        try:
            self.db.add_user(chat_id, username, first_name, last_name)
            logger.info(f"✅ Зарегистрирован пользователь: {first_name} (ID: {chat_id})")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка регистрации пользователя: {e}")
            return False

    def send_to_user(self, chat_id: int, message: str = None,
                     parse_mode: str = "HTML", csv_data: str = None,
                     csv_filename: str = "data.csv") -> bool:
        """Отправка сообщения и/или CSV файла конкретному пользователю"""
        try:
            if csv_data:
                # Отправка файла
                return self._send_csv_file(chat_id, csv_data, csv_filename, message)
            else:
                # Отправка только текста
                return self._send_text_message(chat_id, message, parse_mode)

        except Exception as e:
            logger.error(f"❌ Ошибка отправки пользователю {chat_id}: {e}")
            return False

    def _send_text_message(self, chat_id: int, message: str, parse_mode: str) -> bool:
        """Отправка текстового сообщения"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }

        response = requests.post(url, json=payload, timeout=10)
        success = response.json().get("ok", False)

        if success:
            logger.info(f"✅ CSV файл отправлен пользователю {self.db.get_user_display_name(chat_id)}")
        else:
            logger.warning(f"⚠️ Не удалось отправить CSV пользователю {self.db.get_user_display_name(chat_id)}")
        return response.json().get("ok", False)

    def broadcast_message(self, message: str = None, parse_mode: str = "HTML",
                          csv_data: str = None, csv_filename: str = "data.csv") -> Dict:
        """Массовая рассылка всем пользователям (сообщение и/или CSV файл)"""
        all_users = self.db.get_all_users()
        total = len(all_users)
        successful = 0

        logger.info(f"📢 Рассылка для {total} пользователей...")

        for user in all_users:
            if self.send_to_user(
                    chat_id=user['chat_id'],
                    message=message,
                    parse_mode=parse_mode,
                    csv_data=csv_data,
                    csv_filename=csv_filename
            ):
                successful += 1

        stats = {
            'total': total,
            'successful': successful,
            'failed': total - successful,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }

        logger.info(f"📊 Результат: {successful}/{total}")
        return stats

    def admin_message(self, message: str = None, parse_mode: str = "HTML",
                          csv_data: str = None, csv_filename: str = "data.csv"):
        """Массовая рассылка всем пользователям (сообщение и/или CSV файл)"""
        admin = self.db.get_user_by_id(config.ADMIN_IDS[0])

        logger.info(f"📢 Рассылка для {admin['first_name']} пользователей...")


        self.send_to_user(
                chat_id=admin['chat_id'],
                message=message,
                parse_mode=parse_mode,
                csv_data=csv_data,
                csv_filename=csv_filename
        )

    def get_user_stats(self) -> Dict:
        """Получение статистики пользователей"""
        count = self.db.get_user_count()
        return {
            'total_users': count
        }
    @staticmethod
    def format_notification(title: str, message: str) -> str:
        """Форматирование уведомления"""
        return f"""
📢 <b>{title}</b>

{message}

        """.strip()