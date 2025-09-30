# import the Telegram API token from config.py
from config import TELEGRAM_API_TOKEN

# import the required Telegram modules
from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ApplicationBuilder,
    ConversationHandler,
    ContextTypes
)
from telegram import ReplyKeyboardMarkup, KeyboardButton

# Импортируем конкретные функции из модулей
from modules.config_functions import (
    generate_config, 
    generate_config_success,
    show_menu, 
    handle_menu_buttons,
    product_callback
)
from modules.info_functions import (
    start, help_message, about, status, limitations,
    privacy, tutorial, terms, support, whatsnew
)
from modules.download_links_functions import getapp, handle_os_selection, get_download_link
from modules.utils import cancel, send_typing_action
from modules.payment_handlers import select_product, check_payment

# enable logging
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Константы для ConversationHandler
START, END = range(2)
APP_LETTERS = ["A", "B", "C", "D"]
OS_LETTERS = ["A", "B", "C", "D", "E"]


@send_typing_action
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text("Sorry, I didn't understand that command.")


async def post_init(application):
    """Функция инициализации после запуска бота"""
    logger.info("Bot is starting...")
    # Можно добавить дополнительную инициализацию здесь


async def post_stop(application):
    """Функция очистки при остановке бота"""
    logger.info("Bot is stopping...")
    # Можно добавить cleanup операции здесь


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    try:
        # Отправляем сообщение пользователю об ошибке
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")


def setup_handlers(application):
    """Настройка всех обработчиков бота"""
    
    # Глобальный обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Основные команды
    command_handlers = [
        ("start", start),
        ("help", help_message),
        ("about", about),
        ("status", status),
        ("limitations", limitations),
        ("privacy", privacy),
        ("tutorial", tutorial),
        ("terms", terms),
        ("support", support),
        ("whatsnew", whatsnew),
        ("generate_config", generate_config),
        ("generate_config_success", generate_config_success),
        ("menu", show_menu),
        ("cancel", cancel),
    ]
    
    for command, handler in command_handlers:
        application.add_handler(CommandHandler(command, handler))
    
    # Обработчики для Юкассы
    application.add_handler(
        CallbackQueryHandler(select_product, pattern="^(product_a|product_b|product_c|product_d)$")
    )
    application.add_handler(
        CallbackQueryHandler(check_payment, pattern="^check_")
    )
    
    # Обработчик выбора продукта для генерации конфига
    application.add_handler(
        CallbackQueryHandler(product_callback, pattern="^(product_a|product_b|product_c|product_d)$")
    )
    
    # ConversationHandler для скачивания приложений
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("getapp", getapp)],
        states={
            START: [
                CallbackQueryHandler(handle_os_selection, pattern=f"^{letter}$")
                for letter in APP_LETTERS
            ],
            END: [
                CallbackQueryHandler(get_download_link, pattern=f"^{letter}$")
                for letter in OS_LETTERS
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        per_message=False,
    )
    application.add_handler(conv_handler)
    
    # Обработчик кнопок меню
    application.add_handler(MessageHandler(
        filters.Text([
            "📋 Главное меню", "❓ Помощь", "🛒 Купить доступ", 
            "📥 Скачать приложение", "🔒 Конфиденциальность", 
            "⚖️ Условия использования", "ℹ️ О сервисе"
        ]), 
        handle_menu_buttons
    ))
    
    # Обработчик неизвестных команд
    application.add_handler(MessageHandler(filters.ALL, unknown))


def main():
    """Основная функция запуска бота"""
    try:
        # Инициализация приложения с увеличенными таймаутами
        application = (
            ApplicationBuilder()
            .token(TELEGRAM_API_TOKEN)
            .read_timeout(30)
            .write_timeout(30)
            .connect_timeout(30)
            .pool_timeout(30)
            .post_init(post_init)
            .post_stop(post_stop)
            .build()
        )
        
        # Настройка обработчиков
        setup_handlers(application)
        
        # Запуск бота
        logger.info("Starting bot polling...")
        application.run_polling(
            poll_interval=1.0,
            timeout=30,
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()
