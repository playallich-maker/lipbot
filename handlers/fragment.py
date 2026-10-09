from aiogram import Router
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
)
from aiogram.fsm.context import FSMContext
from .states import LipSync
from config import WEBAPP_URL

router = Router()

@router.message(LipSync.choosing_fragment)
async def handle_fragment(message: Message, state: FSMContext):
    # Просто показываем кнопку — выбор фрагмента происходит в Mini App
    webapp_url = f"{WEBAPP_URL}/?user_id={message.from_user.id}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="🎵 Выбрать фрагмент на волне",
            web_app=WebAppInfo(url=webapp_url)
        )
    ]])
    await message.answer(
        "Открой Mini App: увидишь волну.\n"
        "Выдели фрагмент перетаскиванием, затем нажми «Продолжить» → «Записать кружок».",
        reply_markup=kb
    )
    await state.set_state(LipSync.waiting_video)