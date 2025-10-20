import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram_notifier import TelegramNotifier, config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Инициализация notifier
notifier = TelegramNotifier(config.BOT_TOKEN)


async def start(update: Update, context: CallbackContext):
    """Обработчик команды /start - просто регистрирует пользователя"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Регистрируем пользователя
    notifier.register_user(
        chat_id=chat_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    welcome_text = f"""
👋 Привет, {user.first_name}!

Теперь ты будешь получать уведомления от нашего бота.

Для остановки уведомлений просто заблокируй бота.
    """

    await update.message.reply_text(welcome_text, parse_mode='HTML')


async def stats(update: Update, context: CallbackContext):
    """Показать статистику (только для админов)"""
    chat_id = update.effective_chat.id

    # Проверяем права админа
    if chat_id not in config.ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет прав для этой команды")
        return

    stats = notifier.get_user_stats()

    await update.message.reply_text(
        f"📊 <b>Статистика бота:</b>\n\n"
        f"👥 Всего пользователей: {stats['total_users']}",
        parse_mode='HTML'
    )


async def broadcast(update: Update, context: CallbackContext):
    """Команда рассылки (только для админов)"""
    chat_id = update.effective_chat.id

    # Проверяем права админа
    if chat_id not in config.ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет прав для этой команды")
        return

    # Получаем сообщение для рассылки
    if not context.args:
        await update.message.reply_text("❌ Использование: /broadcast <сообщение>")
        return

    message = " ".join(context.args)
    formatted_message = notifier.format_notification("Уведомление", message)

    # Отправляем рассылку
    stats = notifier.broadcast_message(formatted_message)

    # Отчет админу
    await update.message.reply_text(
        f"📊 <b>Результаты рассылки:</b>\n\n"
        f"👥 Всего пользователей: {stats['total']}\n"
        f"✅ Успешно отправлено: {stats['successful']}\n"
        f"❌ Не удалось отправить: {stats['failed']}\n"
        f"📈 Процент успеха: {stats['success_rate']:.1f}%",
        parse_mode='HTML'
    )


def main():
    """Запуск бота"""
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Только три обработчика
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("broadcast", broadcast))

    print("🤖 Бот запущен...")
    print("📝 Пользователи регистрируются командой /start")
    print("📢 Рассылка: /broadcast <сообщение>")
    print("📊 Статистика: /stats")

    application.run_polling()


if __name__ == "__main__":
    main()