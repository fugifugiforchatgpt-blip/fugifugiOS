# settings.py
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
import json
import os
from theme_utils import (
    load_settings, save_settings, get_theme, set_theme,
    get_bg_color, get_neon_theme, NEON_COLORS
)
from drivers import get_driver_manager

class SettingsWindow:
    def __init__(self, parent, taskbar, on_theme_changed):
        self.parent = parent
        self.taskbar = taskbar
        self.on_theme_changed = on_theme_changed
        self.settings_file = "settings.json"
        self.session_file = "session.json"

        self.window = tk.Toplevel(parent)
        self.window.title("Параметры")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.window.configure(bg="lightgray")
        self.taskbar.add_window(self.window, "Параметры")
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()

        # Загружаем настройки
        settings = load_settings()
        self.current_color = settings.get("bg_color", "lightblue")
        self.current_theme = settings.get("theme", "light")
        self.neon_mode = tk.BooleanVar(value=settings.get("neon_mode", False))
        self.neon_color_var = tk.StringVar(value=settings.get("neon_color", "Розовый"))

        # ---- Настройки драйверов ----
        self.driver_manager = get_driver_manager()
        self.driver_settings = settings.get("drivers", {
            "mouse": "standart",
            "keyboard": "standart"
        })
        for device, drv in self.driver_settings.items():
            self.driver_manager.set_driver(device, drv)

        # ---- СОЗДАНИЕ ДВУХ ЧАСТЕЙ: ВЕРХ (ФИКСИРОВАННЫЙ) И НИЗ (С ПРОКРУТКОЙ) ----

        # Верхний фрейм (фиксированный)
        self.top_frame = tk.Frame(self.window, bg="lightgray")
        self.top_frame.pack(side="top", fill="x", pady=5)

        # Нижний блок должен занимать оставшийся объём окна и быть связан
        # со Scrollbar'ом только через Canvas.
        self.bottom_container = tk.Frame(self.window, bg="lightgray")
        self.bottom_container.pack(side="top", fill="both", expand=True)

        self.bottom_canvas = tk.Canvas(self.bottom_container, bg="lightgray", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.bottom_container, orient="vertical", command=self.bottom_canvas.yview)
        self.bottom_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Внутренний фрейм для содержимого нижней части
        self.bottom_inner = tk.Frame(self.bottom_canvas, bg="lightgray")

        # Размещаем Canvas и Scrollbar
        self.bottom_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Создаём окно внутри Canvas
        self.canvas_window = self.bottom_canvas.create_window((0, 0), window=self.bottom_inner, anchor="nw")

        # При изменении размеров Canvas обновляем ширину внутреннего фрейма
        self.bottom_canvas.bind("<Configure>", self._on_canvas_configure)
        self.bottom_canvas.bind("<MouseWheel>", self._on_mousewheel)

        # ---- Заполняем верхнюю часть ----
        self.create_top_widgets()

        # ---- Заполняем нижнюю часть (с прокруткой) ----
        self.create_bottom_widgets()

        # Обновляем область прокрутки
        self.update_scrollregion()

    def _on_canvas_configure(self, event):
        self.bottom_canvas.itemconfig(self.canvas_window, width=event.width)
        self.update_scrollregion()

    def _on_mousewheel(self, event):
        # Прокрутка должна работать только в нижней прокручиваемой области.
        # В Tkinter wheel на Windows содержит delta; на Linux value может иметь 0,
        # но событие всё равно приходит только в целевой canvas.
        if hasattr(event, "delta") and event.delta:
            steps = int(-1 * (event.delta / 120))
        else:
            steps = -1
        self.bottom_canvas.yview_scroll(steps, "units")
        return "break"

    def update_scrollregion(self):
        self.bottom_canvas.update_idletasks()
        self.bottom_canvas.configure(scrollregion=self.bottom_canvas.bbox("all"))

    # ---- Верхняя часть (фиксированная) ----

    def create_top_widgets(self):
        # Предпросмотр
        self.preview = tk.Frame(self.top_frame, bg=self.current_color, width=150, height=150)
        self.preview.pack(pady=10)
        self.preview.pack_propagate(False)
        tk.Label(self.preview, text="Текущий цвет", bg=self.current_color).pack(expand=True)

        # Кнопки выбора цвета фона
        tk.Button(self.top_frame, text="Выбрать цвет фона", command=self.choose_color).pack(pady=2)
        tk.Button(self.top_frame, text="Сбросить цвет (lightblue)", command=self.reset_color).pack(pady=2)

        # Переключение темы
        self.theme_btn = tk.Button(self.top_frame, text="", command=self.toggle_theme)
        self.theme_btn.pack(pady=2)
        self.update_theme_button()

        # ---- НАСТРОЙКИ НЕОНА ----
        neon_frame = tk.LabelFrame(self.top_frame, text="🌆 Режим НЕОН", padx=10, pady=5)
        neon_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Checkbutton(neon_frame, text="Включить неон", variable=self.neon_mode,
                       command=self.toggle_neon).pack(anchor="w")

        tk.Label(neon_frame, text="Цвет неона:").pack(anchor="w", pady=(2,0))
        self.neon_combo = ttk.Combobox(neon_frame, values=list(NEON_COLORS.keys()),
                                       textvariable=self.neon_color_var, state="readonly")
        self.neon_combo.pack(fill=tk.X, pady=2)
        self.neon_combo.bind("<<ComboboxSelected>>", self.update_neon_preview)

    # ---- Нижняя часть (с прокруткой) ----

    def create_bottom_widgets(self):
        # ---- НАСТРОЙКИ ДРАЙВЕРОВ (только мышь и клавиатура) ----
        driver_frame = tk.LabelFrame(self.bottom_inner, text="🖱️ Драйверы устройств", padx=10, pady=10)
        driver_frame.pack(fill=tk.X, padx=10, pady=5)

        mouse_drivers = self.driver_manager.get_drivers_list("mouse")
        keyboard_drivers = self.driver_manager.get_drivers_list("keyboard")

        # Мышь
        tk.Label(driver_frame, text="Мышь:").grid(row=0, column=0, sticky="w", pady=3)
        self.mouse_var = tk.StringVar(value=self.driver_settings.get("mouse", "standart"))
        self.mouse_combo = ttk.Combobox(driver_frame, values=mouse_drivers,
                                        textvariable=self.mouse_var, state="readonly")
        self.mouse_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        self.mouse_combo.bind("<<ComboboxSelected>>", lambda e: self.on_driver_change("mouse"))

        # Клавиатура
        tk.Label(driver_frame, text="Клавиатура:").grid(row=1, column=0, sticky="w", pady=3)
        self.keyboard_var = tk.StringVar(value=self.driver_settings.get("keyboard", "standart"))
        self.keyboard_combo = ttk.Combobox(driver_frame, values=keyboard_drivers,
                                           textvariable=self.keyboard_var, state="readonly")
        self.keyboard_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        self.keyboard_combo.bind("<<ComboboxSelected>>", lambda e: self.on_driver_change("keyboard"))

        driver_frame.columnconfigure(1, weight=1)

        # ---- НАСТРОЙКИ BIOS ----
        bios_frame = tk.LabelFrame(self.bottom_inner, text="Загрузка", padx=10, pady=10)
        bios_frame.pack(fill=tk.X, padx=10, pady=5)

        self.skip_bios_var = tk.BooleanVar(value=load_settings().get("skip_bios", False))
        tk.Checkbutton(bios_frame, text="Пропускать экран BIOS при загрузке",
                       variable=self.skip_bios_var, command=self.toggle_skip_bios).pack(anchor="w")

        # Кнопка сброса
        tk.Button(self.bottom_inner, text="🗑️ Сбросить все настройки", command=self.reset_all_settings,
                  bg="#ffaaaa").pack(pady=10)

        # Кнопка закрытия
        tk.Button(self.bottom_inner, text="Закрыть", command=self.on_close).pack(pady=5)

        # Обновляем область прокрутки после добавления всех виджетов
        self.update_scrollregion()

    def on_driver_change(self, device_type):
        new_driver = {
            "mouse": self.mouse_var.get(),
            "keyboard": self.keyboard_var.get()
        }[device_type]
        self.driver_manager.set_driver(device_type, new_driver)
        self.driver_settings[device_type] = new_driver
        self._save_driver_settings()

    def _save_driver_settings(self):
        data = load_settings()
        data["drivers"] = self.driver_settings
        save_settings(data)

    def _load_driver_settings(self):
        data = load_settings()
        drivers = data.get("drivers", {})
        for dev in ["mouse", "keyboard"]:
            if dev in drivers:
                self.driver_settings[dev] = drivers[dev]
                self.driver_manager.set_driver(dev, drivers[dev])

    # ================ ОСТАЛЬНЫЕ МЕТОДЫ (без изменений) ================

    def update_theme_button(self):
        theme = get_theme()
        self.theme_btn.config(text="Включить тёмную тему" if theme == "light" else "Включить светлую тему")

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет", parent=self.window)
        if color_code and color_code[1]:
            self.current_color = color_code[1]
            self.preview.configure(bg=self.current_color)
            for child in self.preview.winfo_children():
                child.configure(bg=self.current_color)
            data = load_settings()
            data["bg_color"] = self.current_color
            save_settings(data)
            self.on_theme_changed()

    def reset_color(self):
        self.current_color = "lightblue"
        self.preview.configure(bg="lightblue")
        for child in self.preview.winfo_children():
            child.configure(bg="lightblue")
        data = load_settings()
        data["bg_color"] = "lightblue"
        save_settings(data)
        self.on_theme_changed()
        messagebox.showinfo("Сброс", "Цвет восстановлен")

    def toggle_theme(self):
        new_theme = "dark" if get_theme() == "light" else "light"
        set_theme(new_theme)
        self.update_theme_button()
        self.on_theme_changed()

    def toggle_neon(self):
        data = load_settings()
        data["neon_mode"] = self.neon_mode.get()
        save_settings(data)
        self.apply_neon_preview()
        self.on_theme_changed()

    def toggle_skip_bios(self):
        data = load_settings()
        data["skip_bios"] = self.skip_bios_var.get()
        save_settings(data)

    def update_neon_preview(self, event=None):
        data = load_settings()
        data["neon_color"] = self.neon_color_var.get()
        save_settings(data)
        self.apply_neon_preview()
        self.on_theme_changed()

    def apply_neon_preview(self):
        if self.neon_mode.get():
            color_name = self.neon_color_var.get()
            neon = get_neon_theme(color_name)
            self.preview.configure(bg=neon["bg"])
            for child in self.preview.winfo_children():
                child.configure(bg=neon["bg"], fg=neon["fg"])
        else:
            self.preview.configure(bg=self.current_color)
            for child in self.preview.winfo_children():
                child.configure(bg=self.current_color, fg="black")

    def reset_all_settings(self):
        if messagebox.askyesno("Сброс настроек", "Удалить все настройки и сессии?"):
            for f in [self.settings_file, self.session_file]:
                if os.path.exists(f):
                    os.remove(f)
            default = {
                "bg_color": "lightblue",
                "theme": "light",
                "neon_mode": False,
                "neon_color": "Розовый",
                "skip_bios": False,
                "drivers": {
                    "mouse": "standart",
                    "keyboard": "standart"
                }
            }
            with open(self.settings_file, "w") as f:
                json.dump(default, f)
            self.current_color = "lightblue"
            self.neon_mode.set(False)
            self.neon_color_var.set("Розовый")
            self.skip_bios_var.set(False)
            self.driver_settings = default["drivers"]
            for dev, drv in self.driver_settings.items():
                self.driver_manager.set_driver(dev, drv)
            self.mouse_var.set("standart")
            self.keyboard_var.set("standart")
            self.apply_neon_preview()
            self.on_theme_changed()
            messagebox.showinfo("Сброс", "Все настройки сброшены!")

    def on_close(self):
        self.taskbar.remove_window(self.window)
        self.window.destroy()