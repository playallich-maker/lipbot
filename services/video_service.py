import asyncio
import os

async def make_video_note(video_path: str, audio_path: str, out_path: str) -> bool:
    """
    Делает из обычного видео кружок 240x240 с оригинальной музыкой.
    Ключевое: -map 0:v:0 — берём видео, -map 1:a:0 — берём аудио,
    тем самым полностью выкидываем звук с микрофона.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,       # вход 1: сырое видео из Mini App
        "-i", audio_path,       # вход 2: фрагмент музыки
        "-vf", (
            "crop='min(iw,ih)':'min(iw,ih)',"
            "scale=240:240:force_original_aspect_ratio=decrease,"
            "pad=240:240:(ow-iw)/2:(oh-ih)/2:color=black"
        ),
        "-map", "0:v:0",        # видео из 1-го входа
        "-map", "1:a:0",        # аудио из 2-го входа (микрофон игнорируется)
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-t", "60",
        "-movflags", "+faststart",
        out_path
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await proc.wait()
    return proc.returncode == 0