import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8253775904:AAHJxL6TvDmDr1stpFlMyVT4153FFiWcOWI"
ADMIN_ID = 7565714864  # Sizning Telegram ID raqamingiz

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_order_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Qabul qildim", callback_data="status_accepted")
    builder.button(text="📦 Topshirdim (Pul olinmadi)", callback_data="status_unpaid")
    builder.button(text="💵 Pulni oldim", callback_data="status_paid")
    builder.adjust(1)  # Har bir tugma alohida qatorda turishi uchun
    return builder.as_markup()


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


# WebApp'dan kelgan ma'lumotni ushlab olish (agar hali ham ishlatilsa)
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        print("--- WEB_APP_DATA KELDI ---")
        raw_data = message.web_app_data.data
        print("Xom ma'lumot:", raw_data)

        data = json.loads(raw_data)

        # Admin uchun xabar matnini tuzish (HTML format xavfsizroq)
        text = "🍞 <b>YANGI BUYURTMA KELDI!</b>\n\n"
        text += f"👤 <b>Mijoz:</b> {data.get('client_name')}\n"
        text += f"📞 <b>Tel:</b> {data.get('phone')}\n"
        text += f"⏰ <b>Vaqti:</b> {data.get('delivery_time')}\n\n"
        text += "📦 <b>Mahsulotlar:</b>\n"

        for item in data.get('items', []):
            text += f"• {item['name']} — {item['count']} ta ({item['sum']:,} so'm)\n"

        text += f"\n💰 <b>Jami summa:</b> {data.get('total_sum', 0):,} so'm"
        text += f"\n\n📌 <b>Holati:</b> ⏳ Yangi buyurtma"

        # 1. Mijozga javob xabari
        await message.answer("✅ Buyurtmangiz qabul qilindi! Rahmat.")
        print("Mijozga javob yuborildi.")

        # 2. Adminga (Sizga) xabar yuborish
        if ADMIN_ID:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=text,
                parse_mode="HTML",
                reply_markup=get_order_keyboard()
            )
            print("Adminga muvaffaqiyatli xabar yuborildi!")

    except Exception as e:
        print(f"XATOLIK YUZ BERDI: {e}")
        await message.answer("❌ Buyurtmani qayta ishlashda xatolik bo'ldi.")


# Admin bosgan tugmalarga qarab xabar statusini o'zgartirish
@dp.callback_query(F.data.startswith("status_"))
async def handle_status_change(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    status_map = {
        "accepted": "✅ Qabul qilindi",
        "unpaid": "📦 Mahsulot topshirildi (Pul olinmadi)",
        "paid": "💵 Pulni oldim (Bajarildi)"
    }

    new_status = status_map.get(action, "Noma'lum")

    # Asl matnni o'qib, holatni yangilash
    original_text = callback.message.html_text

    if "📌 <b>Holati:</b>" in original_text:
        base_text = original_text.split("📌 <b>Holati:</b>")[0].strip()
    else:
        base_text = original_text.strip()

    updated_text = f"{base_text}\n\n📌 <b>Holati:</b> {new_status}"

    try:
        await callback.message.edit_text(
            updated_text,
            parse_mode="HTML",
            reply_markup=callback.message.reply_markup
        )
        await callback.answer(f"Status o'zgartirildi: {new_status}")
    except Exception as e:
        print(f"Statusni yangilashda xato: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(dp.start_polling(bot))