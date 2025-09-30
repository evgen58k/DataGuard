# import the required modules
import asyncio  # for asynchronous programming
import json  # for working with JSON data
from functools import wraps  # for using function decorators
from modules.language_functions import *

# import the required Telegram modules
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError
import logging

logger = logging.getLogger(__name__)

# define the send_action decorator
def send_action(action, delay=1):
    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            try:
                await context.bot.send_chat_action(
                    chat_id=update.effective_message.chat_id, action=action
                )
                await asyncio.sleep(delay)
                return await func(update, context, *args, **kwargs)
            except (TimedOut, NetworkError) as e:
                logger.warning(f"Network error in send_action: {e}")
                # Продолжаем выполнение функции даже при ошибке отправки действия
                return await func(update, context, *args, **kwargs)
        return command_func
    return decorator


# set the aliases with custom delays
send_upload_document_action = send_action(ChatAction.UPLOAD_DOCUMENT)
send_typing_action = send_action(ChatAction.TYPING, delay=0.5)  # уменьшенная задержка
send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)


def split_message(text, max_length=4000):
    """Разделяет длинное сообщение на части"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
        else:
            # Ищем последний перенос строки в пределах лимита
            split_pos = text.rfind('\n', 0, max_length)
            if split_pos == -1:
                # Если переносов нет, делим по границе слова
                split_pos = text.rfind(' ', 0, max_length)
            if split_pos == -1:
                # Если и слов нет, просто обрезаем
                split_pos = max_length
            
            parts.append(text[:split_pos])
            text = text[split_pos:].lstrip()
    
    return parts


# define a function to display a message with streaming text
@send_typing_action
async def smooth_streaming_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message_key: str, delimiter: str
):
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            # get the user's language preference
            language, language_file_path = await get_language(update, context)

            # load text based on language preference
            with open(language_file_path, "r", encoding='utf-8') as f:
                strings = json.load(f)

            # split the message into sentences using the custom delimiter
            full_text = strings[message_key]
            
            # Если текст очень длинный, отправляем без анимации
            if len(full_text) > 2000:
                messages = split_message(full_text)
                for msg_part in messages:
                    await update.message.reply_text(msg_part)
                return

            sentences = full_text.split(delimiter)

            # send the first sentence as a new message
            text = sentences[0].strip()
            if not text:  # Если первое предложение пустое, пропускаем
                if len(sentences) > 1:
                    text = sentences[1].strip()
                    sentences = sentences[1:]
                else:
                    await update.message.reply_text(full_text)
                    return
            
            bot_message = await update.message.reply_text(text)

            # loop through each sentence and gradually build up the message
            for sentence in sentences[1:]:
                text += delimiter + sentence
                try:
                    await bot_message.edit_text(text)
                    await asyncio.sleep(0.1)  # увеличенная задержка
                except (TimedOut, NetworkError):
                    # При ошибке редактирования продолжаем без прерывания
                    continue
            
            break  # Успешно завершили, выходим из цикла повторных попыток
            
        except (TimedOut, NetworkError) as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)  # ждем перед повторной попыткой
                continue
            else:
                # Все попытки failed, отправляем простым сообщением
                try:
                    language, language_file_path = await get_language(update, context)
                    with open(language_file_path, "r", encoding='utf-8') as f:
                        strings = json.load(f)
                    
                    full_text = strings[message_key]
                    messages = split_message(full_text)
                    for msg_part in messages:
                        await update.message.reply_text(msg_part)
                except Exception as final_error:
                    logger.error(f"Final attempt failed: {final_error}")
                    await update.message.reply_text("⚠️ Произошла ошибка при загрузке сообщения. Пожалуйста, попробуйте позже.")
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            await update.message.reply_text("❌ Ошибка загрузки текста. Пожалуйста, сообщите администратору.")
            break
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await update.message.reply_text("❌ Непредвиденная ошибка. Пожалуйста, попробуйте позже.")
            break
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.E
