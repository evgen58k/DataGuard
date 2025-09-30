# modules/payment_handlers.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from modules.yookassa_handler import yookassa
from config import TARIFFS

async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора тарифа"""
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    product_id = query.data
    
    if product_id not in TARIFFS:
        await query.answer("Неверный продукт")
        return
    
    tariff = TARIFFS[product_id]
    
    # Создаем платежную ссылку
    payment_url, payment_id = await yookassa.create_payment_link(
        product_id, user_id, chat_id
    )
    
    if payment_url:
        # Сохраняем payment_id для проверки
        context.user_data["current_payment_id"] = payment_id
        
        # Показываем кнопки для оплаты
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить через Юкассу", url=payment_url)],
            [InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"check_{payment_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"💳 **Оплата тарифа**\n\n"
            f"📦 Тариф: {tariff['name']}\n"
            f"💰 Сумма: {tariff['price']} руб.\n"
            f"⏱️ Срок: {tariff['description']}\n"
            f"🔒 Технология: OpenVPN\n\n"
            f"1. Нажмите 'Оплатить через Юкассу'\n"
            f"2. После оплаты нажмите 'Проверить оплату'",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        await query.answer()
    else:
        await query.answer("Ошибка создания платежа", show_alert=True)

async def check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка статуса платежа"""
    query = update.callback_query
    
    if query.data.startswith("check_"):
        payment_id = query.data.replace("check_", "")
        
        status = await yookassa.check_payment_status(payment_id)
        
        if status == "succeeded":
            await yookassa.process_successful_payment(payment_id, context)
            await query.answer("✅ Оплата подтверждена!")
            await query.message.delete()
        elif status == "pending":
            await query.answer("⏳ Платеж обрабатывается...")
        else:
            await query.answer("❌ Платеж не найден")
    else:
        await query.answer("Неизвестная команда")
