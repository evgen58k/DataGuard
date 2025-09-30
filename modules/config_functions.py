import subprocess
import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import OVPN_FILE_PATH
from modules.utils import send_upload_document_action
from modules.language_functions import get_language

logger = logging.getLogger(__name__)


async def generate_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ тарифов для покупки"""
    try:
        buttons = [
            [InlineKeyboardButton(text="1 Месяц - 300 рублей", callback_data="product_a")],
            [InlineKeyboardButton(text="3 Месяца - 900 рублей", callback_data="product_b")],
            [InlineKeyboardButton(text="6 Месяцев - 1500 рублей", callback_data="product_c")],
            [InlineKeyboardButton(text="1 Год - 2500 рублей", callback_data="product_d")],
        ]

        products = InlineKeyboardMarkup(buttons)
        chat_id = update.message.chat_id
        
        await context.bot.send_message(
            chat_id, 
            "🔒 **Выберите тариф**\n\nПосле оплаты вы получите конфигурационный файл для подключения.", 
            reply_markup=products, 
            parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"Error in generate_config: {e}")
        await update.message.reply_text("❌ Ошибка при загрузке тарифов. Попробуйте позже.")


async def generate_config_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Заглушка для успешной генерации конфига"""
    await update.message.reply_text("✅ Конфигурационный файл успешно создан!")


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать главное меню с кнопками"""
    try:
        menu_keyboard = [
            [KeyboardButton("❓ Помощь"), KeyboardButton("ℹ️ О сервисе")],
            [KeyboardButton("🛒 Купить доступ")],
            [KeyboardButton("📥 Скачать приложение"), KeyboardButton("🔒 Конфиденциальность")],
            [KeyboardButton("⚖️ Условия использования"), KeyboardButton("📋 Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "🤖 **DataGuard - Главное меню**\n\n"
            "🔒 Безопасное подключение к интернету\n\n"
            "Выберите действие из меню ниже:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in show_menu: {e}")
        await show_fallback_menu(update)


async def show_fallback_menu(update: Update):
    """Показать меню без клавиатуры в случае ошибки"""
    fallback_text = (
        "🤖 **DataGuard - Главное меню**\n\n"
        "Используйте команды:\n"
        "/menu - Главное меню\n"
        "/generate_config - Купить доступ\n" 
        "/getapp - Скачать приложение\n"
        "/help - Помощь"
    )
    await update.message.reply_text(fallback_text)


async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок меню"""
    try:
        text = update.message.text
        logger.info(f"Обработка кнопки меню: {text}")
        
        button_handlers = {
            "📋 Главное меню": show_menu,
            "❓ Помощь": "help_message",
            "ℹ️ О сервисе": "about", 
            "🛒 Купить доступ": generate_config,
            "📥 Скачать приложение": "getapp",
            "🔒 Конфиденциальность": "privacy",
            "⚖️ Условия использования": "terms"
        }
        
        if text in button_handlers:
            handler = button_handlers[text]
            if isinstance(handler, str):
                # Импортируем и вызываем функцию по имени
                await call_function_by_name(update, context, handler)
            else:
                await handler(update, context)
        else:
            await show_menu(update, context)
            
    except Exception as e:
        logger.error(f"Ошибка в handle_menu_buttons: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте еще раз.")


async def call_function_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE, function_name: str):
    """Вызов функции по имени"""
    try:
        if function_name == "help_message":
            from modules.info_functions import help_message
            await help_message(update, context)
        elif function_name == "about":
            from modules.info_functions import about
            await about(update, context)
        elif function_name == "getapp":
            from modules.download_links_functions import getapp
            await getapp(update, context)
        elif function_name == "privacy":
            from modules.info_functions import privacy
            await privacy(update, context)
        elif function_name == "terms":
            from modules.info_functions import terms
            await terms(update, context)
    except Exception as e:
        logger.error(f"Error calling function {function_name}: {e}")
        await update.message.reply_text("❌ Ошибка при выполнении команды.")


