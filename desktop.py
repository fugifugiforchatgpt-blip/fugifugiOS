# desktop.py
import tkinter as tk
from calculator import Calculator
from notepad import Notepad
from file_manager import FileManager
from settings import SettingsWindow
from painter import Painter
from snake import SnakeGame
from gigachat_assistant import GigaChatAssistant
from sapper import Sapper
from tetris import Tetris
from music_player import MusicPlayer
from task_manager import TaskManager
from sentiment_app import SentimentApp
from antivirus import AntivirusApp
from ffgpt_full import FFChat
from assistant import start_assistant
from theme_utils import (
    load_settings, save_settings, get_theme, set_theme,
    get_bg_color, is_neon_mode, get_neon_theme, NEON_COLORS
)
from browser import BrowserApp  # <--- ДОБАВЛЕНО
import json
import os
import subprocess
import sys
import os

def open_browser():
    script_path = os.path.join(os.path.dirname(__file__), "browser.py")
    subprocess.Popen([sys.executable, script_path])

# ---------- ФУНКЦИЯ ПРИМЕНЕНИЯ ТЕМЫ ----------
def change_bg(master, taskbar):
    settings = load_settings()
    theme = settings.get("theme", "light")
    custom_color = settings.get("bg_color", "lightblue")
    neon_mode = settings.get("neon_mode", False)
    neon_color_name = settings.get("neon_color", "Розовый")

    if neon_mode:
        neon = get_neon_theme(neon_color_name)
        bg_color = neon["bg"]
        taskbar_bg = neon["taskbar"]
        btn_bg = neon["button"]
        btn_fg = neon["fg"]
        fg_color = neon["fg"]

        master.configure(bg=bg_color)
        for child in master.winfo_children():
            if isinstance(child, tk.Frame) and child != taskbar.frame:
                try:
                    child.configure(bg=bg_color)
                except:
                    pass
                for grand in child.winfo_children():
                    try:
                        grand.configure(bg=bg_color, fg=fg_color)
                    except tk.TclError:
                        try:
                            grand.configure(bg=bg_color)
                        except:
                            pass
        taskbar.frame.configure(bg=taskbar_bg)
        taskbar.start_btn.configure(bg=btn_bg, fg=btn_fg, font=("Arial", 10, "bold"))
        for btn in taskbar.buttons_frame.winfo_children():
            btn.configure(bg=btn_bg, fg=btn_fg)
        taskbar.clock_label.configure(bg=taskbar_bg, fg=fg_color)
    else:
        if theme == "dark":
            bg_color = "#2b2b2b"
            taskbar_bg = "#1e1e1e"
            btn_bg = "#4a4a4a"
            btn_fg = "white"
            fg_color = "white"
        else:
            bg_color = custom_color
            taskbar_bg = "darkgray"
            btn_bg = "lightgray"
            btn_fg = "black"
            fg_color = "black"
        master.configure(bg=bg_color)
        for child in master.winfo_children():
            if isinstance(child, tk.Frame) and child != taskbar.frame:
                try:
                    child.configure(bg=bg_color)
                except:
                    pass
                for grand in child.winfo_children():
                    try:
                        grand.configure(bg=bg_color, fg=fg_color)
                    except tk.TclError:
                        try:
                            grand.configure(bg=bg_color)
                        except:
                            pass
        taskbar.frame.configure(bg=taskbar_bg)
        taskbar.start_btn.configure(bg=btn_bg, fg=btn_fg, font=("Arial", 10))
        for btn in taskbar.buttons_frame.winfo_children():
            btn.configure(bg=btn_bg, fg=btn_fg)
        taskbar.clock_label.configure(bg=taskbar_bg, fg=btn_fg)

