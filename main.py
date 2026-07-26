import os
import logging
import time
import json
import random
import string
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import firebase_admin
from firebase_admin import credentials, db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# BOT TOKENS (From Environment Variables)
# ============================================================
ENTRY_BOT_TOKEN = os.environ.get("ENTRY_BOT_TOKEN", "8501142592:AAFep9TneyIhAPRh4LNsLI_-gR8kBqU0xqA")
MAIN_BOT_TOKEN = os.environ.get("MAIN_BOT_TOKEN", "8718104402:AAFiYR3525kfUljhfhw6G6zra-7eQ6kTeOg")
ADVERTISER_BOT_TOKEN = os.environ.get("ADVERTISER_BOT_TOKEN", "8320654823:AAETjVGr-pTexuxAeInT2TdSHFnUVYlH9aI")
ADMIN_BOT_TOKEN = os.environ.get("ADMIN_BOT_TOKEN", "8335073103:AAGR4GUgYl_yh9l3AymEwx0sPwuJV7xW6MM")
ADMIN_IDS = ['8966823502', '6894471315']

# ============================================================
# FIREBASE CREDENTIALS (HARDCODED - VALID KEY)
# ============================================================
FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "tmc-monetization",
    "private_key_id": "204096c8719ca80e4a3858a1f7376917bdf9b6ca",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDGW4C7X92IXmjI\n5t+h1+2mHUKgauAF0Uu/OXTqM+4oSGCd67xrATZJfddWL0+pn0SqL6/Nt99g0mrt\nNiGygvJAWzPMKmF39KinwCv/cT+Q4mkCVaYLhUpvWu8010DAduRz9LX46KBnXM6n\nh+CsJRsIzeg2GvfiquTH3Gh3hm+qUJVp91PdzLoqE2cjw0+WWOzk8iXdJ1ZtqJNm\n8rs/zq0qUXqCZtuNNKE2rMd+ThJ7QIGayRHJFcIA+gZOK3u2GAr7boG4lh0pbJMl\n48hLYwE1dJt6pRSfYtAqCpmgcH8PBvdghpAcDXZGWCH53d4EctM79lrbz+0+GSeC\nO+m8F2KHAgMBAAECggEAASQflAtqHp/QvE4E/ZyAdCbjde9PyKeBAMBR4x/pUJxz\na+uNy+AxcwRsnQJp/MSPnKn8udMkeH6K1cWspjuXN2GadJ7i1b0/emqdLoDMD8I2\n9qLGV4Fik5Pwry/0yHdOT5WpTzcqvd174BAsTvhBW2ERyYlBa8YZoI2YTzePMRgL\n5tVMrmZ4EC5wnsPd+RT9fVtsLbQN0kg0XAxYm5igoVsHrJc51Wo5Xe42y6GnyheF\nGfwUmDitp+ZX6PmULMNXlhmWZqkfvWsAsaACzgAup476U7EcygPus69+ktnGac2Q\n0xbbkFhh7APxemUy1bny5k3zB1dbTNjJePWc07VYnQKBgQD19xbCsJZo+pz2niLT\nZTZtp/P8jGOEBqNSjR9W9YcWmExRMG1iqriDUtRN7pg65npbThZR2ltqk6u2D8Om\nFW5tVuP4qtpP1AKhkmp0VIlTWlJtZwVq/9F7fnttvjrXmCfFNBXD/06sUICtJgZF\nreC2teJOAeSHMO2pBvReaQ64pQKBgQDOczBQTeEO8qKIh0BoGcZSBl1xYanr1z48\nE1j4GGOna9wTITU/ywUSVkILCse2iR2qL+umswVHYGDKFhf2eg5f1oG/kpJQcu90\numsru1nPtfu7FjDVhdGRHe8dsFnQw1Q2Fow/XYS3FdU/SCUlAwzU2iIxGmh/kPXv\nLdr625LauwKBgQDYqy/Gkw38LgAFEyp0c60tjYzVRMoJLFvExYH89U5prgFUZ8eD\n6gWd0WIpwGsjP5I7Sh9JPYPX73uMZnifnjNnZ+psS/0B4y3qLHNQRIOwBFml++F+\n7xkWo0WRV8i30FYAVrBxtj4UdtnTLTLLQK855CEVPH+WQ5ink/PCEuOf7QKBgQCr\nvRr10rNj8efPV2P2tWpLFcxp42qtLDMzWozqZa+QuKMsrrVTShn/9Q2fjeoxKMMq\nrg6Eb+v2QnCB6/snKMYIZ7MroExi7BnSqrk4efPuXF76dS1OkrGQ3KvrsKYmijbl\nf8BPfgZHH7xzlhqAPZdRAdzrqCJB7F8KBsVhZYM2vQKBgQCaVmSJm1SkoCk7JFhP\nEs+LZ+3JrTh/6qbTrRcvPIy38jZoY6jqHKoOrChglJj9Fm+OgwVrakHUbU5sKNx+\nWAHVurODtpYfMSDkXCA3PHY6ZR3R97yHXST9a7UlC8fvcDn19nt2kUbSxtZC4iXD\nc9vjpc56mQ/o3M1LO0jWrXKxgg==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@tmc-monetization.iam.gserviceaccount.com",
    "client_id": "117730776419641959543",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40tmc-monetization.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

