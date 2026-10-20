import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import SessionLocal
from models import Order

BOT_TOKEN = os.getenv("BOT_TOKEN", "8253775904:AAHJxL6TvDmDr1stpFlMyVT4153FFiWcOWI")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "7565714864")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_order_keyboard(order_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Qabul qilindi", callback_data=f"status:{order_id}:🟢 Qabul qilindi"),
            InlineKeyboardButton(text="🍞 Yopilmoqda", callback_data=f"status:{order_id}:🍞 Yopilmoqda")
        ],
        [
            InlineKeyboardButton(text="🚚 Yo'lda", callback_data=f"status:{order_id}:🚚 Yo'lda"),
            InlineKeyboardButton(text="✅ Topshirildi", callback_data=f"status:{order_id}:✅ Topshirildi")
        ]
    ])


@dp.callback_query(F.data.startswith("status:"))
async def process_status_change(callback: types.CallbackQuery):
    _, order_id, new_status = callback.data.split(":")

    db = SessionLocal()
    order = db.query(Order).filter(Order.id == int(order_id)).first()
    if order:
        order.status = new_status
        db.commit()

        text_lines = callback.message.text.split("\n")
        updated_text = []
        for line in text_lines:
            if line.startswith("Status:"):
                updated_text.append(f"Status: {new_status}")
            else:
                updated_text.append(line)

        await callback.message.edit_text("\n".join(updated_text), reply_markup=get_order_keyboard(int(order_id)))
        await callback.answer(f"Status '{new_status}'ga o'zgartirildi!")
    else:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
    db.close()