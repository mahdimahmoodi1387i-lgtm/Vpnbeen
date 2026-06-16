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
    [["🛒 خرید VPN", "🆘 پشتیبانی"],
     ["📄 درباره ما"]],
    resize_keyboard=True
)

# ➕ ثبت کاربر
def add_user(user_id):
    cursor.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

# 🚀 استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    add_user(user_id)

    await update.message.reply_text(
        "👋 خوش اومدی به ربات VPN\n\nیکی از گزینه‌ها رو انتخاب کن 👇",
        reply_markup=main_markup
    )

# 🌍 منوی کشور
def country_menu():
    return ReplyKeyboardMarkup(
        [[c] for c in COUNTRIES] + [["🔙 برگشت"]],
        resize_keyboard=True
    )

# 📦 منوی پلن
def plan_menu(country):
    return ReplyKeyboardMarkup(
        [[p] for p in PLANS[country].keys()] + [["🔙 برگشت"]],
        resize_keyboard=True
    )

# 🧠 مدیریت پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    text = update.message.text

    # خرید
    if text == "🛒 خرید VPN":
        await update.message.reply_text(
            "🌍 کشور رو انتخاب کن:",
            reply_markup=country_menu()
        )

    # برگشت به منوی اصلی
    elif text == "🔙 برگشت" and user_id not in user_country:
        await update.message.reply_text("🏠 برگشتی به منو", reply_markup=main_markup)

    # انتخاب کشور
    elif text in PLANS:
        user_country[user_id] = text

        await update.message.reply_text(
            "📦 پلن رو انتخاب کن:",
            reply_markup=plan_menu(text)
        )

    # برگشت از پلن به کشور
    elif text == "🔙 برگشت" and user_id in user_country:
        user_country.pop(user_id, None)

        await update.message.reply_text(
            "🌍 کشور رو انتخاب کن:",
            reply_markup=country_menu()
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
            "📸 فیش پرداخت رو بفرست"
        )

    # پشتیبانی
    elif text == "🆘 پشتیبانی":
        await update.message.reply_text(
            f"📩 ارتباط مستقیم با پشتیبانی 👇\nhttps://t.me/{SUPPORT_USERNAME}"
        )

    # درباره ما
    elif text == "📄 درباره ما":
        await update.message.reply_text(
            "📄 درباره ما\n\n"
            "این ربات برای فروش VPN پرسرعت ساخته شده 🚀\n\n"
            "✔ سرورهای متنوع\n"
            "✔ پینگ پایین\n"
            "✔ پشتیبانی سریع\n\n"
            "🙏 ممنون از انتخاب شما"
        )

    else:
        await update.message.reply_text("👇 از دکمه‌ها استفاده کن")

# 📸 دریافت فیش
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in pending_users:
        photo = update.message.photo[-1].file_id

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=(
                f"💳 فیش جدید\n"
                f"👤 {user_id}\n"
                f"🌍 {user_country.get(user_id)}\n"
                f"📦 {user_plan.get(user_id)}\n\n"
                f"vpn:{user_id}|YOUR_VPN_LINK"
            )
        )

        await update.message.reply_text("✅ فیش ارسال شد")

    else:
        await update.message.reply_text("اول خرید کن 👇")

# 👨‍💻 پنل ادمین
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return

    text = update.message.text

    if text.startswith("vpn:"):
        try:
            uid, link = text.replace("vpn:", "").split("|")

            await context.bot.send_message(
                chat_id=int(uid),
                text=f"🎉 VPN شما آماده شد:\n\n🔐 {link}"
            )

            await update.message.reply_text("✅ ارسال شد")

        except:
            await update.message.reply_text("❌ فرمت اشتباهه")

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
