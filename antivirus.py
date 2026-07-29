import tkinter as tk
from tkinter import messagebox
import os
import shutil

class AntivirusApp:
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar
        self.window = tk.Toplevel(parent)
        self.window.title("Очистка системы")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        self.taskbar.add_window(self.window, "Очистка системы")

        btn_frame = tk.Frame(self.window, padx=20, pady=40)
        btn_frame.pack(fill=tk.BOTH, expand=True)

        self.clean_btn = tk.Button(btn_frame, text="🗑️ Очистить временные файлы",
                                   command=self.clean_temp,
                                   font=("Arial", 14), bg="#ffaa88", width=25)
        self.clean_btn.pack(pady=20)

        self.status_label = tk.Label(self.window, text="", fg="green")
        self.status_label.pack(pady=5)

    def clean_temp(self):
        temp_dir = "temp"
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)  # создаём пустую папку заново
                self.status_label.config(text="Временные файлы удалены.", fg="green")
                messagebox.showinfo("Очистка", "Папка temp очищена.")
            except Exception as e:
                self.status_label.config(text=f"Ошибка: {e}", fg="red")
                messagebox.showerror("Ошибка", str(e))
        else:
            self.status_label.config(text="Папка temp не найдена, создаю.", fg="orange")
            os.makedirs(temp_dir)
            messagebox.showinfo("Очистка", "Папка temp создана, ничего удалять не нужно.")