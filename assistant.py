import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import requests
import json
import pyautogui
import time

# ---------- НАСТРОЙКИ GigaChat ----------
GIGACHAT_API_KEY = ""  # ВСТАВЬ СВОЙ КЛЮЧ
GIGACHAT_API_URL = "https://gigachat.api.url/chat"

# ---------- КООРДИНАТЫ ИКОНОК (НАСТРОЙ ПОД СВОЙ ЭКРАН) ----------
# Открой Paint или просто запомни, где на экране находятся иконки.
# Координаты (x, y) — это верхний левый угол иконки.
ICON_COORDS = {
    "calculator": (50, 100),
    "notepad": (50, 200),
    "painter": (50, 300),
    "snake": (50, 400),
    "sapper": (50, 500),
    "tetris": (50, 600),
    "music": (50, 700),
    "settings": (50, 800),
    "file_manager": (50, 900),
}

# ---------- ВКЛЮЧИТЬ АНИМАЦИЮ МЫШИ (True/False) ----------
ENABLE_MOUSE_ANIMATION = True

# ---------- ЛОКАЛЬНЫЕ КОМАНДЫ ----------
LOCAL_COMMANDS = {
    "калькулятор": "calculator",
    "кальк": "calculator",
    "открой калькулятор": "calculator",
    "хочу посчитать": "calculator",
    "блокнот": "notepad",
    "открой блокнот": "notepad",
    "записки": "notepad",
    "рисовалка": "painter",
    "открой рисовалку": "painter",
    "рисовать": "painter",
    "змейка": "snake",
    "открой змейку": "snake",
    "поиграть в змейку": "snake",
    "погирать": "snake",
    "играть в змейку": "snake",
    "запусти змейку": "snake",
    "сапёр": "sapper",
    "сапер": "sapper",
    "открой сапёр": "sapper",
    "тетрис": "tetris",
    "открой тетрис": "tetris",
    "музыка": "music",
    "плеер": "music",
    "открой музыку": "music",
    "настройки": "settings",
    "параметры": "settings",
    "файловый менеджер": "file_manager",
    "файлы": "file_manager",
    "проводник": "file_manager",
    "открой файлы": "file_manager"
}

# ---------- ФУНКЦИИ ПОИСКА КОМАНД ----------
def get_app_from_local(text):
    text_lower = text.lower()
    for phrase, app in LOCAL_COMMANDS.items():
        if phrase in text_lower:
            return app
    return None

def get_app_from_gigachat(user_text):
    if not GIGACHAT_API_KEY:
        return None
    headers = {
        "Authorization": f"Bearer {GIGACHAT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": "Ты — помощник в ОС. Отвечай только одним словом: calculator, notepad, painter, snake, tetris, sapper, music, settings, file_manager или unknown."},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.1
    }
    try:
        response = requests.post(GIGACHAT_API_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip().lower()
    except Exception:
        pass
    return None

# ---------- АНИМАЦИЯ МЫШИ ----------
def move_mouse_to_icon(app_name):
    """Плавно двигает мышь к иконке приложения и кликает."""
    if not ENABLE_MOUSE_ANIMATION:
        return
    if app_name not in ICON_COORDS:
        print(f"⚠️ Координаты для {app_name} не заданы")
        return
    x, y = ICON_COORDS[app_name]
    try:
        # Плавное движение (0.5 секунды)
        pyautogui.moveTo(x, y, duration=0.5)
        # Клик
        pyautogui.click()
        time.sleep(0.2)  # небольшая пауза после клика
    except Exception as e:
        print(f"⚠️ Ошибка анимации мыши: {e}")

# ---------- ОТКРЫТИЕ ПРИЛОЖЕНИЙ ----------
def open_app(app_name, master, taskbar):
    # Сначала анимация мыши
    move_mouse_to_icon(app_name)

    if app_name == "calculator":
        from calculator import Calculator
        Calculator(master, taskbar)
        return "🧮 Открываю калькулятор"
    elif app_name == "notepad":
        from notepad import Notepad
        Notepad(master, taskbar)
        return "📝 Открываю блокнот"
    elif app_name == "painter":
        from painter import Painter
        Painter(master, taskbar)
        return "🎨 Открываю рисовалку"
    elif app_name == "snake":
        from snake import SnakeGame
        SnakeGame(master, taskbar)
        return "🐍 Запускаю змейку"
    elif app_name == "sapper":
        from sapper import Sapper
        Sapper(master, taskbar)
        return "💣 Запускаю сапёра"
    elif app_name == "tetris":
        from tetris import Tetris
        Tetris(master, taskbar)
        return "🧩 Запускаю тетрис"
    elif app_name == "music":
        from music_player import MusicPlayer
        MusicPlayer(master, taskbar)
        return "🎵 Открываю музыкальный плеер"
    elif app_name == "settings":
        from settings import SettingsWindow
        SettingsWindow(master, taskbar, lambda: None)
        return "⚙️ Открываю настройки"
    elif app_name == "file_manager":
        from file_manager import FileManager
        FileManager(master, taskbar)
        return "📁 Открываю файловый менеджер"
    else:
        return "🤔 Не понял команду"

# ---------- ОКНО АССИСТЕНТА ----------
def start_assistant(parent, master, taskbar):
    win = tk.Toplevel(parent)
    win.title("Голосовой помощник")
    win.geometry("500x450")
    win.resizable(False, False)

    tk.Label(win, text="Голосовой помощник (с анимацией мыши)", font=("Arial", 14)).pack(pady=10)

    chat_area = scrolledtext.ScrolledText(win, wrap=tk.WORD, height=12, font=("Arial", 10))
    chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    chat_area.insert(tk.END, "👋 Привет! Напиши или скажи команду.\n")
    chat_area.config(state=tk.DISABLED)

    input_frame = tk.Frame(win)
    input_frame.pack(fill=tk.X, padx=10, pady=5)

    entry = tk.Entry(input_frame, font=("Arial", 12))
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    entry.bind("<Return>", lambda e: send_text())

    def add_message(sender, text):
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, f"{sender}: {text}\n")
        chat_area.see(tk.END)
        chat_area.config(state=tk.DISABLED)

    def process_command(text):
        app = get_app_from_local(text)
        if app is None:
            app = get_app_from_gigachat(text)
        if app is None or app == "unknown":
            reply = "🤔 Не понял команду."
        else:
            reply = open_app(app, master, taskbar)
        add_message("🤖", reply)

    def send_text():
        text = entry.get().strip()
        if not text:
            return
        entry.delete(0, tk.END)
        add_message("👤", text)
        threading.Thread(target=process_command, args=(text,), daemon=True).start()

    def voice_input():
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                add_message("🎤", "Слушаю...")
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = recognizer.recognize_google(audio, language="ru-RU")
                    add_message("👤", text)
                    threading.Thread(target=process_command, args=(text,), daemon=True).start()
                except Exception as e:
                    add_message("⚠️", f"Ошибка: {e}")
        except ImportError:
            messagebox.showerror("Ошибка", "Установи: pip install SpeechRecognition")
        except Exception as e:
            add_message("⚠️", f"Ошибка микрофона: {e}")

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="Отправить", command=send_text, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="🎤 Голос", command=voice_input, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Очистить", command=lambda: chat_area.config(state=tk.NORMAL) or chat_area.delete(1.0, tk.END) or chat_area.config(state=tk.DISABLED), bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)

    def on_close():
        win.destroy()
    win.protocol("WM_DELETE_WINDOW", on_close)
    entry.focus()