cred_obj = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred_obj, {
    'databaseURL': 'https://tmc-monetization-default-rtdb.europe-west1.firebasedatabase.app'
})
ref = db.reference('/')

logger.info("✅ Firebase connected!")

# ============================================================
# RATES & CONFIG
# ============================================================
TMC_TO_NAIRA = 100
WITHDRAWAL_FEE = 0.10
MIN_WITHDRAW_RECEIVE = 100
PALMPAY_ACCOUNT = "896-2925-124"
PALMPAY_NAME = "NEXUS EARN LIMITED (TAIWO)"

# ============================================================
# FIREBASE HELPERS
# ============================================================
def get_user(uid):
    try:
        return ref.child(f'users/{uid}').get()
    except:
        return None

def create_user(uid, username):
    try:
        user_data = {
            'uid': uid,
            'username': username,
            'balance': 0,
            'status': 'active',
            'verified': False,
            'joined': datetime.now().isoformat(),
            'channels': {},
            'groups': {},
            'bots': {},
            'referrals': 0,
            'referral_earnings': 0
        }
        ref.child(f'users/{uid}').set(user_data)
        return True
    except:
        return False

def get_user_balance(uid):
    user = get_user(uid)
    return user.get('balance', 0) if user else 0

def is_admin(uid):
    return uid in ADMIN_IDS

def is_banned(uid):
    user = get_user(uid)
    return user and user.get('status') == 'banned'

def generate_narration():
    chars = string.ascii_uppercase + string.digits
    return 'TMC-' + ''.join(random.choices(chars, k=8))

