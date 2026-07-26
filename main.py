import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# ENTRY BOT ONLY
# ============================================================
ENTRY_BOT_TOKEN = "8501142592:AAFep9TneyIhAPRh4LNsLI_-gR8kBqU0xqA"

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="entry_earn")],
        [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="entry_advertise")],
        [InlineKeyboardButton("📖 LEARN MORE", callback_data="entry_learn")],
        [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
    ]
    update.message.reply_text(
        "🚀 WELCOME TO TMC 🔥\n\nTMC - Telegram Monetization Coin\n\nChoose your path:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == "entry_earn":
        keyboard = [[InlineKeyboardButton("🚀 GO TO EARN BOT", url="https://t.me/TMCTelegraMonetizationBot")]]
        query.edit_message_text("💰 EARN WITH TMC\n\n👉 Go to @TMCTelegraMonetizationBot to start earning!", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "entry_advertise":
        keyboard = [[InlineKeyboardButton("🚀 GO TO ADS BOT", url="https://t.me/tmcadvertiserbot")]]
        query.edit_message_text("📢 ADVERTISE WITH TMC\n\n👉 Go to @tmcadvertiserbot to create your campaign!", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "entry_learn":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="entry_back")]]
        query.edit_message_text("📖 ABOUT TMC\n\n1 TMC = ₦100\nDeposit: ₦500 min", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "entry_help":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="entry_back")]]
        query.edit_message_text("❓ HELP\n\nContact @TMCAdminBot", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "entry_back":
        keyboard = [
            [InlineKeyboardButton("💰 EARN", callback_data="entry_earn")],
            [InlineKeyboardButton("📢 ADVERTISE", callback_data="entry_advertise")],
            [InlineKeyboardButton("📖 LEARN", callback_data="entry_learn")],
            [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
        ]
        query.edit_message_text("🚀 WELCOME TO TMC 🔥\n\nChoose your path:", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    logger.info("🚀 Starting TMC Entry Bot...")
    updater = Updater(ENTRY_BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(callback))
    updater.start_polling()
    logger.info("✅ Entry Bot is running!")
    updater.idle()

if __name__ == "__main__":
    main()
