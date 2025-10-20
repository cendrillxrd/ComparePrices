from telegram_notifier import TelegramNotifier


def send_notification_to_all(title: str = None, message: str = None,
                             csv_data: str = None, csv_filename: str = "data.csv"):
    """
    Универсальная функция для отправки уведомлений всем пользователям

    Аргументы:
    - title: Заголовок уведомления
    - message: Текст сообщения
    - csv_data: CSV данные в виде строки
    - csv_filename: Имя файла для CSV
    """
    notifier = TelegramNotifier()

    # Форматируем сообщение если есть заголовок
    formatted_message = None
    if title and message:
        formatted_message = notifier.format_notification(title, message)
    elif message:
        formatted_message = message
    elif title:
        formatted_message = title

    # Отправляем рассылку
    stats = notifier.broadcast_message(
        message=formatted_message,
        csv_data=csv_data,
        csv_filename=csv_filename
    )

    print(f"📨 Отправлено {stats['successful']} из {stats['total']} пользователей")
    return stats

def send_notification_to_admin(title: str = None, message: str = None,
                             csv_data: str = None, csv_filename: str = "data.csv"):
    """
    Универсальная функция для отправки уведомлений всем пользователям

    Аргументы:
    - title: Заголовок уведомления
    - message: Текст сообщения
    - csv_data: CSV данные в виде строки
    - csv_filename: Имя файла для CSV
    """
    notifier = TelegramNotifier()

    # Форматируем сообщение если есть заголовок
    formatted_message = None
    if title and message:
        formatted_message = notifier.format_notification(title, message)
    elif message:
        formatted_message = message
    elif title:
        formatted_message = title

    # Отправляем рассылку
    notifier.admin_message(
        message=formatted_message,
        csv_data=csv_data,
        csv_filename=csv_filename
    )
