from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .states import LipSync

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я делаю липсинги в кружках.\n\n"
        "1️⃣ Отправь мне музыку (mp3)\n"
        "2️⃣ Выбери фрагмент на волне\n"
        "3️⃣ Запиши кружок в Mini App\n"
        "4️⃣ Получи готовый кружок 🎶\n\n"
        "Давай начнём — пришли аудиофайл."
    )
    await state.set_state(LipSync.waiting_audio)