import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# BOT TOKENS (HARDCODED)
# ============================================================
ENTRY_BOT_TOKEN = "8501142592:AAFep9TneyIhAPRh4LNsLI_-gR8kBqU0xqA"
MAIN_BOT_TOKEN = "8718104402:AAFiYR3525kfUljhfhw6G6zra-7eQ6kTeOg"
ADVERTISER_BOT_TOKEN = "8320654823:AAETjVGr-pTexuxAeInT2TdSHFnUVYlH9aI"
ADMIN_BOT_TOKEN = "8335073103:AAGR4GUgYl_yh9l3AymEwx0sPwuJV7xW6MM"

ADMIN_IDS = ['8966823502', '6894471315']

# ============================================================
# ENTRY BOT (@TMCStartBot)
# ============================================================
def entry_start(update, context):
    keyboard = [
        [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="entry_earn")],
        [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="entry_advertise")],
        [InlineKeyboardButton("📖 LEARN MORE", callback_data="entry_learn")],
        [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
    ]
    update.message.reply_text(
        "🚀 WELCOME TO TMC 🔥\n\nTMC - Telegram Monetization Coin\nPowering Digital Value. Rewarding Connections.\n\n💰 Earn from your Telegram channels, groups, and bots!\n📢 Advertise to thousands of engaged users!\n\nChoose your path:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def entry_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == "entry_earn":
        keyboard = [[InlineKeyboardButton("🚀 GO TO EARN BOT", url="https://t.me/TMCTelegraMonetizationBot")]]
        query.edit_message_text(
            "💰 EARN WITH TMC\n\nTurn your Telegram assets into cash!\n\n✅ Link your channels/groups/bots\n✅ Earn from views, clicks, and joins\n✅ Withdraw anytime\n\nGo to @TMCTelegraMonetizationBot to start earning!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_advertise":
        keyboard = [[InlineKeyboardButton("🚀 GO TO ADS BOT", url="https://t.me/tmcadvertiserbot")]]
        query.edit_message_text(
            "📢 ADVERTISE WITH TMC\n\nReach thousands of engaged users!\n\n✅ Create view/click/join campaigns\n✅ Reach active channels, groups, and bots\n✅ Track performance\n\nGo to @tmcadvertiserbot to create your campaign!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_learn":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="entry_back")]]
        query.edit_message_text(
            "📖 ABOUT TMC\n\nTMC is a Telegram monetization platform that connects:\n→ Channel/Group/Bot owners who want to earn\n→ Advertisers who want to reach audiences\n\n💰 1 TMC = ₦100\n💳 Deposit: ₦500 minimum\n💸 Withdraw: Any amount (10% fee)"
        )
    elif data == "entry_help":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="entry_back")]]
        query.edit_message_text(
            "❓ HELP\n\n📌 I want to earn: Go to @TMCTelegraMonetizationBot\n📌 I want to advertise: Go to @tmcadvertiserbot\n📌 I have a referral link: Click it and choose your path\n📌 Contact @TMCAdminBot for support"
        )
    elif data == "entry_back":
        keyboard = [
            [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="entry_earn")],
            [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="entry_advertise")],
            [InlineKeyboardButton("📖 LEARN MORE", callback_data="entry_learn")],
            [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
        ]
        query.edit_message_text(
            "🚀 WELCOME TO TMC 🔥\n\nTMC - Telegram Monetization Coin\n\nChoose your path:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ============================================================
# MAIN BOT (@TMCTelegraMonetizationBot)
# ============================================================
def main_start(update, context):
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="main_balance")],
        [InlineKeyboardButton("📢 Link", callback_data="main_link")],
        [InlineKeyboardButton("💰 Deposit", callback_data="main_deposit")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="main_withdraw")],
        [InlineKeyboardButton("👥 Referrals", callback_data="main_referrals")]
    ]
    update.message.reply_text(
        "👋 Welcome to TMC Earnings!\n\n💰 Balance: 0 TMC (₦0)\nStatus: 🔰 Unverified\n\n👇 Tap a button:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == "main_balance":
        query.edit_message_text("💰 Your balance: 0 TMC (₦0)")
    elif data == "main_link":
        query.edit_message_text(
            "📢 Link Your Asset\n\n/link @channel\n/linkgroup @group\n/linkbot @bot\n\nCost: ₦500 (5 TMC) per asset"
        )
    elif data == "main_deposit":
        query.edit_message_text(
            "💰 Deposit TMC Coins\n\n🏦 Bank: PalmPay\n📋 Account: 896-2925-124\n📝 Name: NEXUS EARN LIMITED (TAIWO)\n\n1 TMC = ₦100"
        )
    elif data == "main_withdraw":
        query.edit_message_text("💸 Withdraw TMC Coins\n\n/withdraw [amount]\n\n10% fee on top")
    elif data == "main_referrals":
        query.edit_message_text(
            "👥 Referral Program\n\nShare your link and earn ₦50!\n\nhttps://t.me/TMCStartBot?start=ref_YOURID"
        )

# ============================================================
# ADVERTISER BOT (@tmcadvertiserbot)
# ============================================================
def advert_start(update, context):
    keyboard = [
        [InlineKeyboardButton("💰 Wallet", callback_data="advert_wallet")],
        [InlineKeyboardButton("📢 Create Campaign", callback_data="advert_create")],
        [InlineKeyboardButton("📊 My Campaigns", callback_data="advert_campaigns")]
    ]
    update.message.reply_text(
        "📢 Welcome to TMC Ads!\n\nReach thousands of engaged users!\n\n👇 Tap a button:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def advert_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == "advert_wallet":
        query.edit_message_text("💰 Your wallet: 0 TMC (₦0)")
    elif data == "advert_create":
        query.edit_message_text(
            "📢 Create Campaign\n\nUse /create views\nOr /create clicks\nOr /create joins"
        )
    elif data == "advert_campaigns":
        query.edit_message_text("📊 You have no active campaigns.")

# ============================================================
# ADMIN BOT (@Dytr44fgh5dxyy5rgbot)
# ============================================================
def admin_start(update, context):
    user = update.effective_user
    uid = str(user.id)

    if uid not in ADMIN_IDS:
        update.message.reply_text("🔒 Access Denied!")
        return

    keyboard = [
        [InlineKeyboardButton("📋 Deposits", callback_data="admin_deposits")],
        [InlineKeyboardButton("📋 Withdrawals", callback_data="admin_withdrawals")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")]
    ]
    update.message.reply_text(
        "🔐 TMC Admin Panel\n\nWelcome, Admin!\n\n👇 Tap a button:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def admin_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == "admin_deposits":
        query.edit_message_text("📋 No pending deposits.")
    elif data == "admin_withdrawals":
        query.edit_message_text("📋 No pending withdrawals.")
    elif data == "admin_users":
        query.edit_message_text("👥 Total users: 0")
    elif data == "admin_stats":
        query.edit_message_text("📊 TMC Stats\n\nTotal Revenue: ₦0\nActive Channels: 0\nActive Campaigns: 0")

# ============================================================
# RUN ALL BOTS
# ============================================================
def run_bot(token, handlers):
    updater = Updater(token)
    dp = updater.dispatcher
    for handler in handlers:
        dp.add_handler(handler)
    logger.info(f"✅ Bot started: {token[:10]}...")
    updater.start_polling()
    return updater

def main():
    logger.info("🚀 Starting ALL 4 TMC Bots...")

    # ENTRY BOT
    run_bot(ENTRY_BOT_TOKEN, [
        CommandHandler("start", entry_start),
        CallbackQueryHandler(entry_callback)
    ])

    # MAIN BOT
    run_bot(MAIN_BOT_TOKEN, [
        CommandHandler("start", main_start),
        CallbackQueryHandler(main_callback)
    ])

    # ADVERTISER BOT
    run_bot(ADVERTISER_BOT_TOKEN, [
        CommandHandler("start", advert_start),
        CallbackQueryHandler(advert_callback)
    ])

    # ADMIN BOT
    run_bot(ADMIN_BOT_TOKEN, [
        CommandHandler("start", admin_start),
        CallbackQueryHandler(admin_callback)
    ])

    logger.info("✅ ALL 4 TMC Bots are running!")

    # Keep running
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
