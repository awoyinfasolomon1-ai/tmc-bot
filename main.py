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
# FIREBASE SERVICE ACCOUNT (FROM YOUR JSON)
# ============================================================
FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "tmc-monetization",
    "private_key_id": "c85e44acaf1d63ebbb03a5a767143f0a3f1de8be",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDU/izHOaYGS8C0\njGFI/GprW1hQOYd6uNkFMsc2VutLYYldOt1yCwPq2mLrv+Kec+uPlcDXlc/Y0E9a\ncdzjz5qBLnAoZCjKAtp+bKM7E0BUrKZiaHxBcXYtLZNH5EdlJ8kXsNxtcXjoAtgx\nNggjyuL3qWyXIhaFaCiM6m8tM1A3DLNQcvDBz3+z/kGIhSErMckYfow+XupxRmZJ\nRkvY+NqQbwiVp+9UJqs2AN6gpG+8CybK7dvp7nmgHrrYd1FU3s87A6NBAkFgCX4+\nfXI/SXNsYCCppriyd+GffAQg43NOccUggbou5nAuz3aoIXdT+Tz3cla4/8vhJhUA\nqONL2ogJAgMBAAECggEAB2lANN7vRVcPsaCUVoIs8Ecdha4YxhcGOyFzD9OarJTs\nXw14LNqQBHUcncwfliidrNF2xDGa6bYG2tRtLZKY00+iuK8SgcPzZxR/4gN3mLKo\nt/Ifh7XrWSNVtXnOl6kYnM3LP7Yj8Tu/GshA5IDv4JL5O7GEk9gF2DBkla+sRfwH\ng5q4JLon4c1Ab56uF5kCdSmSpM22ZwOOBljedB2tYwFeuYOdwygYc0IPtAcz1Fzn\noOdXJPNW2/NYKQzAByiWYCf3yQrqm1ZVM/jan2ZZnIPe9/nJZk3l6WvXwHMqEDev\nYqVBWPOMg25Jz0fLZYvHAw2sut8o3PH7wFbLDKtsUQKBgQDxCSZxCUt7qbiioVLa\n5oC4ocvUgSpNOcY33nKqq+7U7zNeoN0O27kz9gf31HpFd+faPCKFlhsBDtY+PvQY\nnIBMB5D5nt0mI2JAPYJGkH4yRKqhEs3xsW0ckqrPZ4mDF118Mv2T9cFoJlegiq16\nglkVmJIQRCegT9xkUKpksbAWkQKBgQDiN1TVqdwktpRYkjqZpeKiys6i/ASydw9a\neimTHeWpqqJfPqMFUWPs8foOfHgXUIfUsn9GL2YXwDpfDvoc0bo9ru0FYOXfN+OQ\nidm4SnLYxDDDn5MXLVorxrkUBdp6JIAAwx8WBS3KsrU+sZJHS3BLpnp6Sc3iyCGT\nk0rGdEfF+QKBgFd+F8seMZ0g3VmDL50v4Hekm2V2wVEo8I+lGoBjSp1WepIV2Egl\nb9OxsfC+2udOgAWSoIFXHFRE+3W6ykYIwPVYJcLGbMYEQAzLhvdwSa6biEhRmBns\naovdnU0N6zd/irqjk7JamarhiBtJW3FF0WpqaFKpOq0RcBGlykQkz6NRAoGBANkt\nEc8HAghlGMpnqMa10X1Eg1lJ5iCH2T+dpKhOvZxD6xrRgaSrXOmv7cdWi9ymPaFf\ntHznKHaI4AE+2bQtTUXG2FqfilDg0SKElXcuUk/1GnPUkVxg9/6rDChC7lrxC8qv\niPqVAj9ljkegJrU3oZmfPFqG3JhqVoHdmJ4qKHXRAoGAFGRqyX0CZeru6ZuYuyxd\nXGHu+fatP4sxC4bEu+IWVGq66NubTuXLYJgDAMGdetqZCrXk1IBn3QRUkgZxH2hR\nyAZmst2Xo2318AieVTUa6mJEgKdZ93iKzWOwdqFOYfg/mC5Mf6f9XJiPVmJUVzsx\nLSjHevI0YwySF9ZMooIrnKc=\n-----END PRIVATE KEY-----\n",
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

