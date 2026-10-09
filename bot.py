import asyncio
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from server import app
from handlers import start, audio, fragment

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(start.router)
dp.include_router(audio.router)
dp.include_router(fragment.router)


async def run_bot():
    print("Бот запущен")
    await dp.start_polling(bot)


async def run_server():
    print("Сервер запущен на порту 8000")
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    await uvicorn.Server(config).serve()


async def main():
    await asyncio.gather(run_bot(), run_server())


if __name__ == "__main__":
    asyncio.run(main())