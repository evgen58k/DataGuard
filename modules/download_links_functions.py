# import the required modules
import json  # for working with JSON data

# import the file paths
from config import LINKS_PATH

# import the required Telegram modules
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler


# stages
START, END = range(2)
# callback data
APP_OPTIONS = ["OpenVPN"]
APP_LETTERS = ["O"]
OS_OPTIONS = ["Windows", "macOS", "Linux", "Android", "iOS"]
OS_LETTERS = ["Wi", "M", "L", "A", "I"]


# function to get app selection from user
async def getapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # set up the keyboard with app options and their assigned letters (callback data)
    keyboard = [
        [
            InlineKeyboardButton(option, callback_data=letter)
            for option, letter in zip(APP_OPTIONS, APP_LETTERS)
        ]
    ]

    get_app = InlineKeyboardMarkup(keyboard)
    # ask user to select an app
    await update.message.reply_text(
        "Выберите приложение VPN, которое вы хотите загрузить.:", reply_markup=get_app
    )

    return START


# function to handle OS selection from user
async def handle_os_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get CallbackQuery from Update
    query = update.callback_query
    await query.answer()

    selected_app = query.data
    context.user_data["selected_app"] = selected_app
    # set up the keyboard with OS options and their assigned letters (callback data)
    keyboard = [
        [
            InlineKeyboardButton(option, callback_data=letter)
            for option, letter in zip(OS_OPTIONS, OS_LETTERS)
        ]
    ]

    os_selection = InlineKeyboardMarkup(keyboard)
    # ask user to select an OS
    await query.edit_message_text(
        text="Выберите свою операционную систему:", reply_markup=os_selection
    )

    return END


# function to get download link based on user's selections
async def get_download_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_os = query.data
    context.user_data["selected_os"] = selected_os

    selected_app = context.user_data.get("selected_app")
    selected_os = context.user_data.get("selected_os")

    # load the download_links.json file and get the download link based on the user's app and OS selections
    with open(LINKS_PATH) as f:
        data = json.load(f)
    url = data[selected_app][selected_os]
    # display the download link to the user
    await query.edit_message_text(text=f"Вот ваша ссылка для скачивания: {url}")

    return ConversationHandler.END