# ============================================================
# ENTRY BOT (@TMCStartBot)
# ============================================================
def entry_start(update, context):
    user = update.effective_user
    uid = str(user.id)
    username = user.username or user.first_name

    if not get_user(uid):
        create_user(uid, username)

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
            "💰 EARN WITH TMC\n\nTurn your Telegram assets into cash!\n\n✅ Link your channels/groups/bots\n✅ Earn from views, clicks, and joins\n✅ Withdraw anytime\n\n👉 Go to @TMCTelegraMonetizationBot to start earning!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_advertise":
        keyboard = [[InlineKeyboardButton("🚀 GO TO ADS BOT", url="https://t.me/tmcadvertiserbot")]]
        query.edit_message_text(
            "📢 ADVERTISE WITH TMC\n\nReach thousands of engaged users!\n\n✅ Create view/click/join campaigns\n✅ Reach active channels, groups, and bots\n✅ Track performance\n\n👉 Go to @tmcadvertiserbot to create your campaign!",
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
    user = update.effective_user
    uid = str(user.id)
    username = user.username or user.first_name

    if is_banned(uid):
        update.message.reply_text("🚫 You are BANNED from TMC!")
        return

    if not get_user(uid):
        create_user(uid, username)

    user_data = get_user(uid) or {}
    balance = user_data.get('balance', 0)
    verified = user_data.get('verified', False)
    channels = len(user_data.get('channels', {}))
    groups = len(user_data.get('groups', {}))
    bots = len(user_data.get('bots', {}))

    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="main_balance")],
        [InlineKeyboardButton("📢 Link Channel/Group/Bot", callback_data="main_link")],
        [InlineKeyboardButton("💰 Deposit", callback_data="main_deposit")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="main_withdraw")],
        [InlineKeyboardButton("👥 Referrals", callback_data="main_referrals")],
        [InlineKeyboardButton("📊 History", callback_data="main_history")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")]
    ]

    status = "✅ Verified" if verified else "🔰 Unverified"
    msg = (
        f"👋 Welcome to TMC Earnings, @{username}!\n\n"
        f"💰 Balance: {balance} TMC (₦{balance * TMC_TO_NAIRA})\n"
        f"📊 Status: {status}\n"
        f"📢 Channels: {channels}\n"
        f"👥 Groups: {groups}\n"
        f"🤖 Bots: {bots}\n\n"
        f"👇 Tap a button below"
    )
    update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

