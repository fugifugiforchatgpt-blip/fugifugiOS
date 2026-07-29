# settings.py
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
import json
import os
from theme_utils import (
    load_settings, save_settings, get_theme, set_theme,
    get_bg_color, get_neon_theme, NEON_COLORS
)

class SettingsWindow:
    def __init__(self, parent, taskbar, on_theme_changed):
        self.parent = parent
        self.taskbar = taskbar
        self.on_theme_changed = on_theme_changed
        self.settings_file = "settings.json"
        self.session_file = "session.json"

        self.window = tk.Toplevel(parent)
        self.window.title("Параметры")
        self.window.geometry("500x500")
        self.window.configure(bg="lightgray")
        self.taskbar.add_window(self.window, "Параметры")
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()

        settings = load_settings()
        self.current_color = settings.get("bg_color", "lightblue")
        self.current_theme = settings.get("theme", "light")
        self.neon_mode = tk.BooleanVar(value=settings.get("neon_mode", False))
        self.neon_color_var = tk.StringVar(value=settings.get("neon_color", "Розовый"))

        # Предпросмотр
        self.preview = tk.Frame(self.window, bg=self.current_color, width=150, height=150)
        self.preview.pack(pady=20)
        self.preview.pack_propagate(False)
        tk.Label(self.preview, text="Текущий цвет", bg=self.current_color).pack(expand=True)

        # Кнопки выбора цвета фона
        tk.Button(self.window, text="Выбрать цвет фона", command=self.choose_color).pack(pady=5)
        tk.Button(self.window, text="Сбросить цвет (lightblue)", command=self.reset_color).pack(pady=5)

        # Переключение темы
        self.theme_btn = tk.Button(self.window, text="", command=self.toggle_theme)
        self.theme_btn.pack(pady=5)
        self.update_theme_button()

        # ---- НАСТРОЙКИ НЕОНА ----
        neon_frame = tk.LabelFrame(self.window, text="🌆 Режим НЕОН", padx=10, pady=10)
        neon_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Checkbutton(neon_frame, text="Включить неон", variable=self.neon_mode,
                       command=self.toggle_neon).pack(anchor="w")

        tk.Label(neon_frame, text="Цвет неона:").pack(anchor="w", pady=(5,0))
        self.neon_combo = ttk.Combobox(neon_frame, values=list(NEON_COLORS.keys()),
                                       textvariable=self.neon_color_var, state="readonly")
        self.neon_combo.pack(fill=tk.X, pady=5)
        self.neon_combo.bind("<<ComboboxSelected>>", self.update_neon_preview)

        # Пропуск BIOS
        bios_frame = tk.LabelFrame(self.window, text="Загрузка", padx=10, pady=10)
        bios_frame.pack(fill=tk.X, padx=10, pady=5)

        self.skip_bios_var = tk.BooleanVar(value=load_settings().get("skip_bios", False))
        tk.Checkbutton(bios_frame, text="Пропускать экран BIOS при загрузке",
                       variable=self.skip_bios_var, command=self.toggle_skip_bios).pack(anchor="w")

        # Кнопка сброса
        tk.Button(self.window, text="🗑️ Сбросить все настройки", command=self.reset_all_settings,
                  bg="#ffaaaa").pack(pady=10)

        # Кнопка закрытия
        tk.Button(self.window, text="Закрыть", command=self.on_close).pack(pady=5)

        self.apply_neon_preview()

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
                "skip_bios": False
            }
            with open(self.settings_file, "w") as f:
                json.dump(default, f)
            self.current_color = "lightblue"
            self.neon_mode.set(False)
            self.neon_color_var.set("Розовый")
            self.skip_bios_var.set(False)
            self.apply_neon_preview()
            self.on_theme_changed()
            messagebox.showinfo("Сброс", "Все настройки сброшены!")

    def on_close(self):
        self.taskbar.remove_window(self.window)
        self.window.destroy()