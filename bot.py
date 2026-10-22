import json
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart

BOT_TOKEN = "8253775904:AAHJxL6TvDmDr1stpFlMyVT4153FFiWcOWI"  # Bu yerga bot tokeningiz
ADMIN_ID = 7565714864  # 👈 BU YERGA O'ZINGIZNING TELEGRAM ID'INGIZNI YOZING

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Xush kelibsiz! WebApp orqali buyurtma berishingiz mumkin.")


@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)

        # Buyurtma matnini shakllantirish
        text = f"🍞 **YANGI BUYURTMA!**\n\n"
        text += f"👤 **Mijoz / Do'kon:** {data.get('client_name')}\n"
        text += f"📞 **Telefon:** {data.get('phone')}\n"
        text += f"⏰ **Yetkazish vaqti:** {data.get('delivery_time')}\n\n"
        text += "📦 **Buyurtma qilingan mahsulotlar:**\n"

        for item in data.get('items', []):
            text += f"• {item['name']} — {item['count']} ta ({item['sum']:,} so'm)\n"

        text += f"\n💰 **Jami summa:** {data.get('total_sum', 0):,} so'm"

        # 1. Mijozning o'ziga tasdiqlash xabarini yuborish
        await message.answer(f"✅ **Buyurtmangiz qabul qilindi!**\n\n{text}")

        # 2. XADMIN'GA (Sizga) Telegram orqali xabar yuborish 🚀
        if ADMIN_ID and ADMIN_ID != 123456789:
            await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="Markdown")

    except Exception as e:
        await message.answer("Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(dp.start_polling(bot))