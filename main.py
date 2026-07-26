import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# BOT TOKEN (ONE BOT ONLY - TEST)
# ============================================================
BOT_TOKEN = "8501142592:AAFep9TneyIhAPRh4LNsLI_-gR8kBqU0xqA"

# ============================================================
# COMMANDS
# ============================================================
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="earn")],
        [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="advertise")]
    ]
    update.message.reply_text(
        "🚀 WELCOME TO TMC 🔥\n\nTMC - Telegram Monetization Coin\n\nChoose your path:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def callback(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "earn":
        query.edit_message_text("👉 Go to @TMCTelegraMonetizationBot to earn!")
    elif query.data == "advertise":
        query.edit_message_text("👉 Go to @tmcadvertiserbot to advertise!")

# ============================================================
# MAIN
# ============================================================
def main():
    logger.info("🚀 Starting TMC Bot...")
    
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(callback))
    
    updater.start_polling()
    logger.info("✅ TMC Bot is running!")
    updater.idle()

if __name__ == "__main__":
    main()
