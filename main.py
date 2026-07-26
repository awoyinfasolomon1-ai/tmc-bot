import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# BOT TOKENS
# ============================================================
MAIN_BOT_TOKEN = "8718104402:AAFiR3525kfUljhfhw6G6zra-7eQ6kTeOg"
ADVERTISER_BOT_TOKEN = "8320654823:AAETjVGr-pTexuxAeInT2TdSHFnUVYlH9aI"
ADMIN_BOT_TOKEN = "8335073103:AAGR4GUgYl_yh9l3AymEwx0sPwuJV7xW6MM"
ENTRY_BOT_TOKEN = "8501142592:AAFep9TneyIhAPRh4LNsLI_-gR8kBqU0xqA"

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
        await query.edit_message_text("👉 Go to @TMCTelegraMonetizationBot to earn!")
    elif query.data == "advertise":
        await query.edit_message_text("👉 Go to @tmcadvertiserbot to advertise!")

# ============================================================
# MAIN BOT
# ============================================================
async def main_start(update, context):
    await update.message.reply_text("👋 Welcome to TMC Earn!\n\nUse /balance, /deposit, /withdraw, /link")

# ============================================================
# ADVERTISER BOT
# ============================================================
async def advert_start(update, context):
    await update.message.reply_text("📢 Welcome to TMC Ads!\n\nUse /create to start a campaign.")

# ============================================================
# ADMIN BOT
# ============================================================
async def admin_start(update, context):
    await update.message.reply_text("🔐 Admin Panel\n\nUse /deposits, /approve, /withdrawals")

# ============================================================
# RUN BOTS
# ============================================================
async def run_bot(token, handlers):
    app = Application.builder().token(token).build()
    for handler in handlers:
        app.add_handler(handler)
    logger.info(f"✅ Bot started: {token[:10]}...")
    await app.run_polling()

async def main():
    logger.info("🚀 Starting all 4 TMC bots...")
    
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
