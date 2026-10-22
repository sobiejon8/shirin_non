import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

# bot.py faylingizdan bot va dp larni import qilamiz
from bot import bot, dp

@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI ishga tushganda bot pollingni orqa fonda yurgizish
    asyncio.create_task(dp.start_polling(bot))
    yield
    # Server to'xtaganda bot seansini yopish
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

# Statik fayllar va shablonlar
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)