def main_callback(update, context):
    query = update.callback_query
    query.answer()
    user = update.effective_user
    uid = str(user.id)
    data = query.data

    if is_banned(uid):
        query.edit_message_text("🚫 You are BANNED from TMC!")
        return

    user_data = get_user(uid) or {}

    if data == "main_balance":
        balance = user_data.get('balance', 0)
        verified = user_data.get('verified', False)
        msg = (
            f"💰 Your Balance\n\n"
            f"💎 TMC Coins: {balance}\n"
            f"🇳🇬 Naira Value: ₦{balance * TMC_TO_NAIRA}\n\n"
            f"📊 Status: {'✅ Verified' if verified else '🔰 Unverified'}\n"
            f"⚡ Earnings boost: {'+20%' if verified else '0%'}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_link":
        msg = (
            "📢 Link Your Asset\n\n"
            "Choose what you want to link:\n\n"
            "1️⃣ Channel - Add @TMCTelegraMonetizationBot as admin\n"
            "2️⃣ Group - Add @TMCTelegraMonetizationBot as admin\n"
            "3️⃣ Bot - No admin needed, we DM your bot\n\n"
            "Commands:\n"
            "/link @channel\n"
            "/linkgroup @group\n"
            "/linkbot @bot\n\n"
            "Cost: ₦500 (5 TMC) per asset"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_deposit":
        narration = generate_narration()
        msg = (
            f"💰 Deposit TMC Coins\n\n"
            f"Send ₦X to:\n\n"
            f"🏦 Bank: PalmPay\n"
            f"📋 Account: {PALMPAY_ACCOUNT}\n"
            f"📝 Name: {PALMPAY_NAME}\n\n"
            f"📌 Your Narration Code: {narration}\n\n"
            f"Then use: /confirm {narration}\n\n"
            f"💱 1 TMC = ₦100"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_withdraw":
        msg = (
            "💸 Withdraw TMC Coins\n\n"
            "Minimum withdrawal: Any amount (₦100 receive)\n"
            "Fee: 10% (on top)\n\n"
            "To withdraw:\n"
            "/withdraw [amount] (in TMC)\n\n"
            "Example: /withdraw 10\n"
            f"→ You'll receive: ₦900 (10 TMC = ₦1,000 - 10% fee)\n"
            "We'll send to your bank within 24-48 hours"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_referrals":
        refs = user_data.get('referrals', 0)
        earnings = user_data.get('referral_earnings', 0)
        link = f"https://t.me/TMCStartBot?start=ref_{uid}"
        msg = (
            f"👥 Referral Program\n\n"
            f"Your Link:\n{link}\n\n"
            f"📊 Referrals: {refs}\n"
            f"💰 Earnings: ₦{earnings}\n\n"
            f"How it works:\n"
            f"→ Share your link\n"
            f"→ When they join and take action\n"
            f"→ You get ₦50 (0.5 TMC) bonus!"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_history":
        ledger = ref.child('ledger').order_by_child('uid').equal_to(uid).get()
        if not ledger:
            msg = "📊 No transaction history."
        else:
            items = list(ledger.values())[-5:][::-1]
            msg = "📊 Recent Transactions:\n\n"
            for item in items:
                amount = item.get('amount', 0)
                type_icon = "➕" if item.get('type') == 'credit' else "➖"
                msg += f"{type_icon} {item.get('title', 'Transaction')}: {amount} TMC\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_settings":
        msg = (
            "⚙️ Settings\n\n"
            "Choose ad categories you want to receive:\n\n"
            "1️⃣ Crypto\n"
            "2️⃣ Gaming\n"
            "3️⃣ Business\n"
            "4️⃣ News\n"
            "5️⃣ Memes\n"
            "6️⃣ NSFW\n"
            "7️⃣ Tech\n"
            "8️⃣ Health\n"
            "9️⃣ All\n\n"
            "Use: /settings [category]\n"
            "Example: /settings Crypto"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_back":
        user_data = get_user(uid) or {}
        balance = user_data.get('balance', 0)
        verified = user_data.get('verified', False)
        channels = len(user_data.get('channels', {}))
        groups = len(user_data.get('groups', {}))
        bots = len(user_data.get('bots', {}))
        status = "✅ Verified" if verified else "🔰 Unverified"

        keyboard = [
            [InlineKeyboardButton("💰 Balance", callback_data="main_balance")],
            [InlineKeyboardButton("📢 Link", callback_data="main_link")],
            [InlineKeyboardButton("💰 Deposit", callback_data="main_deposit")],
            [InlineKeyboardButton("💸 Withdraw", callback_data="main_withdraw")],
            [InlineKeyboardButton("👥 Referrals", callback_data="main_referrals")],
            [InlineKeyboardButton("📊 History", callback_data="main_history")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")]
        ]
        msg = (
            f"👋 Welcome back!\n\n"
            f"💰 Balance: {balance} TMC (₦{balance * TMC_TO_NAIRA})\n"
            f"📊 Status: {status}\n"
            f"📢 Channels: {channels}\n"
            f"👥 Groups: {groups}\n"
            f"🤖 Bots: {bots}\n\n"
            f"👇 Tap a button below"
        )
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# ADVERTISER BOT (@tmcadvertiserbot)
# ============================================================
def advert_start(update, context):
    user = update.effective_user
    uid = str(user.id)
    username = user.username or user.first_name

    if is_banned(uid):
        update.message.reply_text("🚫 You are BANNED from TMC!")
        return

    if not get_user(uid):
        create_user(uid, username)

    user_data = get_user(uid) or {}
    balance = user_data.get('balance', 0)

    keyboard = [
        [InlineKeyboardButton("💰 Wallet", callback_data="advert_wallet")],
        [InlineKeyboardButton("📢 Create Campaign", callback_data="advert_create")],
        [InlineKeyboardButton("📊 My Campaigns", callback_data="advert_campaigns")],
        [InlineKeyboardButton("💳 Deposit", callback_data="advert_deposit")]
    ]
    msg = (
        f"📢 Welcome to TMC Ads, @{username}!\n\n"
        f"💰 Wallet: {balance} TMC (₦{balance * TMC_TO_NAIRA})\n\n"
        f"👇 Tap a button below"
    )
    update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

def advert_callback(update, context):
    query = update.callback_query
    query.answer()
    user = update.effective_user
    uid = str(user.id)
    data = query.data

    user_data = get_user(uid) or {}

    if data == "advert_wallet":
        balance = user_data.get('balance', 0)
        msg = f"💰 Your Wallet\n\n💎 TMC Coins: {balance}\n🇳🇬 Naira Value: ₦{balance * TMC_TO_NAIRA}"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="advert_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "advert_create":
        msg = (
            "📢 Create Campaign\n\n"
            "Choose campaign type:\n\n"
            "👁️ /create views [goal] - Pay per view\n"
            "👆 /create clicks [goal] - Pay per click\n"
            "✅ /create joins [goal] - Pay per join\n\n"
            "Example: /create views 10000"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="advert_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "advert_campaigns":
        campaigns = ref.child('campaigns').order_by_child('advertiser_id').equal_to(uid).get()
        if not campaigns:
            msg = "📊 You have no campaigns."
        else:
            msg = "📊 Your Campaigns:\n\n"
            for key, val in campaigns.items():
                status = val.get('status', 'active')
                progress = val.get('progress', 0)
                goal = val.get('goal', 0)
                msg += f"🔹 {val.get('title', 'Campaign')}: {progress}/{goal} ({status})\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="advert_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "advert_deposit":
        narration = generate_narration()
        msg = (
            f"💰 Deposit TMC Coins\n\n"
            f"Send ₦X to:\n\n"
            f"🏦 Bank: PalmPay\n"
            f"📋 Account: {PALMPAY_ACCOUNT}\n"
            f"📝 Name: {PALMPAY_NAME}\n\n"
            f"📌 Your Narration Code: {narration}\n\n"
            f"Then use: /confirm {narration}\n\n"
            f"💱 1 TMC = ₦100"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="advert_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "advert_back":
        balance = user_data.get('balance', 0)
        keyboard = [
            [InlineKeyboardButton("💰 Wallet", callback_data="advert_wallet")],
            [InlineKeyboardButton("📢 Create Campaign", callback_data="advert_create")],
            [InlineKeyboardButton("📊 My Campaigns", callback_data="advert_campaigns")],
            [InlineKeyboardButton("💳 Deposit", callback_data="advert_deposit")]
        ]
        msg = f"📢 TMC Ads\n\n💰 Wallet: {balance} TMC\n\n👇 Tap a button"
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# ADMIN BOT (@Dytr44fgh5dxyy5rgbot)
# ============================================================
def admin_start(update, context):
    user = update.effective_user
    uid = str(user.id)

    if not is_admin(uid):
        update.message.reply_text("🔒 Access Denied!")
        return

    keyboard = [
        [InlineKeyboardButton("📋 Deposits", callback_data="admin_deposits")],
        [InlineKeyboardButton("📋 Withdrawals", callback_data="admin_withdrawals")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")]
    ]
    update.message.reply_text(
        "🔐 TMC Admin Panel\n\nWelcome, Admin!\n\n👇 Tap a button",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def admin_callback(update, context):
    query = update.callback_query
    query.answer()
    user = update.effective_user
    uid = str(user.id)
    data = query.data

    if not is_admin(uid):
        query.edit_message_text("🔒 Access Denied!")
        return

    if data == "admin_deposits":
        deposits = ref.child('deposits').order_by_child('status').equal_to('pending').get()
        if not deposits:
            msg = "📋 No pending deposits."
        else:
            msg = "📋 Pending Deposits:\n\n"
            for key, val in deposits.items():
                msg += f"🔹 {val.get('username')}: ₦{val.get('amount')} - {val.get('narration')}\n"
                msg += f"   /approve {key}  |  /decline {key}\n\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_withdrawals":
        withdrawals = ref.child('withdrawals').order_by_child('status').equal_to('pending').get()
        if not withdrawals:
            msg = "📋 No pending withdrawals."
        else:
            msg = "📋 Pending Withdrawals:\n\n"
            for key, val in withdrawals.items():
                msg += f"🔹 {val.get('username')}: ₦{val.get('net_amount')} ({val.get('tmc_amount')} TMC)\n"
                msg += f"   /send {key}  |  /declinew {key}\n\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_users":
        users = ref.child('users').get()
        if not users:
            msg = "👥 Total users: 0"
        else:
            count = len(users)
            msg = f"👥 Total users: {count}\n\n"
            for key, val in list(users.items())[:10]:
                msg += f"🔹 {val.get('username')}: {val.get('balance')} TMC\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_stats":
        users = ref.child('users').get()
        total_users = len(users) if users else 0
        total_balance = 0
        if users:
            for key, val in users.items():
                total_balance += val.get('balance', 0)
        deposits = ref.child('deposits').get()
        total_deposits = len(deposits) if deposits else 0
        msg = (
            f"📊 TMC Stats\n\n"
            f"👥 Total Users: {total_users}\n"
            f"💰 Total Balance: {total_balance} TMC (₦{total_balance * TMC_TO_NAIRA})\n"
            f"💳 Total Deposits: {total_deposits}\n"
            f"📈 Revenue: Coming soon"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_broadcast":
        msg = "📢 Broadcast Message\n\nUse: /broadcast [message]\n\nExample: /broadcast Hello everyone!"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_back":
        keyboard = [
            [InlineKeyboardButton("📋 Deposits", callback_data="admin_deposits")],
            [InlineKeyboardButton("📋 Withdrawals", callback_data="admin_withdrawals")],
            [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")]
        ]
        query.edit_message_text(
            "🔐 TMC Admin Panel\n\n👇 Tap a button",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ============================================================
# ADMIN COMMANDS
# ============================================================
def admin_approve(update, context):
    user = update.effective_user
    uid = str(user.id)
    if not is_admin(uid):
        update.message.reply_text("🔒 Access Denied!")
        return
    args = context.args
    if not args:
        update.message.reply_text("❌ Usage: /approve [deposit_id]")
        return
    deposit_id = args[0]
    deposit = ref.child(f'deposits/{deposit_id}').get()
    if not deposit:
        update.message.reply_text("❌ Deposit not found.")
        return
    if deposit.get('status') != 'pending':
        update.message.reply_text(f"❌ Deposit is already {deposit.get('status')}.")
        return
    amount = deposit.get('amount', 0)
    uid_user = deposit.get('uid')
    tmc_amount = amount // TMC_TO_NAIRA
    current_balance = get_user_balance(uid_user)
    new_balance = current_balance + tmc_amount
    ref.child(f'users/{uid_user}/balance').set(new_balance)
    ref.child(f'deposits/{deposit_id}').update({'status': 'approved', 'approved_at': datetime.now().isoformat()})
    ref.child('ledger').push({'uid': uid_user, 'title': f'💰 Deposit Approved', 'amount': tmc_amount, 'type': 'credit', 'timestamp': datetime.now().isoformat()})
    update.message.reply_text(f"✅ Deposit approved!\n\n💰 Amount: ₦{amount}\n💎 TMC Coins: {tmc_amount}\n👤 User: {deposit.get('username')}\n\n💵 New Balance: {new_balance} TMC")

def admin_decline(update, context):
    user = update.effective_user
    uid = str(user.id)
    if not is_admin(uid):
        update.message.reply_text("🔒 Access Denied!")
        return
    args = context.args
    if not args:
        update.message.reply_text("❌ Usage: /decline [deposit_id]")
        return
    deposit_id = args[0]
    deposit = ref.child(f'deposits/{deposit_id}').get()
    if not deposit:
        update.message.reply_text("❌ Deposit not found.")
        return
    if deposit.get('status') != 'pending':
        update.message.reply_text(f"❌ Deposit is already {deposit.get('status')}.")
        return
    ref.child(f'deposits/{deposit_id}').update({'status': 'rejected', 'rejected_at': datetime.now().isoformat()})
    update.message.reply_text(f"❌ Deposit declined!\n\n👤 User: {deposit.get('username')}\n💰 Amount: ₦{deposit.get('amount')}")

def admin_send(update, context):
    user = update.effective_user
    uid = str(user.id)
    if not is_admin(uid):
        update.message.reply_text("🔒 Access Denied!")
        return
    args = context.args
    if not args:
        update.message.reply_text("❌ Usage: /send [withdrawal_id]")
        return
    withdrawal_id = args[0]
    withdrawal = ref.child(f'withdrawals/{withdrawal_id}').get()
    if not withdrawal:
        update.message.reply_text("❌ Withdrawal not found.")
        return
    if withdrawal.get('status') != 'pending':
        update.message.reply_text(f"❌ Withdrawal is already {withdrawal.get('status')}.")
        return
    ref.child(f'withdrawals/{withdrawal_id}').update({'status': 'approved', 'approved_at': datetime.now().isoformat()})
    update.message.reply_text(f"✅ Withdrawal approved!\n\n👤 User: {withdrawal.get('username')}\n💰 Amount: ₦{withdrawal.get('net_amount')}\n💎 TMC Coins: {withdrawal.get('tmc_amount')}")

def admin_declinew(update, context):
    user = update.effective_user
    uid = str(user.id)
    if not is_admin(uid):
        update.message.reply_text("🔒 Access Denied!")
        return
    args = context.args
    if not args:
        update.message.reply_text("❌ Usage: /declinew [withdrawal_id]")
        return
    withdrawal_id = args[0]
    withdrawal = ref.child(f'withdrawals/{withdrawal_id}').get()
    if not withdrawal:
        update.message.reply_text("❌ Withdrawal not found.")
        return
    if withdrawal.get('status') != 'pending':
        update.message.reply_text(f"❌ Withdrawal is already {withdrawal.get('status')}.")
        return
    uid_user = withdrawal.get('uid')
    tmc_amount = withdrawal.get('tmc_amount', 0)
    current_balance = get_user_balance(uid_user)
    new_balance = current_balance + tmc_amount
    ref.child(f'users/{uid_user}/balance').set(new_balance)
    ref.child(f'withdrawals/{withdrawal_id}').update({'status': 'rejected', 'rejected_at': datetime.now().isoformat()})
    update.message.reply_text(f"❌ Withdrawal declined!\n\n👤 User: {withdrawal.get('username')}\n💰 Amount: ₦{withdrawal.get('net_amount')}\n♻️ Refunded: {tmc_amount} TMC")

def admin_broadcast_command(update, context):
    user = update.effective_user
    uid = str(user.id)
    if not is_admin(uid):
        update.message.reply_text("🔒 Access Denied!")
        return
    args = context.args
    if not args:
        update.message.reply_text("❌ Usage: /broadcast [message]")
        return
    message = ' '.join(args)
    users = ref.child('users').get()
    if not users:
        update.message.reply_text("❌ No users to broadcast to.")
        return
    count = 0
    for key, val in users.items():
        try:
            context.bot.send_message(chat_id=key, text=f"📢 TMC Broadcast:\n\n{message}")
            count += 1
        except:
            pass
    update.message.reply_text(f"✅ Broadcast sent to {count} users!")

# ============================================================
# RUN ALL BOTS
# ============================================================
def run_bot(token, handlers):
    if not token:
        logger.warning(f"⚠️ Token missing, skipping bot")
        return None
    try:
        updater = Updater(token)
        dp = updater.dispatcher
        for handler in handlers:
            dp.add_handler(handler)
        logger.info(f"✅ Bot started: {token[:10]}...")
        updater.start_polling()
        return updater
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        return None

def main():
    logger.info("🚀 Starting ALL 4 TMC Bots with HARCODED FIREBASE...")

    run_bot(ENTRY_BOT_TOKEN, [
        CommandHandler("start", entry_start),
        CallbackQueryHandler(entry_callback)
    ])

    run_bot(MAIN_BOT_TOKEN, [
        CommandHandler("start", main_start),
        CallbackQueryHandler(main_callback)
    ])

    run_bot(ADVERTISER_BOT_TOKEN, [
        CommandHandler("start", advert_start),
        CallbackQueryHandler(advert_callback)
    ])

    run_bot(ADMIN_BOT_TOKEN, [
        CommandHandler("start", admin_start),
        CallbackQueryHandler(admin_callback),
        CommandHandler("approve", admin_approve),
        CommandHandler("decline", admin_decline),
        CommandHandler("send", admin_send),
        CommandHandler("declinew", admin_declinew),
        CommandHandler("broadcast", admin_broadcast_command)
    ])

    logger.info("✅ ALL 4 TMC Bots are running with HARCODED FIREBASE!")

    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
