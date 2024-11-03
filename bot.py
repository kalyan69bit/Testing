import logging
import json
import random
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import BadRequest

# Bot token and channel username (replace with your actual details)
BOT_TOKEN = "8044627800:AAGvCBiRHSlP6aIEr4mI284TrzL2zIYAt4I"  # Replace with your bot token
CHANNEL_USERNAME = "@megasaruku0"  # Replace with your channel username

# File to save and load user data
DATA_FILE = "users_data.json"

# Initialize bot and set up logging
bot = Bot(token=BOT_TOKEN)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined list of items (url and image pairs)
ITEMS = [
    {"url": "https://xpshort.com/XOVwc", "image": "https://ibb.co/rb0dHzC"},
    {"url": "https://xpshort.com/ZEq6U7", "image": "https://ibb.co/G9w84Sq"},
    {"url": "https://xpshort.com/4vlp43", "image": "https://ibb.co/yF1XhbY"},
    {"url": "https://xpshort.com/8YsEjd", "image": "https://ibb.co/1mrpSB3"},
    {"url": "https://xpshort.com/FoD4c", "image": "https://ibb.co/Zgx8Rtj"},
    {"url": "https://xpshort.com/BqVR4k", "image": "https://ibb.co/dtzY5F9"},
    {"url": "https://xpshort.com/fn3lp", "image": "https://ibb.co/N3c5xMy"},
    {"url": "https://xpshort.com/QyzDaX", "image": "https://ibb.co/ys7tzTn"},
    {"url": "https://xpshort.com/zkCxt5", "image": "https://ibb.co/mJXb2vs"},
    {"url": "https://xpshort.com/5IoFJ", "image": "https://ibb.co/b7yHRPV"},
]

ACCESS_DENIED_PHOTO = "https://upload.wikimedia.org/wikipedia/en/thumb/6/68/Telegram_access_denied.jpg/800px-Telegram_access_denied.jpg?20200919053248"

# Load user data from file
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save user data to file
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(users_data, file)

# Initialize user data
users_data = load_data()

# Check if the user has joined the channel
def check_channel_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

# Start command with referral tracking
def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    referrer_id = context.args[0] if context.args else None

    if user_id not in users_data:
        users_data[user_id] = {"referrals": 0, "is_vip": False}
        
        # Check if the user was referred
        if referrer_id and referrer_id != user_id and referrer_id in users_data:
            users_data[referrer_id]["referrals"] += 1
            save_data()  # Save after updating referral count

            # Grant VIP status if referrals reach 50
            if users_data[referrer_id]["referrals"] >= 50 and not users_data[referrer_id]["is_vip"]:
                users_data[referrer_id]["is_vip"] = True
                save_data()  # Save VIP status
                bot.send_message(chat_id=int(referrer_id), text="Congratulations! You've earned VIP status!")

    save_data()  # Save new user info

    # Generate and send welcome message or access denied message
    if check_channel_membership(user_id):
        referral_link = f"https://t.me/{bot.username}?start={user_id}"
        welcome_message = f"Welcome to the bot! Here are the commands you can use:\n\n" \
                          f"/gen - Get a random item\n" \
                          f"/alive - Check if the bot is running\n" \
                          f"/help - Get help\n" \
                          f"/vip - Access VIP content\n\n" \
                          f"Your referral link: {referral_link}"
        update.message.reply_text(welcome_message)
    else:
        keyboard = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        caption = "Access Denied 🚫\n\nYou must join the channel to use the bot."
        update.message.reply_photo(photo=ACCESS_DENIED_PHOTO, caption=caption, reply_markup=reply_markup)

# Command to generate random item
def gen(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if check_channel_membership(user_id):
        item = random.choice(ITEMS)
        try:
            caption = f"Enjoy mawa...❤️: [Click Here]({item['url']})"
            update.message.reply_photo(photo=item["image"], caption=caption, parse_mode='Markdown')
        except BadRequest as e:
            logger.error(f"Failed to send photo: {e}")
            update.message.reply_text("Oops! There was an issue with sending the photo. Please try again later.")
    else:
        keyboard = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        caption = "Access Denied 🚫\n\nYou must join the channel to use the bot."
        update.message.reply_photo(photo=ACCESS_DENIED_PHOTO, caption=caption, reply_markup=reply_markup)

# Alive command
def alive(update: Update, context: CallbackContext):
    update.message.reply_text("The bot is alive! 😊")

# Help command
def help_command(update: Update, context: CallbackContext):
    help_message = "Here are the commands you can use:\n\n" \
                   "/gen - Get a random item\n" \
                   "/alive - Check if the bot is running\n" \
                   "/help - Get help\n" \
                   "/vip - Access VIP content"
    update.message.reply_text(help_message)

# VIP command
def vip(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id in users_data and users_data[user_id]["is_vip"]:
        update.message.reply_text("Welcome, VIP! Enjoy your exclusive content 🔥")
    else:
        update.message.reply_text("VIP content is only available to users with VIP status. Refer 50 people to get VIP access.")

# Error handler
def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        update.message.reply_text("An error occurred. Please try again later.")

def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("gen", gen))
    dispatcher.add_handler(CommandHandler("alive", alive))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("vip", vip))

    # Register the error handler
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
