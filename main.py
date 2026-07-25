import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import firebase_admin
from firebase_admin import credentials, db
import json

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================
# FIREBASE CONFIG
# ============================================================
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyD-JLXyO1F1sWToj6WsjxLeQYJyu5tWuJc",
    "authDomain": "tmc-monetization.firebaseapp.com",
    "databaseURL": "https://tmc-monetization-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "tmc-monetization",
    "storageBucket": "tmc-monetization.firebasestorage.app",
    "messagingSenderId": "462323907910",
    "appId": "1:462323907910:web:9c811ae2170029d420b947"
}

# Initialize Firebase
cred_obj = credentials.Certificate({
    "type": "service_account",
    "project_id": FIREBASE_CONFIG["projectId"],
    "private_key_id": "your-private-key-id",
    "private_key": "your-private-key",
    "client_email": "your-service-account-email",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "your-cert-url"
})

# Initialize Firebase Admin SDK
firebase_admin.initialize_app(cred_obj, {
    'databaseURL': FIREBASE_CONFIG["databaseURL"]
})

ref = db.reference('/')

# ============================================================
# BOT TOKENS (From Environment Variables)
# ============================================================
MAIN_BOT_TOKEN = os.environ.get("MAIN_BOT_TOKEN", "8718104402:AAFiR3525kfUljhfhw6G6zra-7eQ6kTeOg")
ADVERTISER_BOT_TOKEN = os.environ.get("ADVERTISER_BOT_TOKEN", "8320654823:AAETjVGr-pTexuxAeInT2TdSHFnUVYlH9aI")
ADMIN_BOT_TOKEN = os.environ.get("ADMIN_BOT_TOKEN", "8335073103:AAGR4GUgYl_yh9l3AymEwx0sPwuJV7xW6MM")
ENTRY_BOT_TOKEN = os.environ.get("ENTRY_BOT_TOKEN", "8501142592:AAFep9TneyIhAPRh4LNsLI_-gR8kBqU0xqA")

ADMIN_IDS = ['8966823502', '6894471315']  # Solomon & Danimero

# ============================================================
# RATES (Locked In)
# ============================================================
VIEW_RATE_UNVERIFIED = 100  # ₦100 per 1,000 views
VIEW_RATE_VERIFIED = 120    # ₦120 per 1,000 views
CLICK_RATE_UNVERIFIED = 2   # ₦2 per click
CLICK_RATE_VERIFIED = 2.4   # ₦2.40 per click
JOIN_RATE_UNVERIFIED = 5    # ₦5 per join
JOIN_RATE_VERIFIED = 6      # ₦6 per join

ADVERTISER_VIEW_RATE = 200  # ₦200 per 1,000 views
ADVERTISER_CLICK_RATE = 7.5 # ₦7.5 per click
ADVERTISER_JOIN_RATE = 10   # ₦10 per join

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_user(uid):
    """Get user data from Firebase"""
    try:
        user_ref = ref.child(f'users/{uid}')
        return user_ref.get()
    except:
        return None

def update_user(uid, data):
    """Update user data in Firebase"""
    try:
        ref.child(f'users/{uid}').update(data)
        return True
    except:
        return False

