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
ADVERTISER_BOT_TOKEN = "8320654823:AAETjVGr-pTexuxAeInT2TdSHFnUVYlH9aI"

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

TMC_TO_NAIRA = 100

def advert_start(update, context):
    user = update.effective_user
    uid = str(user.id)
    username = user.username or user.first_name
    if not get_user(uid):
        create_user(uid, username)
    user_data = get_user(uid) or {}
    balance = user_data.get('balance', 0)
    keyboard = [
        [InlineKeyboardButton("💰 Wallet", callback_data="advert_wallet")],
        [InlineKeyboardButton("📢 Create Campaign", callback_data="advert_create")],
        [InlineKeyboardButton("📊 My Campaigns", callback_data="advert_campaigns")]
    ]
    msg = f"📢 Welcome to TMC Ads, @{username}!\n\n💰 Wallet: {balance} TMC (₦{balance * TMC_TO_NAIRA})\n\n👇 Tap a button below"
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
        msg = "📢 Create Campaign\n\n👁️ /create views [goal]\n👆 /create clicks [goal]\n✅ /create joins [goal]"
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
    elif data == "advert_back":
        balance = user_data.get('balance', 0)
        keyboard = [
            [InlineKeyboardButton("💰 Wallet", callback_data="advert_wallet")],
            [InlineKeyboardButton("📢 Create Campaign", callback_data="advert_create")],
            [InlineKeyboardButton("📊 My Campaigns", callback_data="advert_campaigns")]
        ]
        msg = f"📢 TMC Ads\n\n💰 Wallet: {balance} TMC\n\n👇 Tap a button"
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    logger.info("🚀 Starting ADVERTISER BOT...")
    updater = Updater(ADVERTISER_BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", advert_start))
    dp.add_handler(CallbackQueryHandler(advert_callback))
    updater.start_polling()
    logger.info("✅ ADVERTISER BOT is running!")
    updater.idle()

if __name__ == "__main__":
    main()
