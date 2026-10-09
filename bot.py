import asyncio
import logging
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from server import app
from handlers import start, audio, fragment

# Включаем логи aiogram — теперь увидим всё, что он делает
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(start.router)
dp.include_router(audio.router)
dp.include_router(fragment.router)


async def run_bot():
    print(">>> RUN_BOT START", flush=True)

    try:
        me = await bot.get_me()
        print(f">>> GET_ME OK: @{me.username} id={me.id}", flush=True)
    except Exception as e:
        print(f">>> GET_ME FAILED: {type(e).__name__}: {e}", flush=True)
        return

    print(">>> START_POLLING", flush=True)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f">>> POLLING CRASHED: {type(e).__name__}: {e}", flush=True)


async def run_server():
    print(">>> RUN_SERVER START", flush=True)
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    await uvicorn.Server(config).serve()


async def main():
    await asyncio.gather(run_bot(), run_server())


if __name__ == "__main__":
    asyncio.run(main())