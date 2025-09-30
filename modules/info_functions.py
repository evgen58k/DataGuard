# import the required modules
import subprocess  # for running shell commands
import datetime  # for getting the current date/time
from modules.utils import *
from modules.language_functions import *


#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    """Обработчик команды /start с показом меню"""
#    await smooth_streaming_message(update, context, "start_message", ".")
#    await show_menu(update, context)  # Показываем меню после приветствия
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с показом меню"""
    try:
        # Показываем приветственное сообщение
        await smooth_streaming_message(update, context, "start_message", ".")
        
        # Показываем меню после приветствия
        from modules.config_functions import show_menu
        await show_menu(update, context)
        
    except Exception as e:
        print(f"Error in start: {e}")
        # Fallback - просто показываем меню
        from modules.config_functions import show_menu
        await show_menu(update, context)





# call the smooth_streaming_message function for the /start command
#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    await smooth_streaming_message(update, context, "start_message", ".")

#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    """Обработчик команды /start с показом меню"""
    # Ваш существующий код для плавной отправки сообщения
#    await smooth_streaming_message(update, context, "start_message", ".")
    
    # Показываем меню после приветствия
#    await show_menu(update, context)









# send a typing indicator in the chat
@send_typing_action
# define a function to handle the /status command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # use subprocess to run the "systemctl status openvpn" command
    output = subprocess.check_output(["systemctl", "status", "openvpn"])

    # extract the relevant line from the output
    active_line = [line for line in output.decode().split("\n") if "Active:" in line][0]

    # send the extracted line back to the user
    await update.message.reply_text(active_line)


# call the smooth_streaming_message function for the /about command
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await smooth_streaming_message(update, context, "about_message", ".")


# call the smooth_streaming_message function for the /limitations command
async def limitations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await smooth_streaming_message(update, context, "limitations_message", "• ")


# call the smooth_streaming_message function for the /privacy command
async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await smooth_streaming_message(update, context, "privacy_message", "• ")


# call the smooth_streaming_message function for the /help command
async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await smooth_streaming_message(update, context, "help_message", "/")


# call the smooth_streaming_message function for the /terms command
async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await smooth_streaming_message(update, context, "terms_message", "•")


# call the smooth_streaming_message function for the /support command
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await smooth_streaming_message(update, context, "support_message", ".")


# call the smooth_streaming_message function for the /tutorial command
async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await smooth_streaming_message(update, context, "tutorial_message", ". ")


# define a global variable to store the last update date
last_update_date = None


# send a typing indicator in the chat
@send_typing_action
# define a function to handle the /whatsnew command
async def whatsnew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language, language_file_path = await get_language(update, context)

    # load text based on language preference
    with open(language_file_path, "r") as f:
        strings = json.load(f)

    global last_update_date

    # set the current date as the latest update date
    latest_update_date = datetime.date.today()

    # check if there is a last update date recorded
    if last_update_date:
        # check if there are any updates made after the last update date
        if latest_update_date > last_update_date:
            # send a message with latest updates and improvements
            await update.message.reply_text(
                f"New updates and improvements since {last_update_date}:\n"
                "• Added support for French, German, Russian, and Spanish languages based on user's Telegram language "
                "preference\n"
            )
        else:
            # send a message indicating that there are no new updates
            await update.message.reply_text(
                "No new updates since the last time you checked."
            )
    else:
        # send a message with all updates and improvements
        all_updates = strings["all_updates"]
        await update.message.reply_text(all_updates)

    # update the last update date
    last_update_date = latest_update_date
