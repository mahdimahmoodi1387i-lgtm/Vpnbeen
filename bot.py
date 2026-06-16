import sqlite3
import nest_asyncio
nest_asyncio.apply()

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔴 تنظیمات
TOKEN = "8905944062:AAEeW8NohFFTcJwHyl8lgdYP3mCkas97e9s"
ADMIN_ID = 5122354878
SUPPORT_USERNAME = "bintoos"

# 🗄️ دیتابیس
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    ref_by INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS points (
    user_id INTEGER PRIMARY KEY,
    point INTEGER DEFAULT 0
)
""")

conn.commit()

# 🌍 پلن‌ها
PLANS = {
    "🇩🇪 آلمان (پینگ پایین)": {
        "10GB": 70000,
        "20GB": 135000,
        "30GB": 199000,
        "40GB": 260000,
        "50GB": 319000
    },
    "🇩🇪 آلمان": {
        "10GB": 55000,
        "20GB": 110000,
        "30GB": 160000,
        "40GB": 210000,
        "50GB": 230000
    },
    "🇹🇷 ترکیه": {
        "10GB": 60000,
        "20GB": 120000,
        "30GB": 170000,
        "40GB": 220000,
        "50GB": 259000
    },
    "🇫🇮 فلاند": {
        "20GB": 70000,
        "30GB": 100000,
        "40GB": 129000,
        "50GB": 159000,
        "60GB": 179000
    }
}

COUNTRIES = list(PLANS.keys())

# 🧠 وضعیت کاربران
user_country = {}
user_plan = {}
pending_users = set()

# 🎛 منوی اصلی
main_markup = ReplyKeyboardMarkup(
    [["🛒 خرید VPN", "🧪 تست VPN"],
     ["🆘 پشتیبانی", "📄 درباره ما"],
     ["👥 پنل رفرال"]],
    resize_keyboard=True
)

# ➕ کاربر
def add_user(user_id):
    cursor.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

# 📊 رفرال
def get_ref_count(user_id):
    cursor.execute("SELECT COUNT(*) FROM users WHERE ref_by=?", (user_id,))
    return cursor.fetchone()[0]

def get_points(user_id):
    cursor.execute("SELECT point FROM points WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

# 🚀 start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    args = context.args

    add_user(user_id)

    # ثبت رفرال
    if args:
        ref_id = int(args[0])
        if ref_id != user_id:
            cursor.execute("SELECT ref_by FROM users WHERE user_id=?", (user_id,))
            row = cursor.fetchone()

            if not row or row[0] is None:
                cursor.execute("UPDATE users SET ref_by=? WHERE user_id=?", (ref_id, user_id))

                cursor.execute(
                    "INSERT INTO points(user_id, point) VALUES(?, 1) "
                    "ON CONFLICT(user_id) DO UPDATE SET point = point + 1",
                    (ref_id,)
                )
                conn.commit()

    bot_username = context.bot.username
    link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(
        "👋 خوش اومدی به ربات VPN\n\n"
        f"🔗 لینک دعوت تو:\n{link}\n\n"
        "💰 هر دعوت = 1 امتیاز",
        reply_markup=main_markup
    )

# 🧠 هندل پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    text = update.message.text

    # خرید
    if text == "🛒 خرید VPN":
        buttons = [[c] for c in COUNTRIES]
        await update.message.reply_text(
            "🌍 کشور رو انتخاب کن:",
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )

    # انتخاب کشور
    elif text in PLANS:
        user_country[user_id] = text

        buttons = [[p] for p in PLANS[text].keys()]
        await update.message.reply_text(
            "📦 پلن رو انتخاب کن:",
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )

    # انتخاب پلن
    elif user_id in user_country and text in PLANS[user_country[user_id]]:
        country = user_country[user_id]
        price = PLANS[country][text]

        user_plan[user_id] = text
        pending_users.add(user_id)

        await update.message.reply_text(
            f"🌍 کشور: {country}\n"
            f"📦 پلن: {text}\n"
            f"💰 قیمت: {price:,} تومان\n\n"
            "💳 کارت:\n6219-XXXX-XXXX-XXXX\n\n"
            "📸 فیش رو بفرست"
        )

    # تست VPN
    elif text == "🧪 تست VPN":
        await update.message.reply_text(
            "🧪 درخواست تست ثبت شد\n⏳ منتظر ادمین باشید"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🧪 درخواست تست VPN\n👤 {user_id}\n\nvpn_test:{user_id}|TEST_LINK"
        )

    # پشتیبانی
    elif text == "🆘 پشتیبانی":
        await update.message.reply_text(
            f"📩 پشتیبانی:\nhttps://t.me/{SUPPORT_USERNAME}"
        )

    # درباره ما
    elif text == "📄 درباره ما":
        await update.message.reply_text(
            "📄 درباره ما\n\n"
            "🔥 فروش VPN پرسرعت\n"
            "✔ سرورهای آلمان، ترکیه، فلاند\n"
            "✔ پینگ پایین\n"
            "✔ پشتیبانی 24/7"
        )

    # پنل رفرال
    elif text == "👥 پنل رفرال":
        count = get_ref_count(user_id)
        points = get_points(user_id)

        bot_username = context.bot.username
        link = f"https://t.me/{bot_username}?start={user_id}"

        await update.message.reply_text(
            "📊 پنل رفرال\n\n"
            f"👥 دعوت‌ها: {count}\n"
            f"⭐ امتیاز: {points}\n\n"
            f"🔗 لینک:\n{link}"
        )

    else:
        await update.message.reply_text("👇 از دکمه‌ها استفاده کن")

# 📸 فیش
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in pending_users:
        photo = update.message.photo[-1].file_id

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=f"💳 فیش جدید\n👤 {user_id}\nvpn:{user_id}|LINK"
        )

        await update.message.reply_text("✅ ارسال شد")

# 👨‍💻 ادمین
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return

    text = update.message.text

    # VPN اصلی
    if text.startswith("vpn:"):
        uid, link = text.replace("vpn:", "").split("|")

        await context.bot.send_message(
            chat_id=int(uid),
            text=f"🎉 VPN شما:\n{link}"
        )

    # VPN تست
    elif text.startswith("vpn_test:"):
        uid, link = text.replace("vpn_test:", "").split("|")

        await context.bot.send_message(
            chat_id=int(uid),
            text=f"🧪 VPN تست شما:\n{link}\n⏳ محدود"
        )

# 🤖 اجرا
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), admin))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("Bot running...")

async def main():
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

await main()
