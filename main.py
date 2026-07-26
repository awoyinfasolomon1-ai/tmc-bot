import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

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
    logger.error("❌ Missing bot tokens! Please set all 4 environment variables.")
    exit(1)

# ============================================================
# ENTRY BOT (@TMCStartBot)
# ============================================================
async def entry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="entry_earn")],
        [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="entry_advertise")],
        [InlineKeyboardButton("📖 LEARN MORE", callback_data="entry_learn")],
        [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
    ]
    await update.message.reply_text(
        "🚀 WELCOME TO TMC 🔥\n\nTMC - Telegram Monetization Coin\nPowering Digital Value. Rewarding Connections.\n\n💰 Earn from your Telegram channels, groups, and bots!\n📢 Advertise to thousands of engaged users!\n\nChoose your path:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def entry_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "entry_earn":
        keyboard = [[InlineKeyboardButton("🚀 GO TO EARN BOT", url="https://t.me/TMCTelegraMonetizationBot")]]
        await query.edit_message_text(
            "💰 EARN WITH TMC\n\nTurn your Telegram assets into cash!\n\n✅ Link your channels/groups/bots\n✅ Earn from views, clicks, and joins\n✅ Withdraw anytime\n\nGo to @TMCTelegraMonetizationBot to start earning!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_advertise":
        keyboard = [[InlineKeyboardButton("🚀 GO TO ADS BOT", url="https://t.me/tmcadvertiserbot")]]
        await query.edit_message_text(
            "📢 ADVERTISE WITH TMC\n\nReach thousands of engaged users!\n\n✅ Create view/click/join campaigns\n✅ Reach active channels, groups, and bots\n✅ Track performance\n\nGo to @tmcadvertiserbot to create your campaign!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_learn":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="entry_back")]]
        await query.edit_message_text(
            "📖 ABOUT TMC\n\nTMC is a Telegram monetization platform that connects:\n→ Channel/Group/Bot owners who want to earn\n→ Advertisers who want to reach audiences\n\n💰 1 TMC = ₦100\n💳 Deposit: ₦500 minimum\n💸 Withdraw: Any amount (10% fee)",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_help":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="entry_back")]]
        await query.edit_message_text(
            "❓ HELP\n\n📌 I want to earn: Go to @TMCTelegraMonetizationBot\n📌 I want to advertise: Go to @tmcadvertiserbot\n📌 I have a referral link: Click it and choose your path\n📌 Contact @TMCAdminBot for support",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_back":
        keyboard = [
            [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="entry_earn")],
            [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="entry_advertise")],
            [InlineKeyboardButton("📖 LEARN MORE", callback_data="entry_learn")],
            [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
        ]
        await query.edit_message_text(
            "🚀 WELCOME TO TMC 🔥\n\nTMC - Telegram Monetization Coin\n\nChoose your path:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ============================================================
# MAIN BOT (@TMCTelegraMonetizationBot)
# ============================================================
async def main_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="main_balance")],
        [InlineKeyboardButton("📢 Link", callback_data="main_link")],
        [InlineKeyboardButton("💰 Deposit", callback_data="main_deposit")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="main_withdraw")],
        [InlineKeyboardButton("👥 Referrals", callback_data="main_referrals")]
    ]
    await update.message.reply_text(
        "👋 Welcome to TMC Earnings!\n\n💰 Balance: 0 TMC (₦0)\nStatus: 🔰 Unverified\n\n👇 Tap a button:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_balance":
        await query.edit_message_text("💰 Your balance: 0 TMC (₦0)")
    elif data == "main_link":
        await query.edit_message_text(
            "📢 Link Your Asset\n\n/link @channel\n/linkgroup @group\n/linkbot @bot\n\nCost: ₦500 (5 TMC) per asset"
        )
    elif data == "main_deposit":
        await query.edit_message_text(
            "💰 Deposit TMC Coins\n\n🏦 Bank: PalmPay\n📋 Account: 896-2925-124\n📝 Name: NEXUS EARN LIMITED (TAIWO)\n\n1 TMC = ₦100"
        )
    elif data == "main_withdraw":
        await query.edit_message_text("💸 Withdraw TMC Coins\n\n/withdraw [amount]\n\n10% fee on top")
    elif data == "main_referrals":
        await query.edit_message_text(
            "👥 Referral Program\n\nShare your link and earn ₦50!\n\nhttps://t.me/TMCStartBot?start=ref_YOURID"
        )

# ============================================================
# ADVERTISER BOT (@tmcadvertiserbot)
# ============================================================
async def advert_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Wallet", callback_data="advert_wallet")],
        [InlineKeyboardButton("📢 Create Campaign", callback_data="advert_create")],
        [InlineKeyboardButton("📊 My Campaigns", callback_data="advert_campaigns")]
    ]
    await update.message.reply_text(
        "📢 Welcome to TMC Ads!\n\nReach thousands of engaged users!\n\n👇 Tap a button:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def advert_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "advert_wallet":
        await query.edit_message_text("💰 Your wallet: 0 TMC (₦0)")
    elif data == "advert_create":
        await query.edit_message_text(
            "📢 Create Campaign\n\nUse /create views\nOr /create clicks\nOr /create joins"
        )
    elif data == "advert_campaigns":
        await query.edit_message_text("📊 You have no active campaigns.")

# ============================================================
# ADMIN BOT (@Dytr44fgh5dxyy5rgbot)
# ============================================================
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Deposits", callback_data="admin_deposits")],
        [InlineKeyboardButton("📋 Withdrawals", callback_data="admin_withdrawals")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")]
    ]
    await update.message.reply_text(
        "🔐 TMC Admin Panel\n\nWelcome, Admin!\n\n👇 Tap a button:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin_deposits":
        await query.edit_message_text("📋 No pending deposits.")
    elif data == "admin_withdrawals":
        await query.edit_message_text("📋 No pending withdrawals.")
    elif data == "admin_users":
        await query.edit_message_text("👥 Total users: 0")
    elif data == "admin_stats":
        await query.edit_message_text("📊 TMC Stats\n\nTotal Revenue: ₦0\nActive Channels: 0\nActive Campaigns: 0")

# ============================================================
# RUN ALL BOTS (FIXED)
# ============================================================
async def run_bot(token, handlers):
    """Run a single bot using Application.run_polling()"""
    app = Application.builder().token(token).build()
    for handler in handlers:
        app.add_handler(handler)
    logger.info(f"✅ Starting bot with token: {token[:10]}...")
    # run_polling is async and blocks until stopped
    await app.run_polling()

async def main():
    logger.info("🚀 Starting all 4 TMC bots...")

    # Create tasks for each bot
    tasks = [
        run_bot(ENTRY_BOT_TOKEN, [
            CommandHandler("start", entry_start),
            CallbackQueryHandler(entry_callback, pattern="^entry_")
        ]),
        run_bot(MAIN_BOT_TOKEN, [
            CommandHandler("start", main_start),
            CallbackQueryHandler(main_callback, pattern="^main_")
        ]),
        run_bot(ADVERTISER_BOT_TOKEN, [
            CommandHandler("start", advert_start),
            CallbackQueryHandler(advert_callback, pattern="^advert_")
        ]),
        run_bot(ADMIN_BOT_TOKEN, [
            CommandHandler("start", admin_start),
            CallbackQueryHandler(admin_callback, pattern="^admin_")
        ])
    ]

    # Run all bots concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