# ============================================================
# BOT TOKENS
# ============================================================
ENTRY_BOT_TOKEN = "8501142592:AAFep9TneyIhAPRh4LNsLI_-gR8kBqU0xqA"
MAIN_BOT_TOKEN = "8718104402:AAFiR3525kfUljhfhw6G6zra-7eQ6kTeOg"
ADVERTISER_BOT_TOKEN = "8320654823:AAETjVGr-pTexuxAeInT2TdSHFnUVYlH9aI"
ADMIN_BOT_TOKEN = "8335073103:AAGR4GUgYl_yh9l3AymEwx0sPwuJV7xW6MM"

ADMIN_IDS = ['8966823502', '6894471315']

# ============================================================
# RATES & CONFIG
# ============================================================
TMC_TO_NAIRA = 100
WITHDRAWAL_FEE = 0.10  # 10%
MIN_WITHDRAW_RECEIVE = 100  # ₦100
VERIFIED_BONUS = 0.20  # +20%

# Palmpay Details
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

def update_balance(uid, amount):
    user = get_user(uid)
    if user:
        new_balance = user.get('balance', 0) + amount
        ref.child(f'users/{uid}/balance').set(new_balance)
        return new_balance
    return None

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
        "🚀 *WELCOME TO TMC* 🔥\n\n"
        "*TMC - Telegram Monetization Coin*\n"
        "*Powering Digital Value. Rewarding Connections.*\n\n"
        "💰 Earn from your Telegram channels, groups, and bots!\n"
        "📢 Advertise to thousands of engaged users!\n\n"
        "*Choose your path:*",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def entry_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == "entry_earn":
        keyboard = [[InlineKeyboardButton("🚀 GO TO EARN BOT", url="https://t.me/TMCTelegraMonetizationBot")]]
        query.edit_message_text(
            "💰 *EARN WITH TMC*\n\n"
            "Turn your Telegram assets into cash!\n\n"
            "✅ Link your channels/groups/bots\n"
            "✅ Earn from views, clicks, and joins\n"
            "✅ Withdraw anytime\n\n"
            "👉 Go to @TMCTelegraMonetizationBot to start earning!",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_advertise":
        keyboard = [[InlineKeyboardButton("🚀 GO TO ADS BOT", url="https://t.me/tmcadvertiserbot")]]
        query.edit_message_text(
            "📢 *ADVERTISE WITH TMC*\n\n"
            "Reach thousands of engaged users!\n\n"
            "✅ Create view/click/join campaigns\n"
            "✅ Reach active channels, groups, and bots\n"
            "✅ Track performance\n\n"
            "👉 Go to @tmcadvertiserbot to create your campaign!",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_learn":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="entry_back")]]
        query.edit_message_text(
            "📖 *ABOUT TMC*\n\n"
            "TMC is a Telegram monetization platform that connects:\n"
            "→ Channel/Group/Bot owners who want to earn\n"
            "→ Advertisers who want to reach audiences\n\n"
            "💰 1 TMC = ₦100\n"
            "💳 Deposit: ₦500 minimum\n"
            "💸 Withdraw: Any amount (10% fee)",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_help":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="entry_back")]]
        query.edit_message_text(
            "❓ *HELP*\n\n"
            "📌 I want to earn: Go to @TMCTelegraMonetizationBot\n"
            "📌 I want to advertise: Go to @tmcadvertiserbot\n"
            "📌 I have a referral link: Click it and choose your path\n"
            "📌 Contact @TMCAdminBot for support",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "entry_back":
        keyboard = [
            [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="entry_earn")],
            [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="entry_advertise")],
            [InlineKeyboardButton("📖 LEARN MORE", callback_data="entry_learn")],
            [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
        ]
        query.edit_message_text(
            "🚀 *WELCOME TO TMC* 🔥\n\n"
            "*Choose your path:*",
            parse_mode='Markdown',
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

    user_data = get_user(uid)
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
        f"👋 *Welcome to TMC Earnings, @{username}!*\n\n"
        f"💰 *Balance:* {balance} TMC (₦{balance * TMC_TO_NAIRA})\n"
        f"📊 *Status:* {status}\n"
        f"📢 *Channels:* {channels}\n"
        f"👥 *Groups:* {groups}\n"
        f"🤖 *Bots:* {bots}\n\n"
        f"👇 *Tap a button below*"
    )
    update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

def main_callback(update, context):
    query = update.callback_query
    query.answer()
    user = update.effective_user
    uid = str(user.id)
    data = query.data

    if is_banned(uid):
        query.edit_message_text("🚫 You are BANNED from TMC!")
        return

    user_data = get_user(uid)

    if data == "main_balance":
        balance = user_data.get('balance', 0)
        verified = user_data.get('verified', False)
        msg = (
            f"💰 *Your Balance*\n\n"
            f"💎 *TMC Coins:* {balance}\n"
            f"🇳🇬 *Naira Value:* ₦{balance * TMC_TO_NAIRA}\n\n"
            f"📊 *Status:* {'✅ Verified' if verified else '🔰 Unverified'}\n"
            f"⚡ *Earnings boost:* {'+20%' if verified else '0%'}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_link":
        msg = (
            "📢 *Link Your Asset*\n\n"
            "*Choose what you want to link:*\n\n"
            "1️⃣ *Channel* - Add @TMCTelegraMonetizationBot as admin\n"
            "2️⃣ *Group* - Add @TMCTelegraMonetizationBot as admin\n"
            "3️⃣ *Bot* - No admin needed, we DM your bot\n\n"
            "*Commands:*\n"
            "/link @channel\n"
            "/linkgroup @group\n"
            "/linkbot @bot\n\n"
            "*Cost: ₦500 (5 TMC) per asset*"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_deposit":
        narration = generate_narration()
        msg = (
            f"💰 *Deposit TMC Coins*\n\n"
            f"*Send ₦X to:*\n\n"
            f"🏦 *Bank:* PalmPay\n"
            f"📋 *Account:* {PALMPAY_ACCOUNT}\n"
            f"📝 *Name:* {PALMPAY_NAME}\n\n"
            f"📌 *Your Narration Code:* `{narration}`\n\n"
            f"*Then use:* `/confirm {narration}`\n\n"
            f"*We'll credit you instantly upon confirmation!*\n\n"
            f"💱 *1 TMC = ₦100*"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_withdraw":
        msg = (
            "💸 *Withdraw TMC Coins*\n\n"
            "*Minimum withdrawal:* Any amount (₦100 receive)\n"
            "*Fee:* 10% (on top)\n\n"
            "*To withdraw:*\n"
            "/withdraw [amount] (in TMC)\n\n"
            "*Example:* /withdraw 10\n"
            f"→ You'll receive: ₦900 (10 TMC = ₦1,000 - 10% fee)\n"
            "*We'll send to your bank within 24-48 hours*"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_referrals":
        refs = user_data.get('referrals', 0)
        earnings = user_data.get('referral_earnings', 0)
        link = f"https://t.me/TMCStartBot?start=ref_{uid}"
        msg = (
            f"👥 *Referral Program*\n\n"
            f"*Your Link:*\n{link}\n\n"
            f"📊 *Referrals:* {refs}\n"
            f"💰 *Earnings:* ₦{earnings}\n\n"
            f"*How it works:*\n"
            f"→ Share your link\n"
            f"→ When they join and take action\n"
            f"→ You get ₦50 (0.5 TMC) bonus!"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_history":
        ledger = ref.child(f'ledger').order_by_child('uid').equal_to(uid).get()
        if not ledger:
            msg = "📊 *No transaction history.*"
        else:
            items = []
            for key, val in ledger.items():
                items.append(val)
            items = items[-5:][::-1]
            msg = "📊 *Recent Transactions:*\n\n"
            for item in items:
                amount = item.get('amount', 0)
                type_icon = "➕" if item.get('type') == 'credit' else "➖"
                msg += f"{type_icon} {item.get('title', 'Transaction')}: {amount} TMC\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_settings":
        msg = (
            "⚙️ *Settings*\n\n"
            "*Choose ad categories you want to receive:*\n\n"
            "1️⃣ Crypto\n"
            "2️⃣ Gaming\n"
            "3️⃣ Business\n"
            "4️⃣ News\n"
            "5️⃣ Memes\n"
            "6️⃣ NSFW\n"
            "7️⃣ Tech\n"
            "8️⃣ Health\n"
            "9️⃣ All\n\n"
            "*Use:* /settings [category]\n"
            "*Example:* /settings Crypto"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "main_back":
        user_data = get_user(uid)
        balance = user_data.get('balance', 0)
        verified = user_data.get('verified', False)
        channels = len(user_data.get('channels', {}))
        groups = len(user_data.get('groups', {}))
        bots = len(user_data.get('bots', {}))
        status = "✅ Verified" if verified else "🔰 Unverified"

        keyboard = [
            [InlineKeyboardButton("💰 Balance", callback_data="main_balance")],
            [InlineKeyboardButton("📢 Link Channel/Group/Bot", callback_data="main_link")],
            [InlineKeyboardButton("💰 Deposit", callback_data="main_deposit")],
            [InlineKeyboardButton("💸 Withdraw", callback_data="main_withdraw")],
            [InlineKeyboardButton("👥 Referrals", callback_data="main_referrals")],
            [InlineKeyboardButton("📊 History", callback_data="main_history")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")]
        ]
        msg = (
            f"👋 *Welcome back!*\n\n"
            f"💰 *Balance:* {balance} TMC (₦{balance * TMC_TO_NAIRA})\n"
            f"📊 *Status:* {status}\n"
            f"📢 *Channels:* {channels}\n"
            f"👥 *Groups:* {groups}\n"
            f"🤖 *Bots:* {bots}\n\n"
            f"👇 *Tap a button below*"
        )
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# MAIN BOT COMMANDS
# ============================================================
def main_balance_command(update, context):
    user = update.effective_user
    uid = str(user.id)
    user_data = get_user(uid)
    if not user_data:
        update.message.reply_text("❌ User not found. Please /start first.")
        return
    balance = user_data.get('balance', 0)
    verified = user_data.get('verified', False)
    msg = (
        f"💰 *Your Balance*\n\n"
        f"💎 *TMC Coins:* {balance}\n"
        f"🇳🇬 *Naira Value:* ₦{balance * TMC_TO_NAIRA}\n\n"
        f"📊 *Status:* {'✅ Verified' if verified else '🔰 Unverified'}"
    )
    update.message.reply_text(msg, parse_mode='Markdown')

def main_deposit_command(update, context):
    narration = generate_narration()
    msg = (
        f"💰 *Deposit TMC Coins*\n\n"
        f"*Send ₦X to:*\n\n"
        f"🏦 *Bank:* PalmPay\n"
        f"📋 *Account:* {PALMPAY_ACCOUNT}\n"
        f"📝 *Name:* {PALMPAY_NAME}\n\n"
        f"📌 *Your Narration Code:* `{narration}`\n\n"
        f"*After sending, use:* `/confirm {narration}`\n\n"
        f"💱 *1 TMC = ₦100*"
    )
    update.message.reply_text(msg, parse_mode='Markdown')

def main_confirm_command(update, context):
    user = update.effective_user
    uid = str(user.id)
    args = context.args
    if not args:
        update.message.reply_text("❌ Please provide a narration code.\nExample: /confirm TMC-ABC123")
        return

    narration = args[0]
    # Check if deposit exists
    deposits = ref.child('deposits').order_by_child('narration').equal_to(narration).get()
    if not deposits:
        update.message.reply_text("❌ Deposit not found. Please check your narration code and try again.")
        return

    # Find the deposit
    deposit_id = None
    deposit_data = None
    for key, val in deposits.items():
        if val.get('status') == 'pending':
            deposit_id = key
            deposit_data = val
            break

    if not deposit_data:
        update.message.reply_text("❌ This deposit has already been processed.")
        return

    amount = deposit_data.get('amount', 0)
    tmc_amount = amount // TMC_TO_NAIRA

    # Update balance
    current_balance = get_user_balance(uid)
    new_balance = current_balance + tmc_amount
    ref.child(f'users/{uid}/balance').set(new_balance)

    # Mark deposit as approved
    ref.child(f'deposits/{deposit_id}').update({
        'status': 'approved',
        'approved_at': datetime.now().isoformat()
    })

    # Add to ledger
    ref.child('ledger').push({
        'uid': uid,
        'title': f'💰 Deposit - {narration}',
        'amount': tmc_amount,
        'type': 'credit',
        'timestamp': datetime.now().isoformat()
    })

    update.message.reply_text(
        f"✅ *Deposit confirmed!*\n\n"
        f"💰 *Amount:* ₦{amount}\n"
        f"💎 *TMC Coins:* {tmc_amount}\n"
        f"💵 *New Balance:* {new_balance} TMC (₦{new_balance * TMC_TO_NAIRA})\n\n"
        f"🎉 Your wallet has been credited!",
        parse_mode='Markdown'
    )

def main_withdraw_command(update, context):
    user = update.effective_user
    uid = str(user.id)
    args = context.args

    if not args:
        update.message.reply_text(
            "❌ Please specify amount in TMC.\n"
            "Example: /withdraw 10\n\n"
            f"⚡ *Minimum withdrawal:* Any amount (₦{MIN_WITHDRAW_RECEIVE} receive)\n"
            f"💰 *Fee:* 10% on top"
        )
        return

    try:
        tmc_amount = float(args[0])
    except ValueError:
        update.message.reply_text("❌ Please enter a valid number.")
        return

    if tmc_amount <= 0:
        update.message.reply_text("❌ Amount must be greater than 0.")
        return

    user_data = get_user(uid)
    if not user_data:
        update.message.reply_text("❌ User not found. Please /start first.")
        return

    balance = user_data.get('balance', 0)
    if tmc_amount > balance:
        update.message.reply_text(f"❌ Insufficient balance. You have {balance} TMC.")
        return

    naira_amount = tmc_amount * TMC_TO_NAIRA
    fee = naira_amount * WITHDRAWAL_FEE
    net_amount = naira_amount - fee

    if net_amount < MIN_WITHDRAW_RECEIVE:
        min_tmc = (MIN_WITHDRAW_RECEIVE + (MIN_WITHDRAW_RECEIVE * WITHDRAWAL_FEE)) / TMC_TO_NAIRA
        update.message.reply_text(
            f"❌ Minimum withdrawal is ₦{MIN_WITHDRAW_RECEIVE} receive.\n"
            f"Please withdraw at least {min_tmc:.1f} TMC."
        )
        return

    msg = (
        f"💸 *Withdrawal Request*\n\n"
        f"💎 *TMC Coins:* {tmc_amount}\n"
        f"🇳🇬 *Gross:* ₦{naira_amount:,.0f}\n"
        f"💰 *Fee (10%):* ₦{fee:,.0f}\n"
        f"✅ *You'll receive:* ₦{net_amount:,.0f}\n\n"
        f"📤 *Please send your bank details:*\n"
        f"Bank Name, Account Number, Account Name"
    )
    update.message.reply_text(msg, parse_mode='Markdown')

    # Save as pending withdrawal
    ref.child('withdrawals').push({
        'uid': uid,
        'username': user_data.get('username'),
        'tmc_amount': tmc_amount,
        'gross_amount': naira_amount,
        'fee': fee,
        'net_amount': net_amount,
        'status': 'pending',
        'timestamp': datetime.now().isoformat()
    })

def main_link_command(update, context):
    user = update.effective_user
    uid = str(user.id)
    args = context.args

    if not args:
        update.message.reply_text(
            "📢 *Link Your Asset*\n\n"
            "/link @channel\n"
            "/linkgroup @group\n"
            "/linkbot @bot\n\n"
            "*Cost: ₦500 (5 TMC) per asset*",
            parse_mode='Markdown'
        )
        return

    asset = args[0]
    user_data = get_user(uid)
    balance = user_data.get('balance', 0)

    if balance < 5:
        update.message.reply_text(
            f"❌ Insufficient balance. You need 5 TMC (₦500) to link an asset.\n"
            f"💰 Your balance: {balance} TMC\n"
            f"💳 Use /deposit to add funds."
        )
        return

    # Deduct 5 TMC
    new_balance = balance - 5
    ref.child(f'users/{uid}/balance').set(new_balance)

    # Add to channels
    channels = user_data.get('channels', {})
    channels[asset] = {
        'linked_at': datetime.now().isoformat(),
        'status': 'active',
        'type': 'channel'
    }
    ref.child(f'users/{uid}/channels').set(channels)

    # Add to ledger
    ref.child('ledger').push({
        'uid': uid,
        'title': f'📢 Linked Channel - {asset}',
        'amount': -5,
        'type': 'debit',
        'timestamp': datetime.now().isoformat()
    })

    update.message.reply_text(
        f"✅ *Channel linked successfully!*\n\n"
        f"📢 {asset}\n"
        f"💰 *Fee:* 5 TMC (₦500)\n"
        f"💵 *New Balance:* {new_balance} TMC\n\n"
        f"🔔 You'll start receiving ads automatically!",
        parse_mode='Markdown'
    )

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

    user_data = get_user(uid)
    balance = user_data.get('balance', 0)

    keyboard = [
        [InlineKeyboardButton("💰 Wallet", callback_data="advert_wallet")],
        [InlineKeyboardButton("📢 Create Campaign", callback_data="advert_create")],
        [InlineKeyboardButton("📊 My Campaigns", callback_data="advert_campaigns")],
        [InlineKeyboardButton("💳 Deposit", callback_data="advert_deposit")]
    ]
    msg = (
        f"📢 *Welcome to TMC Ads, @{username}!*\n\n"
        f"💰 *Wallet:* {balance} TMC (₦{balance * TMC_TO_NAIRA})\n\n"
        f"👇 *Tap a button below*"
    )
    update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

def advert_callback(update, context):
    query = update.callback_query
    query.answer()
    user = update.effective_user
    uid = str(user.id)
    data = query.data

    user_data = get_user(uid)

    if data == "advert_wallet":
        balance = user_data.get('balance', 0)
        msg = f"💰 *Your Wallet*\n\n💎 *TMC Coins:* {balance}\n🇳🇬 *Naira Value:* ₦{balance * TMC_TO_NAIRA}"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="advert_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "advert_create":
        msg = (
            "📢 *Create Campaign*\n\n"
            "*Choose campaign type:*\n\n"
            "👁️ /create views [goal] - Pay per view\n"
            "👆 /create clicks [goal] - Pay per click\n"
            "✅ /create joins [goal] - Pay per join\n\n"
            "*Example:* /create views 10000"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="advert_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "advert_campaigns":
        campaigns = ref.child('campaigns').order_by_child('advertiser_id').equal_to(uid).get()
        if not campaigns:
            msg = "📊 *You have no campaigns.*"
        else:
            msg = "📊 *Your Campaigns:*\n\n"
            for key, val in campaigns.items():
                status = val.get('status', 'active')
                progress = val.get('progress', 0)
                goal = val.get('goal', 0)
                msg += f"🔹 {val.get('title', 'Campaign')}: {progress}/{goal} ({status})\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="advert_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "advert_deposit":
        narration = generate_narration()
        msg = (
            f"💰 *Deposit TMC Coins*\n\n"
            f"*Send ₦X to:*\n\n"
            f"🏦 *Bank:* PalmPay\n"
            f"📋 *Account:* {PALMPAY_ACCOUNT}\n"
            f"📝 *Name:* {PALMPAY_NAME}\n\n"
            f"📌 *Your Narration Code:* `{narration}`\n\n"
            f"*Then use:* `/confirm {narration}`\n\n"
            f"💱 *1 TMC = ₦100*"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="advert_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "advert_back":
        balance = user_data.get('balance', 0)
        keyboard = [
            [InlineKeyboardButton("💰 Wallet", callback_data="advert_wallet")],
            [InlineKeyboardButton("📢 Create Campaign", callback_data="advert_create")],
            [InlineKeyboardButton("📊 My Campaigns", callback_data="advert_campaigns")],
            [InlineKeyboardButton("💳 Deposit", callback_data="advert_deposit")]
        ]
        msg = f"📢 *TMC Ads*\n\n💰 *Wallet:* {balance} TMC\n\n👇 *Tap a button*"
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

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
        "🔐 *TMC Admin Panel*\n\n"
        "Welcome, Admin!\n\n"
        "👇 *Tap a button*",
        parse_mode='Markdown',
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
        deposits = ref.child('deposits').order_by_child('status').equalTo('pending').get()
        if not deposits:
            msg = "📋 *No pending deposits.*"
        else:
            msg = "📋 *Pending Deposits:*\n\n"
            for key, val in deposits.items():
                msg += f"🔹 {val.get('username')}: ₦{val.get('amount')} - {val.get('narration')}\n"
                msg += f"   /approve {key}  |  /decline {key}\n\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_withdrawals":
        withdrawals = ref.child('withdrawals').order_by_child('status').equalTo('pending').get()
        if not withdrawals:
            msg = "📋 *No pending withdrawals.*"
        else:
            msg = "📋 *Pending Withdrawals:*\n\n"
            for key, val in withdrawals.items():
                msg += f"🔹 {val.get('username')}: ₦{val.get('net_amount')} ({val.get('tmc_amount')} TMC)\n"
                msg += f"   /send {key}  |  /declinew {key}\n\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_users":
        users = ref.child('users').get()
        if not users:
            msg = "👥 *Total users:* 0"
        else:
            count = len(users)
            msg = f"👥 *Total users:* {count}\n\n"
            for key, val in users.items():
                if len(msg) > 3500:
                    msg += "\n... and more"
                    break
                msg += f"🔹 {val.get('username')}: {val.get('balance')} TMC\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

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
            f"📊 *TMC Stats*\n\n"
            f"👥 *Total Users:* {total_users}\n"
            f"💰 *Total Balance:* {total_balance} TMC (₦{total_balance * TMC_TO_NAIRA})\n"
            f"💳 *Total Deposits:* {total_deposits}\n"
            f"📈 *Revenue:* Coming soon"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_broadcast":
        msg = (
            "📢 *Broadcast Message*\n\n"
            "Use: /broadcast [message]\n\n"
            "*Example:* /broadcast Hello everyone!"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_back":
        keyboard = [
            [InlineKeyboardButton("📋 Deposits", callback_data="admin_deposits")],
            [InlineKeyboardButton("📋 Withdrawals", callback_data="admin_withdrawals")],
            [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")]
        ]
        query.edit_message_text(
            "🔐 *TMC Admin Panel*\n\n"
            "👇 *Tap a button*",
            parse_mode='Markdown',
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

    # Update balance
    current_balance = get_user_balance(uid_user)
    new_balance = current_balance + tmc_amount
    ref.child(f'users/{uid_user}/balance').set(new_balance)

    # Mark deposit as approved
    ref.child(f'deposits/{deposit_id}').update({
        'status': 'approved',
        'approved_at': datetime.now().isoformat()
    })

    # Add to ledger
    ref.child('ledger').push({
        'uid': uid_user,
        'title': f'💰 Deposit Approved',
        'amount': tmc_amount,
        'type': 'credit',
        'timestamp': datetime.now().isoformat()
    })

    update.message.reply_text(
        f"✅ *Deposit approved!*\n\n"
        f"💰 *Amount:* ₦{amount}\n"
        f"💎 *TMC Coins:* {tmc_amount}\n"
        f"👤 *User:* {deposit.get('username')}\n\n"
        f"💵 *New Balance:* {new_balance} TMC",
        parse_mode='Markdown'
    )

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

    ref.child(f'deposits/{deposit_id}').update({
        'status': 'rejected',
        'rejected_at': datetime.now().isoformat()
    })

    update.message.reply_text(
        f"❌ *Deposit declined!*\n\n"
        f"👤 *User:* {deposit.get('username')}\n"
        f"💰 *Amount:* ₦{deposit.get('amount')}\n\n"
        f"✅ User can try again.",
        parse_mode='Markdown'
    )

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

    ref.child(f'withdrawals/{withdrawal_id}').update({
        'status': 'approved',
        'approved_at': datetime.now().isoformat()
    })

    update.message.reply_text(
        f"✅ *Withdrawal approved!*\n\n"
        f"👤 *User:* {withdrawal.get('username')}\n"
        f"💰 *Amount:* ₦{withdrawal.get('net_amount')}\n"
        f"💎 *TMC Coins:* {withdrawal.get('tmc_amount')}\n\n"
        f"📤 *Please send payment manually.*",
        parse_mode='Markdown'
    )

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

    # Refund balance
    uid_user = withdrawal.get('uid')
    tmc_amount = withdrawal.get('tmc_amount', 0)
    current_balance = get_user_balance(uid_user)
    new_balance = current_balance + tmc_amount
    ref.child(f'users/{uid_user}/balance').set(new_balance)

    ref.child(f'withdrawals/{withdrawal_id}').update({
        'status': 'rejected',
        'rejected_at': datetime.now().isoformat()
    })

    update.message.reply_text(
        f"❌ *Withdrawal declined!*\n\n"
        f"👤 *User:* {withdrawal.get('username')}\n"
        f"💰 *Amount:* ₦{withdrawal.get('net_amount')}\n"
        f"♻️ *Refunded:* {tmc_amount} TMC\n\n"
        f"✅ Balance restored.",
        parse_mode='Markdown'
    )

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
            update.context.bot.send_message(chat_id=key, text=f"📢 *TMC Broadcast:*\n\n{message}", parse_mode='Markdown')
            count += 1
        except:
            pass

    update.message.reply_text(f"✅ *Broadcast sent to {count} users!*", parse_mode='Markdown')

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

    # Entry Bot (@TMCStartBot)
    entry_updater = run_bot(ENTRY_BOT_TOKEN, [
        CommandHandler("start", entry_start),
        CallbackQueryHandler(entry_callback)
    ])

    # Main Bot (@TMCTelegraMonetizationBot)
    main_updater = run_bot(MAIN_BOT_TOKEN, [
        CommandHandler("start", main_start),
        CallbackQueryHandler(main_callback),
        CommandHandler("balance", main_balance_command),
        CommandHandler("deposit", main_deposit_command),
        CommandHandler("confirm", main_confirm_command),
        CommandHandler("withdraw", main_withdraw_command),
        CommandHandler("link", main_link_command)
    ])

    # Advertiser Bot (@tmcadvertiserbot)
    advert_updater = run_bot(ADVERTISER_BOT_TOKEN, [
        CommandHandler("start", advert_start),
        CallbackQueryHandler(advert_callback)
    ])

    # Admin Bot (@Dytr44fgh5dxyy5rgbot)
    admin_updater = run_bot(ADMIN_BOT_TOKEN, [
        CommandHandler("start", admin_start),
        CallbackQueryHandler(admin_callback),
        CommandHandler("approve", admin_approve),
        CommandHandler("decline", admin_decline),
        CommandHandler("send", admin_send),
        CommandHandler("declinew", admin_declinew),
        CommandHandler("broadcast", admin_broadcast_command)
    ])

    logger.info("✅ ALL 4 TMC Bots are running!")

    # Keep running
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
