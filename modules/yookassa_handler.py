# modules/yookassa_handler.py
import asyncio
import uuid
import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import TARIFFS

logger = logging.getLogger(__name__)

class YookassaManager:
    def __init__(self):
        self.pending_payments = {}
    
    async def create_payment_link(self, product_id, user_id, chat_id):
        """Создает ссылку для оплаты через Юкассу"""
        try:
            if product_id not in TARIFFS:
                return None, "Неверный продукт"
            
            tariff = TARIFFS[product_id]
            payment_id = str(uuid.uuid4())
            
            # TODO: Реальная интеграция с Юкассой
            # Пока используем заглушку
            payment_url = f"https://yookassa.ru/demo/payment?amount={tariff['price']}"
            
            # Сохраняем информацию о платеже
            self.pending_payments[payment_id] = {
                'user_id': user_id,
                'chat_id': chat_id,
                'product_id': product_id,
                'tariff': tariff,
                'status': 'pending'
            }
            
            return payment_url, payment_id
            
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            return None, str(e)
    
    async def check_payment_status(self, payment_id):
        """Проверяет статус платежа (заглушка)"""
        # TODO: Реальная проверка статуса в Юкассе
        # Пока имитируем успешный платеж
        if payment_id in self.pending_payments:
            return "succeeded"
        return "not_found"
    
    async def process_successful_payment(self, payment_id, context):
        """Обрабатывает успешный платеж"""
        try:
            if payment_id not in self.pending_payments:
                return False
            
            payment_info = self.pending_payments[payment_id]
            user_data = context.user_data
            
            # Сохраняем данные о тарифе
            user_data["selected_plan"] = payment_info['tariff']['name']
            user_data["duration_days"] = payment_info['tariff']['days']
            user_data["product_id"] = payment_info['product_id']
            
            # Уведомляем пользователя
            await context.bot.send_message(
                payment_info['chat_id'],
                f"✅ **Оплата прошла успешно!**\n\n"
                f"Тариф: {payment_info['tariff']['name']}\n"
                f"Сумма: {payment_info['tariff']['price']} руб.\n\n"
                f"Генерирую конфигурационный файл OpenVPN...",
                parse_mode='Markdown'
            )
            
            # Сразу генерируем OpenVPN конфиг
            await self.generate_openvpn_config(payment_info['chat_id'], context, user_data)
            
            # Удаляем из ожидающих
            del self.pending_payments[payment_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return False
    
    async def generate_openvpn_config(self, chat_id, context, user_data):
        """Генерирует конфигурационный файл OpenVPN"""
        try:
            from modules.config_functions import openvpn_callback
            
            # Создаем mock update объект для вызова openvpn_callback
            class MockUpdate:
                def __init__(self, chat_id):
                    self.effective_chat = type('Chat', (), {'id': chat_id})()
            
            # Вызываем функцию генерации OpenVPN конфига
            await openvpn_callback(MockUpdate(chat_id), context)
            
        except Exception as e:
            logger.error(f"Error generating OpenVPN config: {e}")
            await context.bot.send_message(
                chat_id,
                "❌ Ошибка при генерации конфигурационного файла. "
                "Пожалуйста, обратитесь в поддержку.",
                parse_mode='Markdown'
            )

# Глобальный экземпляр
yookassa = YookassaManager()
