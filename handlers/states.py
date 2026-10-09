from aiogram.fsm.state import State, StatesGroup

class LipSync(StatesGroup):
    waiting_audio = State()       # ждём mp3
    choosing_fragment = State()   # выбирает фрагмент
    waiting_video = State()       # ждёт кружок из Mini App