def create_user(uid, username):
    """Create new user in Firebase"""
    try:
        user_data = {
            'uid': uid,
            'username': username,
            'balance': 0,
            'status': 'active',
            'role': 'user',
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

def is_admin(uid):
    """Check if user is admin"""
    return uid in ADMIN_IDS

def is_banned(uid):
    """Check if user is banned"""
    user = get_user(uid)
    if user:
        return user.get('status') == 'banned'
    return False

# ============================================================
# ENTRY BOT (@TMCStartBot)
# ============================================================
async def entry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry bot /start command"""
    user = update.effective_user
    uid = str(user.id)
    username = user.username or user.first_name
    
    # Check if user exists
    if not get_user(uid):
        create_user(uid, username)
    
    keyboard = [
        [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="entry_earn")],
        [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="entry_advertise")],
        [InlineKeyboardButton("📖 LEARN MORE", callback_data="entry_learn")],
        [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = """🚀 *WELCOME TO TMC* 🔥

*TMC - Telegram Monetization Coin*
*Powering Digital Value. Rewarding Connections.*

---

💰 *Earn from your Telegram channels, groups, and bots!*
📢 *Advertise to thousands of engaged users!*

---

*Choose your path:*

👇 *Tap a button below to begin*"""
    
    await update.message.reply_text(welcome_msg, parse_mode='Markdown', reply_markup=reply_markup)

async def entry_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle entry bot callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "entry_earn":
        msg = """💰 *EARN WITH TMC*

*Turn your Telegram assets into cash!*

✅ Monetize channels (5-15 channels)
✅ Monetize groups (3-10 groups)
✅ Monetize bots (2-5 bots)

Earn from:
👁️ Views – ₦100 per 1,000 views
👆 Clicks – ₦2 per click
✅ Joins – ₦5 per join

👉 *Go to @TMCTelegraMonetizationBot to start earning!*

*Make sure to add the bot as admin to your channel/group!*"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 GO TO EARN BOT", url="https://t.me/TMCTelegraMonetizationBot")],
            [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="entry_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "entry_advertise":
        msg = """📢 *ADVERTISE WITH TMC*

*Reach thousands of engaged users!*

Your ad goes to:
✅ Active Telegram channels
✅ Active Telegram groups
✅ Active Telegram bots

Choose your campaign:
👁️ Views – ₦200 per 1,000 views
👆 Clicks – ₦7.5 per click
✅ Joins – ₦10 per join

👉 *Go to @tmcadvertiserbot to create your campaign!*

*Deposit ₦500 minimum to buy TMC coins*"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 GO TO ADS BOT", url="https://t.me/tmcadvertiserbot")],
            [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="entry_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "entry_learn":
        msg = """📖 *ABOUT TMC*

TMC is a Telegram monetization platform that connects:
→ Channel/Group/Bot owners who want to earn
→ Advertisers who want to reach audiences

*How it works:*

1. Channel owners link their assets (₦500 each)
2. Advertisers create campaigns (buy TMC coins)
3. TMC distributes ads intelligently
4. Channel owners earn from views/clicks/joins
5. Withdraw anytime (10% fee on top)

---

*💰 TMC Coins: 1 TMC = ₦100*
*💳 Deposit: ₦500 minimum*
*💸 Withdraw: Any amount (min ₦100 receive)*"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="entry_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "entry_help":
        msg = """❓ *TMC HELP*

📌 I want to earn:
→ Go to @TMCTelegraMonetizationBot
→ Link your channels/groups/bots
→ Start earning from ads

📌 I want to advertise:
→ Go to @tmcadvertiserbot
→ Deposit ₦500+ to buy TMC coins
→ Create your campaign

📌 I have a referral link:
→ Just click the link and choose your path
→ Your referrer gets ₦50 when you take action

📌 I have a question:
→ Contact @TMCAdminBot (admin only)

---

*Thank you for choosing TMC! 🚀*"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="entry_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "entry_back":
        keyboard = [
            [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="entry_earn")],
            [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="entry_advertise")],
            [InlineKeyboardButton("📖 LEARN MORE", callback_data="entry_learn")],
            [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_msg = """🚀 *WELCOME TO TMC* 🔥

*TMC - Telegram Monetization Coin*
*Powering Digital Value. Rewarding Connections.*

---

💰 *Earn from your Telegram channels, groups, and bots!*
📢 *Advertise to thousands of engaged users!*

---

*Choose your path:*

👇 *Tap a button below to begin*"""
        await query.edit_message_text(welcome_msg, parse_mode='Markdown', reply_markup=reply_markup)

# ============================================================
# MAIN BOT (@TMCTelegraMonetizationBot)
# ============================================================
async def main_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main bot /start command"""
    user = update.effective_user
    uid = str(user.id)
    username = user.username or user.first_name
    
    if is_banned(uid):
        await update.message.reply_text("🚫 You are BANNED from TMC!\nContact @TMCAdminBot for more information.")
        return
    
    if not get_user(uid):
        create_user(uid, username)
    
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="main_balance")],
        [InlineKeyboardButton("📢 Link Channel/Group/Bot", callback_data="main_link")],
        [InlineKeyboardButton("💰 Deposit", callback_data="main_deposit")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="main_withdraw")],
        [InlineKeyboardButton("👥 Referrals", callback_data="main_referrals")],
        [InlineKeyboardButton("📊 History", callback_data="main_history")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    user_data = get_user(uid)
    balance = user_data.get('balance', 0) if user_data else 0
    
    msg = f"""👋 *Welcome to TMC Earnings, @{username}!*

*💰 Your Balance: {balance} TMC (₦{balance * 100})*

*Your Status:* {'✅ Verified' if user_data and user_data.get('verified') else '🔰 Unverified'}

*Channels: {len(user_data.get('channels', {})) if user_data else 0}* 
*Groups: {len(user_data.get('groups', {})) if user_data else 0}*
*Bots: {len(user_data.get('bots', {})) if user_data else 0}*

👇 *Tap a button below*"""
    
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

# ============================================================
# MAIN BOT CALLBACKS
# ============================================================
async def main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main bot callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = str(user.id)
    data = query.data
    
    if is_banned(uid):
        await query.edit_message_text("🚫 You are BANNED from TMC!\nContact @TMCAdminBot for more information.")
        return
    
    user_data = get_user(uid) or {}
    
    if data == "main_balance":
        balance = user_data.get('balance', 0)
        verified = user_data.get('verified', False)
        msg = f"""💰 *Your Balance*

*TMC Coins:* {balance}
*Naira Value:* ₦{balance * 100}

*Status:* {'✅ Verified' if verified else '🔰 Unverified'}

*Earnings boost:* {'+20%' if verified else '0%'}"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "main_link":
        msg = """📢 *Link Your Asset*

*Choose what you want to link:*

1️⃣ *Channel* - Add @TMCTelegraMonetizationBot as admin
2️⃣ *Group* - Add @TMCTelegraMonetizationBot as admin
3️⃣ *Bot* - No admin needed, we DM your bot

*Command:*
/link @username
/linkgroup @groupname
/linkbot @botname

*Cost: ₦500 (5 TMC) per asset*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "main_deposit":
        msg = """💰 *Deposit TMC Coins*

*Send ₦X to:*

🏦 *Bank:* PalmPay
📋 *Account:* 896-2925-124
📝 *Name:* NEXUS EARN LIMITED (TAIWO)

*📌 Your Narration Code:* Use this as your narration

*Then use: /confirm [narration_code]*

*Example:* /confirm NX-ABC123

*We'll credit you instantly upon confirmation!*

*1 TMC = ₦100*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "main_withdraw":
        msg = """💸 *Withdraw TMC Coins*

*Minimum withdrawal:* Any amount
*Fee:* 10% (on top)

*To withdraw:*
/withdraw [amount]

*Example:* /withdraw 10 TMC

*You'll receive:* ₦900 (10 TMC = ₦1,000 - 10% fee)
*We'll send to your bank within 24-48 hours*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "main_referrals":
        refs = user_data.get('referrals', 0)
        earnings = user_data.get('referral_earnings', 0)
        link = f"https://t.me/TMCStartBot?start=ref_{uid}"
        
        msg = f"""👥 *Referral Program*

*Your Link:*
{link}

*Stats:*
📊 Referrals: {refs}
💰 Earnings: ₦{earnings}

*How it works:*
→ Share your link
→ When they join and take action
→ You get ₦50 (0.5 TMC) bonus!"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "main_history":
        msg = """📊 *Your Earnings History*

*Coming soon!*
*We're building this feature.*
*Check back later.*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "main_settings":
        msg = """⚙️ *Settings*

*Choose ad categories you want to receive:*

1️⃣ Crypto
2️⃣ Gaming
3️⃣ Business
4️⃣ News
5️⃣ Memes
6️⃣ NSFW
7️⃣ Tech
8️⃣ Health
9️⃣ All

*Use: /settings [category]*

*Example:* /settings Crypto"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "main_back":
        keyboard = [
            [InlineKeyboardButton("💰 Balance", callback_data="main_balance")],
            [InlineKeyboardButton("📢 Link Channel/Group/Bot", callback_data="main_link")],
            [InlineKeyboardButton("💰 Deposit", callback_data="main_deposit")],
            [InlineKeyboardButton("💸 Withdraw", callback_data="main_withdraw")],
            [InlineKeyboardButton("👥 Referrals", callback_data="main_referrals")],
            [InlineKeyboardButton("📊 History", callback_data="main_history")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        balance = user_data.get('balance', 0)
        msg = f"""👋 *Welcome back!*

*💰 Balance: {balance} TMC (₦{balance * 100})*

*Status:* {'✅ Verified' if user_data.get('verified') else '🔰 Unverified'}

👇 *Tap a button below*"""
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

# ============================================================
# ADVERTISER BOT (@tmcadvertiserbot)
# ============================================================
async def advert_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Advertiser bot /start command"""
    user = update.effective_user
    uid = str(user.id)
    username = user.username or user.first_name
    
    if is_banned(uid):
        await update.message.reply_text("🚫 You are BANNED from TMC!\nContact @TMCAdminBot for more information.")
        return
    
    if not get_user(uid):
        create_user(uid, username)
    
    keyboard = [
        [InlineKeyboardButton("💰 Wallet", callback_data="advert_wallet")],
        [InlineKeyboardButton("📢 Create Campaign", callback_data="advert_create")],
        [InlineKeyboardButton("📊 My Campaigns", callback_data="advert_campaigns")],
        [InlineKeyboardButton("💳 Deposit", callback_data="advert_deposit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = f"""📢 *Welcome to TMC Ads, @{username}!*

*Reach thousands of engaged users!*

💰 *Wallet: {user_data.get('balance', 0) if user_data else 0} TMC*

👇 *Tap a button below*"""
    
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

# ============================================================
# ADMIN BOT (@Dytr44fgh5dxyy5rgbot)
# ============================================================
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin bot /start command"""
    user = update.effective_user
    uid = str(user.id)
    
    if not is_admin(uid):
        await update.message.reply_text("🔒 Access Denied!\nYou are not authorized to use this bot.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📋 Pending Deposits", callback_data="admin_deposits")],
        [InlineKeyboardButton("📋 Pending Withdrawals", callback_data="admin_withdrawals")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = f"""🔐 *TMC Admin Panel*

Welcome, Admin!

👇 *Tap a button to manage the platform*"""
    
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

# ============================================================
# MAIN FUNCTION - RUN ALL BOTS
# ============================================================
async def main():
    """Run all 4 bots"""
    
    # Create applications for each bot
    entry_app = Application.builder().token(ENTRY_BOT_TOKEN).build()
    main_app = Application.builder().token(MAIN_BOT_TOKEN).build()
    advert_app = Application.builder().token(ADVERTISER_BOT_TOKEN).build()
    admin_app = Application.builder().token(ADMIN_BOT_TOKEN).build()
    
    # Add handlers for ENTRY bot
    entry_app.add_handler(CommandHandler("start", entry_start))
    entry_app.add_handler(CallbackQueryHandler(entry_callback, pattern="^entry_"))
    
    # Add handlers for MAIN bot
    main_app.add_handler(CommandHandler("start", main_start))
    main_app.add_handler(CallbackQueryHandler(main_callback, pattern="^main_"))
    main_app.add_handler(CommandHandler("balance", main_balance))
    main_app.add_handler(CommandHandler("deposit", main_deposit))
    main_app.add_handler(CommandHandler("withdraw", main_withdraw))
    main_app.add_handler(CommandHandler("link", main_link))
    
    # Add handlers for ADVERTISER bot
    advert_app.add_handler(CommandHandler("start", advert_start))
    advert_app.add_handler(CallbackQueryHandler(advert_callback, pattern="^advert_"))
    
    # Add handlers for ADMIN bot
    admin_app.add_handler(CommandHandler("start", admin_start))
    admin_app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    admin_app.add_handler(CommandHandler("deposits", admin_deposits))
    admin_app.add_handler(CommandHandler("approve", admin_approve))
    admin_app.add_handler(CommandHandler("decline", admin_decline))
    admin_app.add_handler(CommandHandler("withdrawals", admin_withdrawals))
    admin_app.add_handler(CommandHandler("send", admin_send))
    admin_app.add_handler(CommandHandler("users", admin_users))
    admin_app.add_handler(CommandHandler("verify", admin_verify))
    admin_app.add_handler(CommandHandler("ban", admin_ban))
    admin_app.add_handler(CommandHandler("unban", admin_unban))
    admin_app.add_handler(CommandHandler("broadcast", admin_broadcast))
    
    # Start all bots
    await entry_app.initialize()
    await main_app.initialize()
    await advert_app.initialize()
    await admin_app.initialize()
    
    await entry_app.start()
    await main_app.start()
    await advert_app.start()
    await admin_app.start()
    
    await entry_app.updater.start_polling()
    await main_app.updater.start_polling()
    await advert_app.updater.start_polling()
    await admin_app.updater.start_polling()
    
    logger.info("✅ All 4 TMC Bots are running!")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