# ---------- ПАНЕЛЬ ЗАДАЧ ----------
class Taskbar:
    def __init__(self, master, show_start_menu_callback):
        self.master = master
        self.frame = tk.Frame(master, height=40)
        self.frame.pack(side="bottom", fill="x")

        self.start_btn = tk.Button(self.frame, text="Пуск", font=("Arial", 10),
                                   command=show_start_menu_callback)
        self.start_btn.pack(side="left", padx=5, pady=5)

        self.buttons_frame = tk.Frame(self.frame)
        self.buttons_frame.pack(side="left", fill="x", expand=True, padx=5)

        self.clock_label = tk.Label(self.frame, font=("Arial", 10))
        self.clock_label.pack(side="right", padx=5, pady=5)
        self.update_clock()
        self.clock_label.bind("<Button-1>", self.show_calendar)

        self.window_buttons = {}
        self._after_id = None

        # Привязка событий для драйверов (мышь, клавиатура)
        self.master.bind("<Motion>", self.on_mouse_move)
        self.master.bind("<ButtonPress>", self.on_mouse_click)
        self.master.bind("<KeyPress>", self.on_key_press)
        self.master.bind("<KeyRelease>", self.on_key_release)
        self.last_x, self.last_y = 0, 0
        from drivers import get_driver_manager
        self.driver_manager = get_driver_manager()

        change_bg(master, self)

    # ---------- Обработчики с драйверами ----------
    def on_mouse_move(self, event):
        raw = {
            "x": event.x,
            "y": event.y,
            "dx": event.x - self.last_x,
            "dy": event.y - self.last_y,
            "buttons": 0,
        }
        self.last_x, self.last_y = event.x, event.y
        processed = self.driver_manager.process_input("mouse", raw)
        if processed:
            # можно передать в активное окно, но пока просто логируем
            pass

    def on_mouse_click(self, event):
        raw = {"x": event.x, "y": event.y, "buttons": event.num, "dx": 0, "dy": 0}
        processed = self.driver_manager.process_input("mouse", raw)
        if processed:
            pass

    def on_key_press(self, event):
        raw = {"key": event.keysym, "modifiers": event.state, "pressed": True}
        processed = self.driver_manager.process_input("keyboard", raw)
        if processed is None:
            return "break"

    def on_key_release(self, event):
        raw = {"key": event.keysym, "modifiers": event.state, "pressed": False}
        processed = self.driver_manager.process_input("keyboard", raw)
        if processed is None:
            return "break"

    # ---------- Остальные методы Taskbar ----------
    def update_clock(self):
        from time import strftime
        if self.clock_label.winfo_exists():
            self.clock_label.config(text=strftime("%H:%M:%S"))
            self._after_id = self.master.after(1000, self.update_clock)

    def cancel_clock(self):
        if self._after_id:
            self.master.after_cancel(self._after_id)
            self._after_id = None

    def add_window(self, window, title):
        btn = tk.Button(self.buttons_frame, text=title, font=("Arial", 9),
                        command=lambda: self.raise_window(window))
        btn.pack(side="left", padx=2, pady=2)
        self.window_buttons[window] = btn

        if is_neon_mode():
            neon = get_neon_theme(load_settings().get("neon_color", "Розовый"))
            btn.configure(bg=neon["button"], fg=neon["fg"])

        def on_close():
            self.remove_window(window)
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_close)

    def remove_window(self, window):
        if window in self.window_buttons:
            self.window_buttons[window].destroy()
            del self.window_buttons[window]

    def raise_window(self, window):
        try:
            if window.state() == "iconic":
                window.deiconify()
            window.lift()
            window.focus_force()
        except:
            self.remove_window(window)

    def collect_session(self):
        session_data = []
        for win in list(self.window_buttons.keys()):
            try:
                if win.winfo_exists():
                    title = win.title()
                    if "Калькулятор" in title:
                        session_data.append("Calculator")
                    elif "Блокнот" in title:
                        session_data.append("Notepad")
                    elif "Файловый менеджер" in title:
                        session_data.append("FileManager")
                    elif "Рисовалка" in title:
                        session_data.append("Painter")
                    elif "Параметры" in title:
                        session_data.append("SettingsWindow")
                    elif "Змейка" in title:
                        session_data.append("SnakeGame")
                    elif "Сапёр" in title:
                        session_data.append("Sapper")
                    elif "Тетрис" in title:
                        session_data.append("Tetris")
                    elif "Музыкальный плеер" in title:
                        session_data.append("MusicPlayer")
                    elif "Ассистент" in title:
                        session_data.append("GigaChatAssistant")
                    elif "Фуги Фуги ИИ" in title:
                        session_data.append("SentimentApp")
                    elif "Очистка системы" in title:
                        session_data.append("AntivirusApp")
                    elif "ФФGPT" in title:
                        session_data.append("FFChat")
                    elif "Диспетчер задач" in title:
                        session_data.append("TaskManager")
                    elif "Голосовой помощник" in title:
                        session_data.append("Assistant")
                    elif "FugiFugi Browser" in title:
                        session_data.append("BrowserApp")
            except:
                continue
        return session_data

    def save_session(self):
        session = self.collect_session()
        with open("session.json", "w") as f:
            json.dump(session, f)

    def load_session(self):
        if os.path.exists("session.json"):
            try:
                with open("session.json", "r") as f:
                    return json.load(f)
            except:
                pass
        return []

    def clear_session_file(self):
        if os.path.exists("session.json"):
            os.remove("session.json")

    def close_all_windows(self, save=False):
        if save:
            self.save_session()
        else:
            self.clear_session_file()
        for win in list(self.window_buttons.keys()):
            try:
                win.destroy()
            except:
                pass

    def show_calendar(self, event):
        try:
            from calendar_popup import CalendarPopup
            x = event.x_root
            y = event.y_root + 25
            CalendarPopup(self.master, x, y)
        except Exception as e:
            print("Ошибка календаря:", e)

