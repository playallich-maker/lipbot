import os
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .states import LipSync
from services.audio_service import get_duration

router = Router()

@router.message(LipSync.waiting_audio, F.audio | F.document)
async def handle_audio(message: Message, state: FSMContext, bot):
    file_id = message.audio.file_id if message.audio else message.document.file_id
    file = await bot.get_file(file_id)
    os.makedirs("storage/audio", exist_ok=True)
    path = f"storage/audio/{message.from_user.id}_original.mp3"
    await bot.download_file(file.file_path, path)

    # ОТЛАДКА
    print(f">>> SAVED: {path}", flush=True)
    print(f">>> CWD: {os.getcwd()}", flush=True)
    print(f">>> EXISTS: {os.path.exists(path)}", flush=True)
    print(f">>> SIZE: {os.path.getsize(path) if os.path.exists(path) else 0}", flush=True)
    print(f">>> LS storage/audio: {os.listdir('storage/audio')}", flush=True)

    duration = get_duration(path)
    await state.update_data(audio_path=path, duration=duration)

    await message.answer(
        f"🎵 Трек получен! Длительность: <b>{duration} сек</b>.\n\n"
        f"Открой Mini App для выбора фрагмента — увидишь волну.",
        parse_mode="HTML"
    )
    await state.set_state(LipSync.choosing_fragment)