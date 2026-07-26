import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# BOT TOKENS (From Environment Variables)
# ============================================================
MAIN_BOT_TOKEN = os.environ.get("MAIN_BOT_TOKEN")
ADVERTISER_BOT_TOKEN = os.environ.get("ADVERTISER_BOT_TOKEN")
ADMIN_BOT_TOKEN = os.environ.get("ADMIN_BOT_TOKEN")
ENTRY_BOT_TOKEN = os.environ.get("ENTRY_BOT_TOKEN")

if not all([MAIN_BOT_TOKEN, ADVERTISER_BOT_TOKEN, ADMIN_BOT_TOKEN, ENTRY_BOT_TOKEN]):
    logger.error("❌ Missing bot tokens! Set all 4 environment variables.")
    exit(1)

# ============================================================
# ENTRY BOT (@TMCStartBot)
# ============================================================
async def entry_start(update, context):
    keyboard = [
        [InlineKeyboardButton("💰 EARN", callback_data="earn")],
        [InlineKeyboardButton("📢 ADVERTISE", callback_data="advertise")]
    ]
    await update.message.reply_text(
        "🚀 WELCOME TO TMC 🔥\n\nChoose your path:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def entry_callback(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "earn":
        await query.edit_message_text("👉 Go to @TMCTelegraMonetizationBot to start earning!")
    elif query.data == "advertise":
        await query.edit_message_text("👉 Go to @tmcadvertiserbot to advertise!")

# ============================================================
# MAIN BOT (@TMCTelegraMonetizationBot)
# ============================================================
async def main_start(update, context):
    await update.message.reply_text(
        "👋 Welcome to TMC Earn!\n\nUse /balance, /deposit, /withdraw, /link"
    )

# ============================================================
# ADVERTISER BOT (@tmcadvertiserbot)
# ============================================================
async def advert_start(update, context):
    await update.message.reply_text(
        "📢 Welcome to TMC Ads!\n\nUse /create to start a campaign."
    )

# ============================================================
# ADMIN BOT (@Dytr44fgh5dxyy5rgbot)
# ============================================================
async def admin_start(update, context):
    await update.message.reply_text(
        "🔐 Admin Panel\n\nUse /deposits, /approve, /withdrawals"
    )

# ============================================================
# RUN ALL BOTS
# ============================================================
async def run_bot(token, handlers):
    app = Application.builder().token(token).build()
    for handler in handlers:
        app.add_handler(handler)
    logger.info(f"✅ Starting bot...")
    await app.run_polling()

async def main():
    logger.info("🚀 Starting TMC bots...")
    
    tasks = [
        run_bot(ENTRY_BOT_TOKEN, [
            CommandHandler("start", entry_start),
            CallbackQueryHandler(entry_callback)
        ]),
        run_bot(MAIN_BOT_TOKEN, [
            CommandHandler("start", main_start)
        ]),
        run_bot(ADVERTISER_BOT_TOKEN, [
            CommandHandler("start", advert_start)
        ]),
        run_bot(ADMIN_BOT_TOKEN, [
            CommandHandler("start", admin_start)
        ])
    ]
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
