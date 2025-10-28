import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# Muhim sozlamalar
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CARD_NUMBER = os.getenv("CARD_NUMBER")

# Render uchun avtomatik sozlamalar
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("PORT", 10000))  # Render PORT muhit o‘zgaruvchisidan oladi
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # majburiy emas, agar berilmasa avtomatik aniqlanadi
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else None

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- /start ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = (
        "🇰🇷 *KAREAN SCHOOL — Boshlang‘ich va TOPIK 1 jonli darslari!*\n\n"
        "📅 *Dars kunlari:* Seshanba • Payshanba • Shanba\n"
        "🕒 Darslar jonli tarzda o‘tkaziladi (Zoom yoki Google Meet orqali)\n\n"
        "🎓 *Yo‘nalishlar:*\n"
        "🧩 Boshlang‘ich — Hangeul, talaffuz, kundalik so‘zlashuv\n"
        "📘 TOPIK 1 — Grammatikalar, so‘z boyligi va test tayyorgarlik\n\n"
        "💰 *Kurs narxi:* 200 000 so‘m / oy\n"
        "🎁 Chegirma — 150 000 so‘m (birinchi o‘quvchilar uchun)\n\n"
        "📲 Darsga yozilish uchun pastdagi tugmani bosing 👇"
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="✏️ Darsga yozilaman", callback_data="yozilish"))
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

# --- Foydalanuvchi yoziladi ---
@dp.callback_query_handler(Text(equals="yozilish"))
async def yozilish(callback_query: types.CallbackQuery):
    user = callback_query.from_user
    await bot.send_message(
        ADMIN_ID,
        f"📩 *Yangi o‘quvchi yozilmoqchi!*\n\n"
        f"👤 Ismi: {user.first_name}\n"
        f"🆔 Telegram ID: `{user.id}`\n\n"
        f"✅ Tasdiqlash uchun yuboring:\n`/tasdiqla_{user.id}`",
        parse_mode="Markdown"
    )
    await callback_query.message.answer(
        "✅ Arizangiz yuborildi! Tez orada admin siz bilan bog‘lanadi 🙌",
        parse_mode="Markdown"
    )

# --- Admin tasdiqlaydi ---
@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID and message.text.startswith("/tasdiqla_"))
async def tasdiqlash(message: types.Message):
    try:
        user_id = int(message.text.split("_")[1])
        await bot.send_message(
            user_id,
            f"✅ *Arizangiz tasdiqlandi!*\n\n"
            f"💳 To‘lov uchun karta raqami:\n`{CARD_NUMBER}`\n\n"
            f"📸 To‘lovni amalga oshirgach, skrinshotni shu yerga yuboring.",
            parse_mode="Markdown"
        )
        await message.reply("✅ Foydalanuvchiga karta raqam yuborildi.")
    except Exception as e:
        await message.reply(f"❌ Xatolik: foydalanuvchiga yuborib bo‘lmadi.\n{e}")

# --- Rasm yuborilganda ---
@dp.message_handler(content_types=["photo"])
async def rasm_qabul(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("✅ To‘lov qabul qilindi! Tez orada siz bilan bog‘lanamiz 🙌")
        await bot.send_message(
            ADMIN_ID,
            f"💰 *Yangi to‘lov skrinshoti keldi!*\n"
            f"👤 {message.from_user.first_name} (ID: {message.from_user.id})",
            parse_mode="Markdown"
        )
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id)

# --- Webhook funksiyalari ---
async def on_startup(dp):
    global WEBHOOK_URL
    if not WEBHOOK_URL:
        # Render domeni avtomatik aniqlanadi
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url:
            WEBHOOK_URL = f"{render_url}{WEBHOOK_PATH}"
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook o‘rnatildi: {WEBHOOK_URL}")

async def on_shutdown(dp):
    await bot.delete_webhook()
    print("🛑 Webhook o‘chirildi")

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
