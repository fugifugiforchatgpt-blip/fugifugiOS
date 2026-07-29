# task_manager.py
import tkinter as tk
from tkinter import ttk
import psutil
import threading

class TaskManager:
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar
        self.window = tk.Toplevel(parent)
        self.window.title("Диспетчер задач")
        self.window.geometry("500x400")
        self.window.minsize(400, 300)
        self.taskbar.add_window(self.window, "Диспетчер задач")
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()

        # Таблица процессов (окон)
        columns = ("Окно", "Состояние")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings", height=12)
        self.tree.heading("Окно", text="Приложение")
        self.tree.heading("Состояние", text="Статус")
        self.tree.column("Окно", width=300)
        self.tree.column("Состояние", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Кнопки
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        self.kill_btn = tk.Button(btn_frame, text="Снять задачу", command=self.kill_selected, bg="#ffaaaa")
        self.kill_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = tk.Button(btn_frame, text="Обновить", command=self.refresh_list)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # Информация о системе
        sys_frame = tk.LabelFrame(self.window, text="Система", padx=5, pady=5)
        sys_frame.pack(fill=tk.X, padx=5, pady=5)

        self.cpu_label = tk.Label(sys_frame, text="CPU: --%", anchor="w")
        self.cpu_label.pack(fill=tk.X)

        self.ram_label = tk.Label(sys_frame, text="RAM: -- / -- GB (--%)", anchor="w")
        self.ram_label.pack(fill=tk.X)

        # Первоначальное заполнение
        self.refresh_list()
        self.update_system_info()

    def refresh_list(self):
        """Обновляет список окон из taskbar.window_buttons"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for window, btn in self.taskbar.window_buttons.items():
            title = window.title()
            # Проверяем, существует ли окно
            try:
                state = "Работает"
                if not window.winfo_exists():
                    state = "Закрыто"
                self.tree.insert("", tk.END, values=(title, state), tags=(window,))
            except:
                continue

    def kill_selected(self):
        """Завершает выбранный процесс (окно)"""
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, "values")
        title = values[0]
        # Находим окно по заголовку
        for window in list(self.taskbar.window_buttons.keys()):
            if window.title() == title:
                try:
                    window.destroy()
                except:
                    pass
                break
        self.refresh_list()

    def update_system_info(self):
        """Обновляет показатели CPU и RAM (раз в секунду)"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            ram_used_gb = mem.used / (1024**3)
            ram_total_gb = mem.total / (1024**3)
            ram_percent = mem.percent
            self.cpu_label.config(text=f"CPU: {cpu_percent:.1f}%")
            self.ram_label.config(text=f"RAM: {ram_used_gb:.1f} / {ram_total_gb:.1f} GB ({ram_percent:.1f}%)")
        except Exception as e:
            self.cpu_label.config(text="CPU: недоступно")
            self.ram_label.config(text="RAM: недоступно")
        # Обновляем каждые 2 секунды
        self.window.after(2000, self.update_system_info)