async def product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product selection and set duration"""
    query = update.callback_query
    await query.answer()
    
    try:
        language, language_file_path = await get_language(update, context)
        with open(language_file_path, "r", encoding='utf-8') as f:
            strings = json.load(f)

        # Map product selection to duration days
        product_durations = {
            "product_a": 30,
            "product_b": 90,
            "product_c": 180,
            "product_d": 365
        }
        
        product_names = {
            "product_a": "1 месяц",
            "product_b": "3 месяца", 
            "product_c": "6 месяцев",
            "product_d": "1 год"
        }

        choice = query.data
        chat_id = query.message.chat_id

        if choice in product_durations:
            # Store selected plan and duration in user data
            context.user_data["duration_days"] = product_durations[choice]
            context.user_data["selected_plan"] = product_names[choice]
            
            # Proceed directly to OpenVPN config generation
            await generate_openvpn_config(update, context)
        else:
            await context.bot.send_message(chat_id, "❌ Неверный выбор продукта.")
            
    except Exception as e:
        logger.error(f"Error in product_callback: {e}")
        await query.message.reply_text("❌ Ошибка при обработке выбора продукта.")


@send_upload_document_action
async def generate_openvpn_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate OpenVPN configuration file"""
    try:
        query = update.callback_query
        chat_id = query.message.chat_id
        
        # Get user data
        duration_days = context.user_data.get("duration_days")
        selected_plan = context.user_data.get("selected_plan")
        
        if not duration_days or not selected_plan:
            await context.bot.send_message(chat_id, "❌ Данные о подписке не найдены.")
            return

        await context.bot.send_message(chat_id, "⏳ Генерируем ваш конфигурационный файл DataGuard...")

        # Generate unique client name
        user_id = query.from_user.id
        client_name = f"user_{user_id}"
        
        # Generate OpenVPN configuration
        return_code = subprocess.run([
            "pivpn", "ovpn", "add", "nopass", "-n", client_name, "-d", str(duration_days)
        ]).returncode
        
        if return_code != 0:
            await context.bot.send_message(chat_id, "❌ Ошибка генерации конфигурации.")
            return

        # Send configuration file to user
        file_path = os.path.join(OVPN_FILE_PATH, f"{client_name}.ovpn")
        await send_configuration_file(context, chat_id, file_path, client_name, selected_plan)
        
        # Cleanup
        await cleanup_after_config_generation(context, chat_id, query.message.message_id, file_path)
        
    except Exception as e:
        logger.error(f"Error in generate_openvpn_config: {e}")
        await context.bot.send_message(chat_id, "❌ Ошибка при создании конфигурационного файла.")


async def send_configuration_file(context, chat_id, file_path, client_name, selected_plan):
    """Send configuration file to user"""
    try:
        with open(file_path, "rb") as f:
            await context.bot.send_document(
                chat_id, 
                document=f, 
                filename=f"{client_name}.ovpn",
                caption=f"🔑 **Ваш конфигурационный файл**\n\nСрок действия: {selected_plan}"
            )
        
        # Send confirmation message
        duration_message = f"✅ Ваша подписка DataGuard активна в течение {selected_plan}."
        await context.bot.send_message(chat_id, duration_message)
        
    except FileNotFoundError:
        await context.bot.send_message(chat_id, "❌ Файл конфигурации не найден.")
    except Exception as e:
        logger.error(f"Error sending config file: {e}")
        await context.bot.send_message(chat_id, f"❌ Ошибка при отправке файла: {str(e)}")


async def cleanup_after_config_generation(context, chat_id, message_id, file_path):
    """Cleanup after config generation"""
    # Clean up user data
    context.user_data.pop("selected_plan", None)
    context.user_data.pop("duration_days", None)
    
    # Delete original product selection message
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
    
    # Clean up configuration file
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"Error deleting config file: {e}")
