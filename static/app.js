// ============================================================
// Telegram Mini App для липсингов в кружках
// Файл: static/app.js
// Содержит: выбор фрагмента на волне + запись видео с музыкой
// ============================================================

const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
tg.disableVerticalSwipes();

const params = new URLSearchParams(window.location.search);
const userId = params.get("user_id");

console.log("USER ID:", userId);
console.log("FULL URL:", window.location.href); // ← добавь эту строку для отладки

// Элементы интерфейса
const waveScreen = document.getElementById("waveScreen");
const recordScreen = document.getElementById("recordScreen");
const regionInfo = document.getElementById("regionInfo");

// ============================================================
// ЧАСТЬ 1: ВЫБОР ФРАГМЕНТА НА ВОЛНЕ
// ============================================================

let selectedStart = 0;
let selectedEnd = 0;
let wavesurfer;

// Инициализация волны через wavesurfer.js
async function initWaveform() {
  wavesurfer = WaveSurfer.create({
    container: "#waveform",
    waveColor: "#666",
    progressColor: "#ff3b30",
    height: 100,
    normalize: true,
  });

  // Подключаем плагин regions — выделение фрагмента перетаскиванием
  const regionsPlugin = wavesurfer.registerPlugin(WaveSurfer.Regions.create());

  // Загружаем полный аудиофайл пользователя
  wavesurfer.load(`/audio/${userId}`);

  wavesurfer.on("ready", () => {
    // Разрешаем пользователю выделить область перетаскиванием
    regionsPlugin.enableDragSelection({
      color: "rgba(255, 59, 48, 0.3)",
    });
    regionInfo.textContent = "Выдели фрагмент на волне";
  });

  // Когда пользователь закончил выделение — сохраняем границы
  regionsPlugin.on("region-created", (region) => {
    selectedStart = region.start;
    selectedEnd = region.end;
    regionInfo.textContent =
      `Выбрано: ${formatTime(selectedStart)} – ${formatTime(selectedEnd)}`;
  });
}

// Форматирование секунд в "M:SS"
function formatTime(sec) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

// Прослушать выделенный фрагмент
document.getElementById("playRegionBtn").onclick = () => {
  if (selectedEnd > selectedStart) {
    wavesurfer.play(selectedStart, selectedEnd);
  }
};

// Подтвердить фрагмент → перейти к записи
document.getElementById("confirmRegionBtn").onclick = async () => {
  if (selectedEnd <= selectedStart) {
    regionInfo.textContent = "⚠️ Сначала выдели фрагмент";
    return;
  }

  // Говорим серверу, какой фрагмент вырезать
  const res = await fetch("/select-fragment", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      start: selectedStart,
      end: selectedEnd,
    }),
  }).then((r) => r.json());

  if (!res.ok) {
    regionInfo.textContent = "❌ Ошибка: " + res.error;
    return;
  }

  // Переключаемся на экран записи
  waveScreen.style.display = "none";
  recordScreen.style.display = "flex";
  await initRecording(res.duration);
};

// Запускаем загрузку волны
initWaveform().catch((err) => {
  regionInfo.textContent = "Ошибка загрузки волны: " + err.message;
});

// ============================================================
// ЧАСТЬ 2: ЗАПИСЬ ВИДЕО С МУЗЫКОЙ
// ============================================================

const videoEl = document.getElementById("preview");
const musicEl = document.getElementById("music");
const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const statusEl = document.getElementById("status");
const progressBar = document.getElementById("progressBar");

let stream, mediaRecorder, chunks = [];
let fragmentDuration = 0;

// Инициализация записи: музыка + камера (без микрофона)
async function initRecording(duration) {
  fragmentDuration = duration;

  // Загружаем фрагмент музыки
  musicEl.src = `/fragment/${userId}?t=${Date.now()}`;
  await musicEl.load();

  // Запрашиваем камеру (audio: false — микрофон не пишем)
  stream = await navigator.mediaDevices.getUserMedia({
    video: {
      width: { ideal: 480 },
      height: { ideal: 480 },
      facingMode: "user",
      frameRate: { ideal: 30 },
    },
    audio: false, // микрофон не пишем, звук наложит сервер
  });
  videoEl.srcObject = stream;
}

// Определяем поддерживаемый формат записи (iOS Safari не умеет webm)
function pickMimeType() {
  const types = [
    "video/mp4;codecs=h264", // приоритет для iOS
    "video/webm;codecs=h264",
    "video/webm;codecs=vp8",
    "video/webm",
  ];
  for (const t of types) {
    if (MediaRecorder.isTypeSupported(t)) return t;
  }
  return "";
}

// Старт записи
recordBtn.onclick = async () => {
  chunks = [];
  const mimeType = pickMimeType();

  mediaRecorder = new MediaRecorder(stream, {
    mimeType,
    videoBitsPerSecond: 2_000_000,
  });

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) chunks.push(e.data);
  };
  mediaRecorder.onstop = uploadRecording;

  // Одновременный старт музыки и записи
  musicEl.currentTime = 0;
  await musicEl.play();

  // iOS-фикс: сбрасываем данные каждые 100 мс, иначе blob может быть пустым
  mediaRecorder.start(100);

  recordBtn.style.display = "none";
  stopBtn.style.display = "block";
  statusEl.textContent = "🔴 Запись... Слушай музыку!";

  // Прогресс-бар и авто-стоп по длительности фрагмента
  const startTime = Date.now();
  const timer = setInterval(() => {
    const elapsed = (Date.now() - startTime) / 1000;
    progressBar.style.width =
      Math.min(100, (elapsed / fragmentDuration) * 100) + "%";
    if (elapsed >= fragmentDuration + 0.5) {
      clearInterval(timer);
      stopRecording();
    }
  }, 100);

  mediaRecorder._timer = timer;
};

// Стоп записи
function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    musicEl.pause();
    clearInterval(mediaRecorder._timer);
    stopBtn.style.display = "none";
    statusEl.textContent = "⏳ Отправка...";
  }
}
stopBtn.onclick = stopRecording;

// Загрузка готового видео на сервер
async function uploadRecording() {
  const blob = new Blob(chunks, { type: mediaRecorder.mimeType });

  const formData = new FormData();
  formData.append("video", blob, "recording.webm");
  formData.append("user_id", userId);
  formData.append("init_data", tg.initData); // для проверки подлинности

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (data.ok) {
      statusEl.textContent = "✅ Готово! Кружок отправлен в чат.";
      tg.close();
    } else {
      statusEl.textContent = "❌ Ошибка: " + data.error;
    }
  } catch (e) {
    statusEl.textContent = "❌ Ошибка сети";
  }
}