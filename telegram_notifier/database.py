import os
import sqlite3
from typing import List, Dict, Optional


class Database:
    def __init__(self, db_path: str = os.path.join(os.path.dirname(__file__), "notifications.db") ):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Только одна таблица - пользователи
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()

    def get_user_by_chat_id(self, chat_id: int) -> Optional[Dict]:
        """Получение информации о пользователе по chat_id"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT chat_id, username, first_name, last_name, created_at 
                    FROM users WHERE chat_id = ?
                ''', (chat_id,))

                row = cursor.fetchone()
                if row:
                    return {
                        'chat_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'created_at': row[4]
                    }
                return None

        except sqlite3.Error as e:
            print(f"❌ Ошибка получения пользователя: {e}")
            return None

    def get_user_display_name(self, chat_id: int) -> str:
        """Получение отображаемого имени пользователя"""
        user = self.get_user_by_chat_id(chat_id)
        if not user:
            return f"Пользователь {chat_id}"

        # Формируем имя в порядке приоритета:
        # 1. Имя + Фамилия
        # 2. Только имя
        # 3. Username
        # 4. Chat ID
        if user['first_name'] and user['last_name']:
            return f"{user['first_name']} {user['last_name']}"
        elif user['first_name']:
            return user['first_name']
        elif user['username']:
            return f"@{user['username']}"
        else:
            return f"Пользователь {chat_id}"

    def add_user(self, chat_id: int, username: str = None,
                 first_name: str = None, last_name: str = None):
        """Добавление нового пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (chat_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, username, first_name, last_name))
            conn.commit()

    def get_all_users(self) -> List[Dict]:
        """Получение списка всех пользователей"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT chat_id, username, first_name, last_name
                FROM users
            ''')

            users = []
            for row in cursor.fetchall():
                users.append({
                    'chat_id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'last_name': row[3]
                })

            return users

    def get_user_by_id(self, chat_id: int) -> Optional[Dict]:
        """Получение пользователя по определенному chat_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT chat_id, username, first_name, last_name
                FROM users
                WHERE chat_id = ?
            ''', (chat_id,))

            row = cursor.fetchone()

            if row:
                return {
                    'chat_id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'last_name': row[3]
                }
            else:
                return None

    def get_user_count(self) -> int:
        """Получение количества пользователей"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]