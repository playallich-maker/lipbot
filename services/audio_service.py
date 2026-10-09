from pydub import AudioSegment

def get_duration(path: str) -> int:
    """Возвращает длительность аудио в секундах"""
    audio = AudioSegment.from_file(path)
    return int(len(audio) / 1000)


def cut_audio(src: str, dst: str, start: int, end: int):
    """Вырезает кусок аудио с start по end секунду"""
    audio = AudioSegment.from_file(src)
    fragment = audio[start * 1000 : end * 1000]
    fragment.export(dst, format="mp3")