import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# ONE BOT ONLY - @TMCStartBot
# ============================================================
BOT_TOKEN = "8501142592:AAFep9TneyIhAPRh4LNsLI_-gR8kBqU0xqA"

async def start(update: Update, context):
    await update.message.reply_text("🚀 Hello! TMC Bot is LIVE and WORKING! 🎉")

async def main():
    logger.info("🚀 Starting TMC Bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
