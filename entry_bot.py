import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# FIREBASE (HARDCODED)
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
# BOT TOKENS
# ============================================================
ENTRY_BOT_TOKEN = "8501142592:AAFep9TneyIhAPRh4LNsLI_-gR8kBqU0xqA"

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
        "🚀 WELCOME TO TMC 🔥\n\nTMC - Telegram Monetization Coin\n\nChoose your path:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def entry_callback(update, context):
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
        query.edit_message_text("📖 ABOUT TMC\n\n1 TMC = ₦100\nDeposit: ₦500 min\nWithdraw: 10% fee", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "entry_help":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="entry_back")]]
        query.edit_message_text("❓ HELP\n\nContact @TMCAdminBot", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "entry_back":
        keyboard = [
            [InlineKeyboardButton("💰 I WANT TO EARN", callback_data="entry_earn")],
            [InlineKeyboardButton("📢 I WANT TO ADVERTISE", callback_data="entry_advertise")],
            [InlineKeyboardButton("📖 LEARN MORE", callback_data="entry_learn")],
            [InlineKeyboardButton("❓ HELP", callback_data="entry_help")]
        ]
        query.edit_message_text("🚀 WELCOME TO TMC 🔥\n\nChoose your path:", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    logger.info("🚀 Starting ENTRY BOT...")
    updater = Updater(ENTRY_BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", entry_start))
    dp.add_handler(CallbackQueryHandler(entry_callback))
    updater.start_polling()
    logger.info("✅ ENTRY BOT is running!")
    updater.idle()

if __name__ == "__main__":
    main()
