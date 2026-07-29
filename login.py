# login.py
import tkinter as tk
from tkinter import messagebox, ttk
from user_manager import verify_user, get_user_list

class LoginWindow:
    def __init__(self, master, on_success):
        self.master = master
        self.on_success = on_success
        self.master.attributes("-fullscreen", True)
        self.master.configure(bg="#2b2b2b")

        frame = tk.Frame(self.master, bg="#3c3c3c", padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Fugi_fugi OS", font=("Arial", 24), bg="#3c3c3c", fg="white").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(frame, text="Пользователь:", bg="#3c3c3c", fg="white").grid(row=1, column=0, sticky="e")
        self.user_combo = ttk.Combobox(frame, values=get_user_list(), state="readonly")
        self.user_combo.grid(row=1, column=1, padx=5)
        if get_user_list():
            self.user_combo.current(0)

        tk.Label(frame, text="Пароль:", bg="#3c3c3c", fg="white").grid(row=2, column=0, sticky="e")
        self.pass_entry = tk.Entry(frame, show="*")
        self.pass_entry.grid(row=2, column=1, padx=5)
        self.pass_entry.bind("<Return>", self.check)

        tk.Button(frame, text="Войти", command=self.check).grid(row=3, column=0, columnspan=2, pady=10)

    def check(self, event=None):
        user = self.user_combo.get()
        if not user:
            messagebox.showerror("Ошибка", "Выберите пользователя")
            return
        pwd = self.pass_entry.get()
        if verify_user(user, pwd):
            self.on_success(user)
        else:
            messagebox.showerror("Ошибка", "Неверный пароль")