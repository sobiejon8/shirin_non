import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8253775904:AAHJxL6TvDmDr1stpFlMyVT4153FFiWcOWI"  # Bot tokeningiz
ADMIN_ID = 7565714864  # 👈 BU YERGA O'ZINGIZNING TELEGRAM ID RAQAMINGIZNI YOZING

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Render'dagi HTTPS WebApp manzilingiz
    web_app_url = "https://shirin-non.onrender.com"

    builder.button(
        text="🍞 Buyurtma berish",
        web_app=types.WebAppInfo(url=web_app_url)
    )

    await message.answer(
        "Assalomu alaykum! Shirin Non Sexi botiga xush kelibsiz.\n\n"
        "Buyurtma berish uchun pastdagi tugmani bosing:",
        reply_markup=builder.as_markup()
    )


# WebApp'dan kelgan ma'lumotni ushlab olish
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        # JSON ko'rinishidagi ma'lumotni o'qish
        raw_data = message.web_app_data.data
        data = json.loads(raw_data)

        # Admin uchun xabar matnini tuzish
        text = "🍞 **YANGI BUYURTMA KELDI!**\n\n"
        text += f"👤 **Mijoz:** {data.get('client_name')}\n"
        text += f"📞 **Tel:** {data.get('phone')}\n"
        text += f"⏰ **Vaqti:** {data.get('delivery_time')}\n\n"
        text += "📦 **Mahsulotlar:**\n"

        for item in data.get('items', []):
            text += f"• {item['name']} — {item['count']} ta ({item['sum']:,} so'm)\n"

        text += f"\n💰 **Jami summa:** {data.get('total_sum', 0):,} so'm"

        # 1. Mijozga javob xabari
        await message.answer("✅ Buyurtmangiz qabul qilindi! Rahmat.")

        # 2. Adminga (Sizga) xabar yuborish
        if ADMIN_ID:
            await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="Markdown")

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        await message.answer("❌ Buyurtmani qayta ishlashda xatolik bo'ldi.")