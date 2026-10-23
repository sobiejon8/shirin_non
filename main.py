import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List

BASE_DIR = Path(__file__).resolve().parent
from bot import bot, dp, ADMIN_ID

@asynccontextmanager
async def lifespan(app: FastAPI):
    polling_task = asyncio.create_task(dp.start_polling(bot))
    yield
    polling_task.cancel()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory=str(templates_dir))

# Pydantic orqali kelayotgan ma'lumotni tekshirish
class OrderItem(BaseModel):
    name: str
    count: int
    price: int
    sum: int

class OrderRequest(BaseModel):
    client_name: str
    phone: str
    delivery_time: str
    items: List[OrderItem]
    total_sum: int

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")

# Saytdan buyurtmani qabul qilib, adminga Telegram orqali yuboruvchi API
@app.post("/api/order")
async def create_order(order: OrderRequest):
    try:
        text = "🍞 <b>YANGI BUYURTMA KELDI! (Saytdan)</b>\n\n"
        text += f"👤 <b>Mijoz:</b> {order.client_name}\n"
        text += f"📞 <b>Tel:</b> {order.phone}\n"
        text += f"⏰ <b>Vaqti:</b> {order.delivery_time}\n\n"
        text += "📦 <b>Mahsulotlar:</b>\n"

        for item in order.items:
            text += f"• {item.name} — {item.count} ta ({item.sum:,} so'm)\n"

        text += f"\n💰 <b>Jami summa:</b> {order.total_sum:,} so'm"

        if ADMIN_ID:
            await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="HTML")
            print("Adminga muvaffaqiyatli xabar yuborildi!")

        return {"status": "success"}
    except Exception as e:
        print(f"API Order Xatolik: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)