# ---------- ДИАЛОГ ВЫХОДА ----------
class ExitDialog:
    def __init__(self, master, taskbar):
        self.master = master
        self.taskbar = taskbar
        self.window = tk.Toplevel(master)
        self.window.transient(master)
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        self.window.title("Завершение работы")
        self.window.geometry("350x200")
        self.window.resizable(False, False)
        self.window.configure(bg="lightgray")
        tk.Label(self.window, text="Выберите действие:", font=("Arial", 12), bg="lightgray").pack(pady=10)
        btn_frame = tk.Frame(self.window, bg="lightgray")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Закрыть все приложения и выйти", command=self.shutdown_no_save,
                  bg="#ff8888", width=30).pack(pady=5)
        tk.Button(btn_frame, text="Сохранить открытые приложения и выйти", command=self.shutdown_save,
                  bg="#88ff88", width=30).pack(pady=5)
        tk.Button(btn_frame, text="Отмена", command=self.cancel).pack(pady=5)

    def shutdown_no_save(self):
        self.taskbar.close_all_windows(save=False)
        self.master.quit()

    def shutdown_save(self):
        self.taskbar.close_all_windows(save=True)
        self.master.quit()

    def cancel(self):
        self.window.destroy()

# ---------- МЕНЮ ПУСК ----------
class StartMenu:
    def __init__(self, master, x, y, taskbar):
        self.window = tk.Toplevel(master)
        self.window.transient(master)
        self.window.lift()
        self.window.focus_force()
        self.window.overrideredirect(True)
        self.window.geometry(f"260x560+{x}+{y - 560}")

        settings = load_settings()
        neon_mode = settings.get("neon_mode", False)
        if neon_mode:
            neon = get_neon_theme(settings.get("neon_color", "Розовый"))
            bg = neon["bg"]
            btn_bg = neon["button"]
            fg = neon["fg"]
        elif settings.get("theme", "light") == "dark":
            bg = "#3c3c3c"
            btn_bg = "#4a4a4a"
            fg = "white"
        else:
            bg = "lightgray"
            btn_bg = "lightgray"
            fg = "black"
        self.window.configure(bg=bg)

        apps = [
            ("🧮 Калькулятор", lambda: Calculator(master, taskbar)),
            ("📝 Блокнот", lambda: Notepad(master, taskbar)),
            ("📁 Файловый менеджер", lambda: FileManager(master, taskbar)),
            ("🎨 Рисовалка", lambda: Painter(master, taskbar)),
            ("🐍 Змейка", lambda: SnakeGame(master, taskbar)),
            ("💣 Сапёр", lambda: Sapper(master, taskbar)),
            ("🧩 Тетрис", lambda: Tetris(master, taskbar)),
            ("🎵 Музыкальный плеер", lambda: MusicPlayer(master, taskbar)),
            ("🤖 Ассистент (GigaChat)", lambda: GigaChatAssistant(master, taskbar)),
            ("🧠 Фуги Фуги ИИ (Sentiment)", lambda: SentimentApp(master, taskbar)),
            ("🧠 ФФGPT (чат)", lambda: FFChat(tk.Toplevel(master))),
            ("🛡️ Очистка системы", lambda: AntivirusApp(master, taskbar)),
            ("🌐 Браузер", open_browser),
            ("⚙️ Параметры", lambda: SettingsWindow(master, taskbar, lambda: change_bg(master, taskbar))),
            ("📊 Диспетчер задач", lambda: TaskManager(master, taskbar)),
            ("🎤 Голосовой помощник", lambda: start_assistant(master, master, taskbar)),
            ("🚪 Выход...", lambda: ExitDialog(master, taskbar))
        ]

        content = tk.Frame(self.window, bg=bg)
        content.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(content, bg=bg, highlightthickness=0, width=230)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(content, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        for text, cmd in apps:
            btn = tk.Button(self.inner, text=text, font=("Arial", 11),
                            bg=btn_bg, fg=fg, relief="flat", anchor="w", command=cmd)
            btn.pack(fill="x", padx=2, pady=3)

        close_btn = tk.Button(self.inner, text="Закрыть", command=self.window.destroy,
                              bg=btn_bg, fg=fg)
        close_btn.pack(side="bottom", pady=5)

        self._update_scrollregion()

    def _on_canvas_configure(self, event):
        if self.canvas.winfo_exists():
            self.canvas.itemconfig(self.canvas_window, width=max(200, event.width))
            self._update_scrollregion()

    def _on_mousewheel(self, event):
        if self.canvas.winfo_exists():
            try:
                if event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
                else:
                    steps = int(-event.delta / 120)
                    self.canvas.yview_scroll(steps, "units")
            except Exception:
                pass
            return "break"

    def _update_scrollregion(self):
        if self.canvas.winfo_exists():
            self.inner.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

# ---------- ВОССТАНОВЛЕНИЕ СЕССИИ ----------
def restore_session(master, taskbar):
    session_list = taskbar.load_session()
    for app_name in session_list:
        if app_name == "Calculator":
            Calculator(master, taskbar)
        elif app_name == "Notepad":
            Notepad(master, taskbar)
        elif app_name == "FileManager":
            FileManager(master, taskbar)
        elif app_name == "Painter":
            Painter(master, taskbar)
        elif app_name == "SnakeGame":
            SnakeGame(master, taskbar)
        elif app_name == "Sapper":
            Sapper(master, taskbar)
        elif app_name == "Tetris":
            Tetris(master, taskbar)
        elif app_name == "MusicPlayer":
            MusicPlayer(master, taskbar)
        elif app_name == "GigaChatAssistant":
            GigaChatAssistant(master, taskbar)
        elif app_name == "SettingsWindow":
            SettingsWindow(master, taskbar, lambda: change_bg(master, taskbar))
        elif app_name == "TaskManager":
            TaskManager(master, taskbar)
        elif app_name == "SentimentApp":
            SentimentApp(master, taskbar)
        elif app_name == "AntivirusApp":
            AntivirusApp(master, taskbar)
        elif app_name == "FFChat":
            FFChat(tk.Toplevel(master))
        elif app_name == "Assistant":
            start_assistant(master, master, taskbar)
        elif app_name == "BrowserApp":             # <--- ДОБАВЛЕНО
            BrowserApp(master, taskbar)
    taskbar.clear_session_file()

# ---------- РАБОЧИЙ СТОЛ ----------
def show_desktop(master):
    for w in master.winfo_children():
        w.destroy()

    workspace = tk.Frame(master)
    workspace.pack(fill="both", expand=True)

    shortcuts_frame = tk.Frame(workspace)
    shortcuts_frame.pack(anchor="nw", padx=20, pady=20)

    def make_shortcut(text, command):
        btn = tk.Button(shortcuts_frame, text=text, font=("Arial", 12),
                        command=command, bg="white", relief="raised", width=18)
        btn.pack(anchor="w", pady=2)
        return btn

    def show_start_menu():
        x = taskbar.start_btn.winfo_rootx()
        y = taskbar.start_btn.winfo_rooty()
        StartMenu(master, x, y, taskbar)

    global taskbar
    taskbar = Taskbar(master, show_start_menu)

    # Ярлыки на рабочем столе
    make_shortcut("🧮 Калькулятор", lambda: Calculator(master, taskbar))
    make_shortcut("📝 Блокнот", lambda: Notepad(master, taskbar))
    make_shortcut("📁 Файловый менеджер", lambda: FileManager(master, taskbar))
    make_shortcut("🎨 Рисовалка", lambda: Painter(master, taskbar))
    make_shortcut("🐍 Змейка", lambda: SnakeGame(master, taskbar))
    make_shortcut("💣 Сапёр", lambda: Sapper(master, taskbar))
    make_shortcut("🧩 Тетрис", lambda: Tetris(master, taskbar))
    make_shortcut("🎵 Музыкальный плеер", lambda: MusicPlayer(master, taskbar))
    make_shortcut("🤖 Ассистент (GigaChat)", lambda: GigaChatAssistant(master, taskbar))
    make_shortcut("🧠 Фуги Фуги ИИ (Sentiment)", lambda: SentimentApp(master, taskbar))
    make_shortcut("🧠 ФФGPT", lambda: FFChat(tk.Toplevel(master)))
    make_shortcut("🛡️ Очистка системы", lambda: AntivirusApp(master, taskbar))
    make_shortcut("🌐 Браузер", open_browser)
    make_shortcut("⚙️ Параметры", lambda: SettingsWindow(master, taskbar, lambda: change_bg(master, taskbar)))
    make_shortcut("🎤 Голосовой помощник", lambda: start_assistant(master, master, taskbar))

    title = tk.Label(workspace, text="Добро пожаловать в Fugi_fugi OS!",
                     font=("Arial", 24))
    title.pack(pady=50)

    change_bg(master, taskbar)
    restore_session(master, taskbar)