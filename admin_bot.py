import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import firebase_admin
from firebase_admin import credentials, db

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
ADMIN_BOT_TOKEN = "8335073103:AAGR4GUgYl_yh9l3AymEwx0sPwuJV7xW6MM"
ADMIN_IDS = ['8966823502', '6894471315']

def is_admin(uid):
    return uid in ADMIN_IDS

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
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")]
    ]
    update.message.reply_text("🔐 TMC Admin Panel\n\nWelcome, Admin!\n\n👇 Tap a button", reply_markup=InlineKeyboardMarkup(keyboard))

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
                msg += f"🔹 {val.get('username')}: ₦{val.get('amount')}\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "admin_withdrawals":
        withdrawals = ref.child('withdrawals').order_by_child('status').equal_to('pending').get()
        if not withdrawals:
            msg = "📋 No pending withdrawals."
        else:
            msg = "📋 Pending Withdrawals:\n\n"
            for key, val in withdrawals.items():
                msg += f"🔹 {val.get('username')}: ₦{val.get('net_amount')}\n"
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
        msg = f"📊 TMC Stats\n\n👥 Total Users: {total_users}\n💰 Total Balance: {total_balance} TMC\n💳 Total Deposits: {total_deposits}"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "admin_back":
        keyboard = [
            [InlineKeyboardButton("📋 Deposits", callback_data="admin_deposits")],
            [InlineKeyboardButton("📋 Withdrawals", callback_data="admin_withdrawals")],
            [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")]
        ]
        query.edit_message_text("🔐 TMC Admin Panel\n\n👇 Tap a button", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    logger.info("🚀 Starting ADMIN BOT...")
    updater = Updater(ADMIN_BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", admin_start))
    dp.add_handler(CallbackQueryHandler(admin_callback))
    updater.start_polling()
    logger.info("✅ ADMIN BOT is running!")
    updater.idle()

if __name__ == "__main__":
    main()
