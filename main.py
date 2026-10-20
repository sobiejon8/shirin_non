import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import engine, Base, get_db
import models
from bot import bot, dp, ADMIN_CHAT_ID, get_order_keyboard

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_name: str
    phone_number: str
    requested_time: str
    items: List[OrderItemCreate]


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    if not products:
        sample_products = [
            models.Product(
                title="Borka (katta)",
                price=3000,
                image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300"
            ),
            models.Product(
                title="Kichik borka",
                price=2800,
                image_url="https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=300"
            ),
            models.Product(
                title="Kekis (1 salafan)",
                price=15000,
                image_url="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300"
            ),
            models.Product(
                title="Qora borka noni",
                price=7000,
                image_url="https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=300"
            ),
        ]
        db.add_all(sample_products)
        db.commit()
        products = db.query(models.Product).all()
    return products
@app.post("/api/orders")
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    new_order = models.Order(
        customer_name=order_data.customer_name,
        phone_number=order_data.phone_number,
        requested_time=order_data.requested_time,
        status="🟡 Kutilmoqda"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    total_sum = 0
    items_text = []

    for item in order_data.items:
        prod = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if prod:
            item_price = prod.price * item.quantity
            total_sum += item_price

            order_item = models.OrderItem(
                order_id=new_order.id,
                product_name=prod.title,
                quantity=item.quantity,
                price=prod.price
            )
            db.add(order_item)
            items_text.append(f"• {prod.title}: {item.quantity} dona x {int(prod.price):,} = {int(item_price):,} so'm")

    db.commit()

    message_text = (
            f"🔔 **Yangi buyurtma!**\n\n"
            f"**Mijoz:** {new_order.customer_name} ({new_order.phone_number})\n"
            f"**Kerakli vaqt:** Soat {new_order.requested_time} gacha\n\n"
            f"**Mahsulotlar:**\n" + "\n".join(items_text) + "\n\n"
                                                            f"**Jami summa:** {int(total_sum):,} so'm\n"
                                                            f"**Status:** {new_order.status}"
    )

    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message_text,
            reply_markup=get_order_keyboard(new_order.id),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Botga xabar yuborishda xatolik: {e}")

    return {"status": "success", "order_id": new_order.id}


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(dp.start_polling(bot))