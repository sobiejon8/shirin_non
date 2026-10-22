import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

# Loyiha ildiz papkasini aniqlash
BASE_DIR = Path(__file__).resolve().parent

# bot.py faylidan import
from bot import bot, dp

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bot pollingni orqa fonda yurgizish
    polling_task = asyncio.create_task(dp.start_polling(bot))
    yield
    # Server to'xtaganda bot seansini yopish
    polling_task.cancel()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

# Statik va Templates papkalarini ulash
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory=str(templates_dir))

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)