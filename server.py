from fastapi import FastAPI, UploadFile, Form, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import aiofiles, os
from aiogram import Bot
from aiogram.types import FSInputFile

from config import BOT_TOKEN
from services.audio_service import get_duration, cut_audio
from services.video_service import make_video_note

bot = Bot(BOT_TOKEN)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/audio/{user_id}")
async def get_audio(user_id: int):
    """Отдаём полный аудиофайл для отображения волны"""
    path = f"storage/audio/{user_id}_original.mp3"
    if not os.path.exists(path):
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(path, media_type="audio/mpeg")


@app.get("/fragment/{user_id}")
async def get_fragment(user_id: int):
    """Отдаём выбранный фрагмент для проигрывания"""
    path = f"storage/audio/{user_id}_fragment.mp3"
    if not os.path.exists(path):
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(path, media_type="audio/mpeg")


@app.post("/select-fragment")
async def select_fragment(data: dict):
    """Принимает выделенный фрагмент, вырезает и сохраняет"""
    user_id = data["user_id"]
    start = int(data["start"])
    end = int(data["end"])

    src = f"storage/audio/{user_id}_original.mp3"
    dst = f"storage/audio/{user_id}_fragment.mp3"

    if not os.path.exists(src):
        return {"ok": False, "error": "Audio not found"}

    cut_audio(src, dst, start, end)
    duration = end - start

    return {"ok": True, "duration": duration}


@app.post("/upload")
async def upload(
    video: UploadFile = File(...),
    user_id: str = Form(...),
    init_data: str = Form(...),
):
    uid = int(user_id)
    os.makedirs("storage/uploads", exist_ok=True)
    raw_path = f"storage/uploads/{uid}_raw.webm"

    async with aiofiles.open(raw_path, "wb") as f:
        await f.write(await video.read())

    # Оригинальное аудио + видео → кружок
    audio_path = f"storage/audio/{uid}_fragment.mp3"
    out_path = f"storage/notes/{uid}_note.mp4"
    os.makedirs("storage/notes", exist_ok=True)

    success = await make_video_note(raw_path, audio_path, out_path)
    if not success:
        return JSONResponse({"ok": False, "error": "FFmpeg failed"})

    # Отправляем кружок
    try:
        await bot.send_video_note(
            chat_id=uid,
            video_note=FSInputFile(out_path),
        )
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})

    # Чистим все временные файлы
    for p in [raw_path, out_path, audio_path,
              f"storage/audio/{uid}_original.mp3"]:
        if os.path.exists(p):
            os.remove(p)

    return {"ok": True}